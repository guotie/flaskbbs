#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

import urllib
from copy import deepcopy
from markdown2 import Markdown

from flask import g, request, redirect, session
from flask import render_template
from flask import request, url_for, jsonify, current_app

from models import Section, Node, Topic, Reply
from forms import TopicForm, NodeForm, ReplyForm

from datetime import datetime

from flaskcommon.extensions import db, cache

from flask import Blueprint
bp_bbs = Blueprint('bp_bbs', __name__, template_folder='templates', static_folder='static')

from flask.ext.login import current_user, login_required

from flaskcommon.utils import generate_url, get_page_query

DEFAULT_PAGE_SIZE = 50
DEFAULT_PAGE_REPLIES = 50

def user_is_not_anonymous():
    return current_user.is_authenticated()

@cache.cached(timeout=60, unless=user_is_not_anonymous)
@bp_bbs.route('/')
def bbs_index():
    options = {}
    page = request.args.get('page', 0, type=int)

    sort = request.args.get('sort', 0, type=int)
    if sort:
        options["sort"]=sort
    else:
        options["sort"] = 0

    query = Topic.query.all_topics(sort)
    count, num_pages, topics = get_page_query(query, page, page_size=DEFAULT_PAGE_SIZE)

    def pager_url(p, options):
        return generate_url('.bbs_index', page=p, **options)

    def filter_url(orig_options, **args):
        options = deepcopy(orig_options)
        for k,v in args.items():
            options[k] = v
        return generate_url(".bbs_index", **options)

    sections = Section.query.get_all_sections()
    return render_template("node_index.html",
                                topics=topics,
                                options=options,
                                count=count,
                                pager_url=pager_url,
                                filter_url=filter_url,
                                num_pages=num_pages,
                                page=page,
                                sections=sections,
                                node=None
                            )

@bp_bbs.route('/topic/<id>', methods=['GET', 'POST'])
def bbs_topic(id):
    options = {"id": id}
    page = request.args.get('page', 0, type=int)
    topic = Topic.query.get(id)
    if not topic:
        return render_template("topic_not_found.html")

    count, num_pages, replies = get_page_query(Reply.query.replies_at_topic(topic.id), page, page_size=DEFAULT_PAGE_REPLIES)
    def pager_url(p, options):
        return generate_url(".bbs_topic", page=p, **options)

    if current_user.is_anonymous():
        form = None
    else:
        form = ReplyForm(request.form)

    if request.method == "POST":
        if current_user.is_anonymous():
            return redirect(url_for("auth.login", next=request.path) or "/")
        if form.validate():
            reply = Reply(section=topic.section, node=topic.node, user=current_user, topic=topic,
                content=form.data["content"], created=datetime.now(), floor=topic.reply_count+1)
            topic.last_reply_by = current_user.username
            topic.last_reply_at = datetime.now()
            topic.reply_count += 1
            current_user.profile.replies += 1
            node = topic.node
            node.reply_count += 1
            section = topic.section
            section.reply_count += 1
            db.session.add_all([reply, topic, current_user.profile, node, section])
            db.session.commit()

            return redirect(pager_url((reply.floor-1)/DEFAULT_PAGE_REPLIES, options))

        return render_template("topic.html", topic=topic, options=options, count=count, pager_url=pager_url,
                                num_pages=num_pages, page=page, replies=replies, form=form)

    topic.hits += 1
    db.session.commit()

    markdowner = Markdown()
    topic.content = markdowner.convert(topic.content)
    for r in replies:
        r.content = markdowner.convert(r.content)

    return render_template("topic.html", topic=topic,
                                            options=options,
                                            count=count,
                                            pager_url=pager_url,
                                            num_pages=num_pages,
                                            page=page,
                                            replies=replies,
                                            form=form
                            )

@bp_bbs.route('/sections')
def bbs_sections():
    return render_template("sections.html")

@cache.cached(timeout=90, unless=user_is_not_anonymous)
@bp_bbs.route('/section/<section_name>')
def bbs_section(section_name):
    return render_template("section.html")

@cache.cached(timeout=90, unless=user_is_not_anonymous)
@bp_bbs.route('/node/<node_name>')
def bbs_node(node_name):
    name = urllib.unquote(node_name).strip()
    node = Node.query.filter(Node.name==name).first()
    if not node:
        return render_template("node_not_found.html", name=name)

    options = {"node_name": node_name}
    page = request.args.get('page', 0, type=int)

    sort = request.args.get('sort', 0, type=int)
    if sort:
        options["sort"]=sort
    else:
        options["sort"] = 0

    query = Topic.query.filter(Topic.node==node).all_topics(sort)
    count, num_pages, topics = get_page_query(query, page, page_size=DEFAULT_PAGE_SIZE)

    def pager_url(p, options):
        return generate_url('.bbs_node', page=p, **options)

    def filter_url(orig_options, **args):
        options = deepcopy(orig_options)
        for k,v in args.items():
            options[k] = v
        return generate_url(".bbs_node", **options)

    sections = Section.query.all()
    return render_template("node_index.html",
        topics=topics,
        options=options,
        count=count,
        pager_url=pager_url,
        filter_url=filter_url,
        num_pages=num_pages,
        page=page,
        sections=sections,
        node=node
    )

@bp_bbs.route("/add/topic", methods=['GET', 'POST'])
@login_required
def bbs_add_topic():
    node_str = urllib.unquote(request.args.get('node', "").strip())
    node = None
    if node_str:
        node = Node.query.filter(Node.name==node_str).first()
        if not node:
            return render_template("node_not_found.html", next=url_for('.bbs_add_topic'), name=node_str)

    form = TopicForm(request.form)
    form.node.choices = Section.query.get_all_nodes()
    if node_str:
        form.node.data=node.title
    if request.method == 'POST' and form.validate():
        if not node:
            node = Node.query.filter(Node.title==form.data["node"].strip()).first()
            if not node:
                form.node.errors.append(u"节点不存在！")
                return render_template("add_topic.html", form=form)
        section = node.section
        topic = Topic(user=current_user, title=form.data['title'].strip(), content=form.data["content"],
                    tags=form.data["tags"], created=datetime.now(), last_modified=datetime.now(),
                    last_reply_at=datetime.now())
        topic.section = section
        topic.node = node

        #db.session.add(topic)
        node.topic_count += 1
        #db.session.add(node)
        section.topic_count += 1
        #db.session.add(section)
        current_user.profile.topics += 1
        db.session.add_all([topic, node, section, current_user.profile])
        db.session.commit()
        return redirect(url_for(".bbs_topic", id=topic.id))
    if node_str:
        action_url = url_for(".bbs_add_topic", node=node_str)
    else:
        action_url = url_for(".bbs_add_topic")
    return render_template("add_topic.html", form=form, action_url=action_url)

@bp_bbs.route("/add/node", methods=['GET', 'POST'])
@login_required
def bbs_add_node():
    form = NodeForm(request.form)
    form.section.query_factory = Section.query.all

    if request.method == 'POST' and form.validate():
        section = form.data["section"]
        print section, type(section)
        if not section:
            form.section.errors.append(u"Section不存在！")
            return render_template("add_node.html", form=form)

        node = Node(section=section, name=form.data["node_name"].strip(), title=form.data["node_title"],
                    descp=form.data["descp"], item_per_page=form.data["item_per_page"], header=form.data["header"],
                    footer=form.data["footer"], sidebar=form.data["sidebar"], sidebar_ads=form.data["sidebar_ads"],
                    avatar_url=form.data["avatar_url"]
                )
        node.created = datetime.now()

        section.node_count += 1
        db.session.add_all([node, section])
        db.session.commit()
        return redirect(url_for(".bbs_node", node_name=urllib.quote(node.name)))

    return render_template("add_node.html", form=form)

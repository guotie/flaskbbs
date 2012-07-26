#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'guotie'

import time, datetime

from flask.ext.sqlalchemy import BaseQuery

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import func

from flaskcommon.extensions import db, cache
from flaskcommon.auth.models import User
from flaskcommon.utils import timesince

class SectionQuery(BaseQuery):
    @cache.cached(timeout=1800, key_prefix="all_nodes")
    def get_all_nodes(self):
        sections = Section.query.all()
        result = []
        for section in sections:
            nodes = section.nodes
            sub_res = tuple((node.title, node) for node in nodes)
            result.append((section.title, sub_res))

        return result

    def get_all_sections(self):
        return Section.query.order_by(Section.sort_order.desc()).all()

class Section(db.Model):
    '''
    name is used by url, must be a-zA-Z0-9-
    title is utf-8 characters
    '''
    __tablename__ = "section"

    query_class = SectionQuery

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    descp = db.Column(db.Text, nullable=True)
    avatar = db.Column(db.String(200), nullable=True)
    title_alternative = db.Column(db.String(200), nullable=True)
    header = db.Column(db.Text, nullable=True)
    footer = db.Column(db.Text, nullable=True)
    node_count = db.Column(db.Integer, default=0)
    topic_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    #created = db.Column(db.DateTime, nullable=True, default=func.now())
    #last_modified = db.Column(db.DateTime, nullable=True, onupdate=datetime.datetime.now)
    created = db.Column(db.DateTime, nullable=True)
    last_modified = db.Column(db.DateTime, nullable=True)
    sort_order = db.Column(db.Integer, default=1)

    def __unicode__(self):
        return self.title

class NodeQuery(BaseQuery):
    pass

class Node(db.Model):
    '''node_type: 0  public plaza
                  1  public club, anybody can join without permission except people who is in blacklist
                  2  private club, one can join with permission or invitation
                  3 secret club, anybody cannot see secret club except members
    '''
    __tablename__ = "node"

    query_class = NodeQuery

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, ForeignKey('section.id'), nullable=False)
    section = relationship("Section", backref="nodes")

    members = db.Column(db.Integer, default=0)
    follows = db.Column(db.Integer, default=0)
    node_type = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)

    name = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(60), nullable=False, index=True)
    descp = db.Column(db.Text, nullable=False, default="")

    header = db.Column(db.Text, nullable=True)
    footer = db.Column(db.Text, nullable=True)
    theme = db.Column(db.String(40), nullable=False, default="default")
    sidebar = db.Column(db.Text, nullable=True)
    sidebar_ads = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(40), nullable=True, index=True)

    topic_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    parent_node = db.Column(db.Integer, nullable=True)
    avatar_url = db.Column(db.String(100), nullable=True)

    keywords = db.Column(db.Text, default="")
    item_per_page = db.Column(db.Integer, default=50)

    created = db.Column(db.DateTime, nullable=True)#, default=func.now())
    last_modified = db.Column(db.DateTime, nullable=True)#, onupdate=datetime.datetime.now)

    def __unicode__(self):
        return self.title

class TopicQuery(BaseQuery):
    def all_topics(self, sort):
        if sort == 0:
            return self.order_by(Topic.last_reply_at.desc()).order_by(Topic.created.desc())
        elif sort == 1:
            return self.order_by(Topic.impact.desc()).order_by(Topic.last_reply_at.desc()).order_by(Topic.created.desc())
        elif sort == 2:
            return self.order_by(Topic.created.desc())
        elif sort == 3:
            return self.filter(Topic.reply_count==0).order_by(Topic.created.desc())
        return self.order_by(Topic.last_reply_at.desc()).order_by(Topic.created.desc())

    def impact_topics(self):
        return self.order_by(Topic.impact.desc())

def get_current_impact():
    return int(time.time())

class Topic(db.Model):
    '''
    status: 0: normal
            1: promotion
            2: close
    '''
    __tablename__ = "topic"

    query_class = TopicQuery

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, ForeignKey('section.id'), nullable=False, index=True)
    section = relationship("Section", backref="topics")
    node_id = db.Column(db.Integer, ForeignKey('node.id'), nullable=False, index=True)
    node = relationship("Node", backref="topics")

    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False, index=True)
    user = relationship("User", backref="topics")

    marks = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=0)

    title = db.Column(db.String(100), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    content_length = db.Column(db.Integer, nullable=True, default=0)
    created = db.Column(db.DateTime, nullable=True)#, default=func.now())
    last_modified = db.Column(db.DateTime, nullable=True)

    hits = db.Column(db.Integer, default=1)
    reply_count = db.Column(db.Integer, default=0)
    reply_members = db.Column(db.Integer, default=0)
    last_reply_by = db.Column(db.String(100), nullable=False, default="", index=True)
    last_reply_at = db.Column(db.DateTime, nullable=True)#, onupdate=datetime.datetime.now)

    up_count = db.Column(db.Integer, default=0)
    down_count = db.Column(db.Integer, default=0)

    tags = db.Column(db.String(100), nullable=False, index=True)

    impact = db.Column(db.Integer, default=get_current_impact, index=True)
    theme = db.Column(db.String(40), nullable=False, default="default")

    def __unicode__(self):
        '''
        admin need this
        '''
        return self.title

    @property
    def hr_created_tm(self):
        return timesince(self.created)

    @property
    def hr_last_reply(self):
        return timesince(self.last_reply_at)

class ReplyQuery(BaseQuery):
    def replies_at_topic(self, topic_id):
        return Reply.query.filter(Reply.topic_id==topic_id).order_by(Reply.created)

class Reply(db.Model):

    __tablename__ = "reply"

    query_class = ReplyQuery

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, ForeignKey('section.id'), nullable=False, index=True)
    section = relationship("Section", backref="replies")
    node_id = db.Column(db.Integer, ForeignKey('node.id'), nullable=False, index=True)
    node = relationship("Node", backref="replies")

    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False, index=True)
    user = relationship("User", backref="replies")
    topic_id = db.Column(db.Integer, ForeignKey("topic.id"), nullable=False, index=True)
    topic = relationship("Topic", backref="replies")

    parent_reply_id = db.Column(db.Integer, default=0)

    floor = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    support = db.Column(db.Integer, default=0)
    against = db.Column(db.Integer, default=0)

    def __unicode__(self):
        return self.content

    @property
    def hr_created_tm(self):
        return timesince(self.created)

def create_section(name, title, avatar=None, commit=False, **kwargs):
    section = Section(name=name, title=title, node_count=0, topic_count=0, reply_count=0,
        created=datetime.datetime.now(), last_modified=datetime.datetime.now(), **kwargs)
    if avatar:
        section.avatar = avatar
    db.session.add(section)
    if commit:
        db.session.commit()

    return section

def create_node(section, name, title, avatar=None, commit=False, **kwargs):
    node = Node(section=section, name=name, title=title, topic_count=0, reply_count=0,
        created=datetime.datetime.now(), last_modified=datetime.datetime.now(), **kwargs)
    section.node_count += 1
    if avatar:
        node.avatar_url = avatar

    db.session.add(node)
    if commit:
        db.session.commit()

    return node

def init_data(app):
    print "create secion & nodes ....\n"
    section = create_section(name="flask-bbs", title=u"flask-bbs", descp=u"flask-bbs讨论区")
    create_node(section=section, name="fb-dev", title=u"flask-bbs开发", descp=u"flask-bbs开发、roadmap")
    create_node(section=section, name="fb-bug", title=u"flask-bbs bug反馈", descp=u"flask-bbs bug反馈")
    create_node(section=section, name="suggest", title=u"功能建议", descp=u"flask-bbs功能建议")

    db.session.commit()

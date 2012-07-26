#!/usr/bin/python
# -*- coding: utf-8 -*-
#
__author__ = 'guotie'

import time
import urllib

from flask import current_app, request, redirect, session, flash, url_for
from flask import render_template

from sqlalchemy.orm.exc import DetachedInstanceError

from flask import Flask, Blueprint
blueprint_auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')
# app = Flask(__name__)

from weibo import APIClient
from models import Anonymous, User, UserProfile, create_user
from forms import UserRegForm, LoginForm, SettingsForm, ChangePasswordForm, settings_from_user, FindPasswordForm, AvaterForm

from flaskcommon.extensions import db, cache

from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin,
                            confirm_login, fresh_login_required)

login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "auth.login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

def login_manager_init(app):
    login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    if not id:
        return None
    user = cache.get(str(id))
    if user:
        user = db.session.merge(user)
    return user

#@login_manager.token_loader
#def load_token(token):
#    id = mcache_get(str(token))
#    return User.query.get(id)

#@login_manager.unauthorized_handler
#def handle_unauthorized():
#    return render_template("unauthorized.html")

###################################################################
#   sina weibo
###################################################################
@blueprint_auth.route('/login/weibo')
def login_weibo():
    client = APIClient(app_key=current_app.config["APP_KEY"],
                        app_secret=current_app.config["APP_SECRET"],
                        redirect_uri=request.host_url+url_for(".weibo_callback"))
    url = client.get_authorize_url()

    return redirect(url)

def get_or_create_weibo_user(client, code):
    res = client.request_access_token(code)

    # print "token:", str(res.access_token), "expires: ", res.expires_in
    token = res.access_token
    expires_in = res.expires_in
    client.set_access_token(token, expires_in)

    # first, try to get user from the mcache
    user = cache.get(str(token))
    if user:
        print "get_or_create_weibo_user, from cache: %s %d"  %(str(user), user.id)
        #try:
        #    mcache_set(str(user.id), user)
        #    return user
        #except DetachedInstanceError:
        #    print "merge user ...."
        #    user = db.session.merge(user)
        #    mcache_set(str(user.id), user)
        #    return user
        user = db.session.merge(user)
        print "get_or_create_weibo_user, cache db merge: %s %d"  %(str(user), user.id)
        return user

    auth_id = "weibo_" + str(res.uid)
    user = User.query.get_by_authid(auth_id)
    if not user:
        weibo_user = client.get.users__show(uid=res.uid)
        print "get_or_create_weibo_user", weibo_user

        kw = dict()
        kw['auth_id'] = auth_id
        kw['nickname'] = kw['username'] = weibo_user.screen_name
        kw['avater'] = weibo_user.profile_image_url
        kw['gender'] = weibo_user.gender

        kw2 = dict()
        kw2['province'] = weibo_user.province
        kw2['city'] = weibo_user.city
        kw2['copper_coins'] = 5000

        #print kw, kw2
        user = User(**kw)
        profile = UserProfile(**kw2)
        user.profile = profile
        db.session.add_all([user, profile])

        db.session.commit()

    # save user in mcache
    #mcache_set(str(token), user, expires_in=expires_in-int(time.time()))
    #mcache_set(str(user.id), user)
    cache.set(str(token), user, expires_in=expires_in-int(time.time()))
    cache.set(str(user.id), user)
    print "get_or_create_weibo_user, from db: %s %d. set token: %s"  %(str(user), user.id, str(token))

    return user

@blueprint_auth.route('/login/weibo_callback')
def weibo_callback():
    code = request.args.get('code')
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=SINA_CALLBACK_URL)

    user = get_or_create_weibo_user(client, code)

    if not user:
        return render_template("login_weibo_failed.html")

    print "weibo_callback: user = %s %s" %(str(user), type(user))
    if login_user(user, remember=True):
        print "%s Logged in!" %user.username
        #flash("Logged in!")
        return redirect(request.args.get("next") or "/")
    else:
        return redirect(session.get('login_ok_url', '/'))

@blueprint_auth.route("/logout")
@login_required
def logout():
    logout_user()
    #flash("Logged out.")
    return redirect("/")

###################################################################################################
#   local register & login
###################################################################################################

@blueprint_auth.route("/register", methods=['GET', 'POST'])
def register():
    form = UserRegForm(request.form)
    if request.method == 'POST' and form.validate():
        user = create_user("local_%s" %form.data['name'],
            form.data["name"],
            form.data['email'],
            copper_coins=5000,
            password=form.data['password'])
        cache.set(str(user.id), user)
        if login_user(user, remember=True):
            return redirect(request.args.get("next") or "/")
    #print form.data["name"], type(form.data["name"])
    return render_template("reg.html", form=form)

@blueprint_auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    next = request.args.get("next")
    if request.method == 'POST' and form.validate():
        username = form.data["email"]
        password = form.data["password"]

        if '@' in username:
            user = User.query.filter(User.email==username).first()
        else:
            user = User.query.filter(User.username==username).first()
        if not user:
            form.email.errors.append(u'用户名或email未注册或密码不正确')
            return render_template("login.html", form=form, next=next)
        if not user.check_password(password):
            form.email.errors.append(u'用户名或email未注册或密码不正确')
            return render_template("login.html", form=form, next=next)
        cache.set(str(user.id), user)
        if not login_user(user, remember=True):
            form.email.errors.append(u'login failed!')
            return render_template("login.html", form=form, next=next)
        return redirect(request.args.get("next") or "/")
    return render_template("login.html", form=form, next=next)

@blueprint_auth.route("/member/<username>")
def member(username):
    name = urllib.unquote(username)
    member = User.query.filter(User.username==name).first()
    if member:
        return render_template("member.html", member=member)
    else:
        return render_template("no_member.html", username=name)

@blueprint_auth.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(request.form)
    if request.method == 'POST':
        form = SettingsForm(request.form)
        if form.validate():
            uchanged = False
            pchanged = False
            user = current_user
            profile = user.profile
            if user.username != form.username.data:
                user.username = form.username.data
                if user.modify_chance <= 0:
                    form.username.errors.append(u'您修改用户名的机会已经用完，无法再修改用户名！')
                    return render_template("settings.html", form=form)
                if User.query.filter(User.username==form.username.data).first():
                    form.username.errors.append(u'该用户名已被使用！')
                    return render_template("settings.html", form=form)
                uchanged =True
                user.modify_chance -= 1
                if user.modify_chance <= 0:
                    user.modify_chance = 0
                    form.username.extra_class = "disable"
            #if user.nickname != form.nickname.data:
            #    user.nickname = form.nickname.data
            #    uchanged =True

            if profile.city != form.city.data or\
                profile.province != form.province.data or\
                profile.birthday != form.birthday.data or\
                profile.blog != form.blog.data or\
                profile.descp != form.descp.data or\
                profile.signature != form.signature.data or \
                profile.realname != form.realname.data or\
                profile.idcard != form.idcard.data:
                profile.city = form.city.data
                profile.province = form.province.data
                profile.birthday = form.birthday.data
                profile.blog = form.blog.data
                profile.descp = form.descp.data
                profile.signature = form.signature.data
                profile.realname = form.realname.data
                profile.idcard = form.idcard.data
                pchanged = True

            if uchanged:
                db.session.add(user)
            if pchanged:
                db.session.add(profile)

            if uchanged or pchanged:
                db.session.commit()
                if uchanged:
                    mcache_set(str(user.id), user)
                    login_user(user, remember=True)
                    #return redirect("/")
                else:
                    flash(u"个人资料设置成功！")
        return render_template("settings.html", form=form)

    form = settings_from_user(current_user)
    return render_template("settings.html", form=form)

@blueprint_auth.route("/findpassword", methods=['GET', 'POST'])
def findpassword():
    form = FindPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter().first()
        if user:
            return render_template("findpassword_ok.html")
        form.password.errors.append(u'Email不正确或未注册！')
    return render_template("findpassword.html", form=form)


@blueprint_auth.route("/changepassword", methods=['GET', 'POST'])
@login_required
def changepassword():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        if not current_user.check_password(form.old_password.data):
            form.old_password.errors.append(u'密码错误！')
            return  render_template("changepassword.html", form=form)

        current_user.password = User.create_password(form.new_password.data)
        db.session.add(current_user)
        db.session.commit()
        flash(u"密码修改成功！")
        return  render_template("changepassword.html", form=ChangePasswordForm())

    return render_template("changepassword.html", form=form)

@blueprint_auth.route("/avater", methods=['GET', 'POST'])
@login_required
def avater():
    form = AvaterForm(request.form)
    if request.method =='POST' and form.validate():
        return render_template('avater.html', form=form)

    return render_template('avater.html', form=form)

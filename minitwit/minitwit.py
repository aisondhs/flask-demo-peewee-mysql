# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import time
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug import check_password_hash, generate_password_hash
from models import *


# configuration
PER_PAGE = 30
DEBUG = True
SECRET_KEY = '&Us\xb9\xa0\xef\xc9\xe8H\xfc\x10\xe2\xfd9\xffR\x8c\xa2\xb65\x18\xd9\xf7?'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

def get_user_id(username):
    """Convenience method to look up the id for a username."""
    try:
        user = User.select().where(User.username == username).get();
        return user.id
    except User.DoesNotExist:
        user = None
    return None

def get_user(username):
    try:
        user = User.select().where(User.username == username).get();
    except User.DoesNotExist:
        user = None
    return user

def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = User.select().where(User.id == session['user_id']).get()
        g.user = user

@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    else:
        whomids = [follow.whom for follow in Follower.select().where(Follower.who == session['user_id'])]
        if whomids :
            messages = Message.select().join(User).where(User.id == session['user_id'] | User.id << whomids ).limit(PER_PAGE) 
        else:
            messages = Message.select().join(User).where(User.id == session['user_id']).limit(PER_PAGE)
    return render_template('timeline.html', messages = messages)


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    messages = Message.select().join(User).limit(PER_PAGE)
    return render_template('timeline.html', messages = messages)


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = get_user(username)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        try:
            followed = Follower.select().where((Follower.who == session['user_id']) & (Follower.whom == profile_user.id)).get()
        except Follower.DoesNotExist:
            followed = None
    messages =  Message.select().join(User).where(User.id == profile_user.id).limit(PER_PAGE)
    return render_template('timeline.html', messages = messages, followed=followed,profile_user=profile_user)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    new_follower = Follower(who = session['user_id'],whom = whom_id)
    new_follower.save()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    follower = Follower.select().where((Follower.who == session['user_id']) & (Follower.whom == whom_id)).get()
    follower.delete_instance()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        msg = Message(author = session['user_id'],text = request.form['text'],pub_date = int(time.time()))
        msg.save()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = get_user(request.form['username'])
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user.pw_hash,
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user.id
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            new_user = User(username = request.form['username'],email = request.form['email'],pw_hash = generate_password_hash(request.form['password']))
            new_user.save()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url


if __name__ == '__main__':
    app.run()

from flask import Flask, send_from_directory, render_template, request, redirect, url_for, session, flash
from models import Post, User
from db import db_session
import time
import random

import os
import logging
import base64

env = os.environ

app = Flask(__name__)

app.secret_key = '7a6f2bde-2a5f-45ca-9783-fc84e0caa0e2'

@app.errorhandler(500)
@app.errorhandler(404)
def error(e):
    images = [
            "https://media.giphy.com/media/Kady4vI8gBa24/giphy.gif",
            "https://media.giphy.com/media/dcubXtnbck0RG/giphy.gif",
            "https://media.giphy.com/media/kc8PUzwL0rSqk/giphy.gif",
            "https://media.giphy.com/media/PKkqsNWPGiJ2w/giphy.gif",
            "https://media.giphy.com/media/10oMLv2r64Bhja/giphy.gif",
            "https://media.giphy.com/media/ZGW88HgXu3eww/giphy.gif",
            "https://media.giphy.com/media/F5vPRXczEP9bG/giphy.gif",
            "https://media.giphy.com/media/QNFGUaJ7OGU80/giphy.gif"
            ]
    image = random.choice(images)
    error_number = random.randint(10000, 20000)
    return render_template('error.html', error_number=error_number, image=image)

@app.route("/")
def home():
    posts = Post.visible()
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    user_count = User.query.count()
    post_count = Post.query.count()
    flagged_count = Post.query.filter_by(flagged=True).count()

    return render_template('about.html', user_count=user_count,
            post_count=post_count, flagged_count=flagged_count)

@app.route("/new", methods=['POST'])
def new_post():
    if not session['logged_in']:
        flash('You need to login/signup before flagging.')
        return redirect(url_for('signup'))

    post_content = request.form.get('content', False)

    if not post_content:
        flash('Post content empty.')
        return redirect(url_for('home'))

    Post(post_content, session['logged_user_id'])
    flash('New post created, it should appear down below, otherwise refresh.')
    return redirect(url_for('home'))

@app.route("/flag", methods=['POST'])
def flag_post():
    if not session['logged_in']:
        flash('You need to login/signup before posting.')
        return redirect(url_for('signup'))

    post_id = request.form.get('id', False)

    if not post_id:
        flash('Error while flagging, please try again.')
        return redirect(url_for('home'))

    try:
        post_id = int(post_id)
    except Exception:
        flash('Error while flagging, please try again.')
        return redirect(url_for('home'))

    db = db_session()
    post = db.query(Post).get(post_id)

    if not post:
        flash('Error while flagging, please try again.')
        return redirect(url_for('home'))

    if post.author == session['logged_user_id']:
        flash('You can\'t flag your own posts.')
        return redirect(url_for('home'))

    post.flagged = True
    db.commit()

    flash('Thanks for flagging that post, an admin will have a look at it shortly.')
    return redirect(url_for('home'))

def valid_admin_key(admin_key):
    # Decode the key
    key = base64.b64decode(admin_key)

    # Split into a char array
    key = [x for x in key.decode("utf-8")]

    # Get the passed timestamps
    key_timestamp = int("".join(key[1:4]))
    # Generate the current timestamps plus a second
    current_timestamp = int(time.time() + 1) % 1000

    # Keep only every 4th char
    key = "".join(key[::4])

    # Break here if the key is not good
    if key != env.get('ADMIN_KEY'):
        return False

    # Now the timestamps verification, the key_timestamp needs to be smaller
    # than the current one, but not by more than a few seconds. Also, if the
    # current timestamps is closer to 0 (i.e. the new cycle), make it so that a
    # big timestamps is still valid.
    # i.e. the - are the valid times
    #  0                                                   999
    #                  [------c
    #  ---c                                                [--
    max_time_diff = 5  # max time diff of 5 seconds
    max_timestamp = 999

    if current_timestamp > max_time_diff:
        # Easy case, the current timestamps is after X seconds, the key_timestamps
        # should be higher than c_t - X and lower than c_t
        return current_timestamp - max_time_diff < key_timestamp < current_timestamp
    else:
        # Tricky case, the c_t is before X seconds, the k_t can be between 0 and c_t or between 998 + c_t - X and 999:
        return 0 < key_timestamp < current_timestamp or \
               max_timestamp + current_timestamp - max_time_diff - 1 < key_timestamp < max_timestamp


@app.route("/get_post/")
def get_post():
    admin_key = request.args.get('admin_key')

    if not admin_key or not valid_admin_key(admin_key):
        flash('Only admins can access this page.')
        return redirect(url_for('home'))

    # Get the next post to check
    return str(Post.post_to_check())

@app.route("/check/<post_id>", methods=['GET', 'POST'])
def check_post(post_id):
    admin_key = request.args.get('admin_key')

    if not admin_key or not valid_admin_key(admin_key):
        flash('Only admins can access this page.')
        return redirect(url_for('home'))

    db = db_session()

    # Get the post
    post = db.query(Post).get(post_id)

    if not post:
        flash('No post selected')
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('post.html', post=post)

    post.checked = True
    db.commit()

    # Mock up a sql injection, this is not secure :o
    try:
        results = db.execute("select * from posts where id = {};".format(post_id))
        return "\n".join(str(a) for a in results)
    except Exception as e:
        return str(e)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # Get the form
    if request.method == 'GET':
        return render_template('signup.html')

    # From here, treat as a POST

    # Get the username from he form
    username = request.form.get('username', None)

    # Ensure it exists
    if not username:
        return render_template('signup.html', error="Username required.")

    # Get the username from he form
    password = request.form.get('password', None)

    # Ensure it exists
    if not password:
        return render_template('signup.html', error="Password required.")

    # Try to login/create
    user_exist, password_valid = User.try_login(username, password)

    # If the user does not exist, add it to the db, this corresponds to the Signup
    if not user_exist:
        User(name=username, password=password)

    if user_exist and not password_valid:
        return render_template('signup.html', error="Password invalid.")

    # At this point, the user exist and the password is valid, log him in

    # Login the user, save the username in the session and return to the
    # homepage
    user = User.query.filter_by(name=username).first()

    session['logged_in'] = True
    session['logged_username'] = username
    session['logged_user_id'] = user.id

    return redirect(url_for('home'))

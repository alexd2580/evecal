from functools import wraps
from flask import \
    render_template, redirect, url_for, \
    abort, flash, request, current_app, \
    make_response
from flask_login import login_required, current_user, login_user, logout_user

from . import app, db
from .models import User
from .forms import *

print('Processing views.py')

valid_paths = ['/', '/index', '/login', '/logout', '/register']

def next_is_valid(next):
    for i in valid_paths:
        if next == i:
            return True
    return False

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            return f(*args, **kwargs)
        return redirect(url_for('index_route'))
    return decorated_function

@app.route('/')
def root():
    return redirect(url_for('login_route'))
    #render_template('index.html')

@app.route('/index')
@login_required
def index_route():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login_route():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user is None or not user.verify_password(password):
            flash('Invalid username/password pair')
            return render_template('login.html', title='Sign In', form=form)
        login_user(user)
        flash('Logged in successfully as {}'.format(username))
        next = request.args.get('next')
        if not next_is_valid(next):
            return redirect(url_for('index_route'))
        return redirect(next or url_for('index_route'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout_route():
    logout_user()
    return redirect(url_for('login_route'))

@app.route('/register', methods=['GET','POST'])
@logout_required
def register_route():
    form = RegisterForm()
    if form.validate_on_submit():
        username = request.form['username']
        pw = request.form['password']
        pw_retype = request.form['retype_password']

        same_count = User.query.filter_by(username=username).count()
        if same_count != 0:
            flash('Username {} already taken'.format(username))
        elif pw != pw_retype:
            flash('Passwords do not match')
        else:
            new_user = User(username, pw)
            db.session.add(new_user)
            db.session.commit()
            flash('Successfully registered')
            return redirect(url_for('login_route'))
    return render_template('register.html', title='Register', form=form)

@app.route('/<other>', methods=['GET', 'POST'])
def not_found(other = None):
    flash('Invalid path: {}'.format(other))
    return redirect(url_for('index_route'))

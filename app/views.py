from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask_login import login_required, current_user, login_user, logout_user

from . import app
from .models import User
from .forms import *

print('Processing views.py')

@app.route('/')
def root():
    return redirect('login')
    #render_template('index.html')

@app.route('/index')
@login_required
def index_route():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.verify_password(request.form['password']):
            flash('Invalid username/password pair')
            return render_template('login.html', title='Sign In', form=form)
        login_user(user)
        flash('Logged in successfully as {}'.format(form.username.data))
        next = flask.request.args.get('next')
        if not next_is_valid(next):
            return flask.abort(400)
        return redirect(next or url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout_route():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register_route():
    form = RegisterForm()
    if form.validate_on_submit():
        flash('Successfully registered')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

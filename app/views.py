from functools import wraps
from flask import \
    render_template, redirect, url_for, \
    abort, flash, request, current_app, \
    make_response
from flask_login import login_required, current_user, login_user, logout_user

from . import app, db
from .models import User, Event
from .forms import *

from datetime import date, datetime, timedelta
from calendar import Calendar

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

# Returns the date of the first day of the next month
def get_next_month(this_month):
    # increasing the date by 40 days should
    m = ((this_month.month + 1) % 13) + 1
    y = this_month.year
    if m == 1:
        y += 1
    return date(y, m, 1)

# get_month_and_events :: [Week [Day Name Date [Event ID Name]]]
def get_month_and_events(year, month):
    cal = Calendar(0) # default replace by user db?
    the_month = cal.monthdatescalendar(year, month)

    begin = the_month[0][0]
    end = the_month[-1][-1]
    events = Event.query.filter(
        Event.event_date > begin.strftime('%Y-%m-%d'),
        Event.event_date < end.strftime('%Y-%m-%d'))
    print(events)

    def per_day(day):
        return (day.strftime('%A'), day)

    def per_week(week):
        return [per_day(d) for d in week]

    def per_month(month):
        return [per_week(w) for w in month]

    return per_month(the_month)

# get_day_and_events :: [Event ID Name]
def get_day_and_events(year, month, day):
    today = date(year,month,day)
    tomorrow = today + timedelta(days=1)
    events = Event.query.filter(
        Event.event_date > today.strftime('%Y-%m-%d'),
        Event.event_date < tomorrow.strftime('%Y-%m-%d')).all()
    return events

@app.route('/calendar', methods=['GET'])
def calendar_route():
    now = date.today()
    year = int(request.args.get('year') or now.year)
    month = int(request.args.get('month') or now.month)
    day = request.args.get('day')
    if day is not None:
        day = int(day)

    at_month = date(2016, month, 1)
    month_name = at_month.strftime("%B")

    if day is None:
        month_and_events = get_month_and_events(year, month)
        return render_template(
            'calendar_month.html',
            title='Calendar',
            year=year,
            month=month,
            month_name=month_name,
            month_and_events=month_and_events)

    day_and_events = get_day_and_events(year, month, day)
    return render_template(
        'calendar_day.html',
        title='Calendar',
        year=year,
        month=month,
        day=day,
        month_name=month_name,
        day_and_events=day_and_events)

@app.route('/<other>', methods=['GET', 'POST'])
def not_found(other = None):
    flash('Invalid path: {}'.format(other))
    return redirect(url_for('index_route'))


"""
# Returns the localized month name
# Assuming date(2016, month, 1) returns the first day of month=month
def month_to_name(month):
    at_month = date(2016, month, 1)
    return at_month.strftime("%B")

# Returns a list of weeks where each week contains a list of days
# Hardcoding Monday to be the first day of the week
def date_to_weeks(year, month):
    start_date = date(year, month, 1)
    day_of_week = start_date.weekday()
    one_day = timedelta(1)
    start_date -= day_of_week * one_day

    weeks = []
    while start_date.month <= month:
        week = []
        for i in range(0,7):
            week.append(start_date.strftime("%A"))
            start_date += one_day
        weeks.append(week)

    return weeks

# Can be performed once! TODO
# Returns a list of localized weekday names
# Hardcoding Monday to be the first day of the week
def week_to_days():
    now = date.today()
    one_day = timedelta(1)
    monday = now - now.weekday() * one_day
    weekdays = []
    for i in range(0,7):
        weekdays.append((monday + timedelta(i)).strftime("%A"))
    return weekdays
"""

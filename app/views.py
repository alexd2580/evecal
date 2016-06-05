from functools import wraps
from flask import \
    render_template, redirect, url_for, \
    abort, flash, request, current_app, \
    make_response
from flask_login import login_required, current_user, login_user, logout_user

from . import app, db
from .models import *
from .forms import *

from datetime import date, datetime, timedelta
from calendar import Calendar
from urllib.parse import quote

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

# / redirects to calendar
@app.route('/')
def root():
    return redirect(url_for('calendar_route'))
    #render_template('index.html')

# TODO remove /index
@app.route('/index')
@login_required
def index_route():
    return render_template('index.html', user=current_user)

# Login form
# Get request displays a login-form
# Post checks user credentials and loggs in the user, redirects to calendar
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
        if next_is_valid(next):
            return redirect(next)
        return redirect(url_for('index_route'))

    return render_template('login.html', title='Sign In', form=form)

# Loggs out the user
# Redirects to calendar
@app.route('/logout')
@login_required
def logout_route():
    logout_user()
    return redirect(url_for('calendar_route'))

# On GET displays a register new user form
# On post checks if the username is already taken
# Adds a user-entry and redirects to login
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

# displays the calendar.
# If year and month are submitted, displays a month views
# If the day is also submitted displays a day-view
# POST requests "subscribe" and "unsubscribe"  perform the named actions
# and redirect back to the calendar
@app.route('/calendar', methods=['GET','POST'])
def calendar_route():
    if request.method == 'POST':
        unsubscribe = request.form.get('unsubscribe')
        if unsubscribe is not None:
            optionally_redundant_subscriptions = Subscription.query\
                .filter(Subscription.event_id == int(unsubscribe))\
                .filter(Subscription.user_id == current_user.id)

            optionally_redundant_subscriptions.delete()
            db.session.commit()
            flash('Unsubscribed from event')

        subscribe = request.form.get('subscribe')
        if subscribe is not None:
            # Integrity checks
            optionally_redundant_subscriptions = Subscription.query\
                .filter(Subscription.event_id == int(subscribe))\
                .filter(Subscription.user_id == current_user.id).all()
            if not optionally_redundant_subscriptions:
                s = Subscription(current_user.id, int(subscribe))
                db.session.add(s)
                db.session.commit()
                flash('Subscribed to event')
            flash('Already subscribed to that event')

        redirect(url_for('calendar_route'))

    now = date.today()
    year = int(request.args.get('year') or now.year)
    month = int(request.args.get('month') or now.month)
    day = request.args.get('day')

    at_month = date(2016, month, 1)
    month_name = at_month.strftime("%B")

    if day is None:
        month_and_events = get_month_and_events(year, month)
        return render_template(
            'calendar_month.html',
            title='Calendar',
            month_name=month_name,
            month_and_events=month_and_events)

    day = int(day)
    day_and_events = get_day_and_events(year, month, day)
    #day_and_events = [(e,e.creator) for e in day_and_events]
    return render_template(
        'calendar_day.html',
        title='Calendar',
        year=year,
        month=month,
        day=day,
        month_name=month_name,
        this_path=quote(request.path),
        day_and_events=day_and_events)


@app.route('/add', methods=['GET', 'POST'])
def add_route():
    form = EventForm()
    if form.validate_on_submit():
        event_name = request.form['eventname']
        event_date = form.starttime.data
        event_descr = request.form['eventdescr']
        e = Event(event_date, event_name, event_descr, current_user.id)

        db.session.add(e)
        db.session.commit()

        return redirect(url_for('calendar_route'))

    return render_template(
        'add_event.html',
        form=form,
        title='Add Event')


@app.route('/edit', methods=['GET', 'POST'])
def edit_route():
    next = request.args.get('next')
    if next is None:
        next = url_for('calendar_route')

    form = EditForm()
    if form.validate_on_submit():
        id = request.form['eventid']
        event = Event.query.filter(Event.id == int(id)).one()

        event.name = request.form['eventname']
        event.event_date = form.starttime.data # request.form['starttime']
        # any reasons to use only one of the accessors?
        event.description = request.form['eventdescr']

        db.session.commit()

        return redirect(next)

    id = request.args.get('id')
    if id is None:
        return redirect(next)

    event = Event.query.filter(Event.id == int(id)).one()

    if event.creator_id != current_user.id:
        flash('You cannot edit this event')
        return redirect(next)

    form.eventid.data = event.id
    form.eventname.data = event.name
    form.starttime.data = event.event_date
    form.eventdescr.data = event.description

    return render_template(
        'edit_event.html',
        title='Edit Event',
        next=next,
        form=form)


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

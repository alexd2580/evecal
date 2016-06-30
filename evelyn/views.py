from functools import wraps
from flask import \
    render_template, redirect, url_for, \
    abort, flash, request, current_app, \
    make_response
from flask_login import \
    login_required, current_user, \
    login_user, logout_user

from sqlalchemy.orm import lazyload

from datetime import date, datetime, timedelta, time
from calendar import Calendar
from urllib.parse import quote

from .models import *
from .forms import *

################################################################################

print('Initializing views')

# returns the timedelta as a string (currently english)
# if it is less than a minute, returns "now"
# if the timedelta is negative, returns "already passed"
def timedelta_to_string(rem):
    def with_word(num, singular, multiple):
        if num < 0:
            return ''
        elif num == 1:
            return str(num) + ' ' + singular + ' '
        else:
            return str(num) + ' ' + multiple + ' '

    if rem.seconds < 60:
        return 'now'
    if rem.days < 0:
        return 'already passed'

    (minutes, _) = divmod(rem.seconds, 60)
    (hours, minutes) = divmod(minutes, 60)

    s = with_word(rem.days, 'day', 'days')
    s += with_word(hours, 'hour', 'hours')
    s += with_word(minutes, 'minute', 'minutes')

    return s.strip()

# fix_month_year :: Month -> Year -> (Month, Year)
def fix_month_year(m, y):
    while m > 12:
        m -= 12
        y += 1
    while m < 1:
        m += 12
        y -= 1
    return (m, y)

# Returns the date of the first day of the next month
def get_next_month(this_month):
    (m, y) = fix_month_year(this_month.month + 1, this_month.year)
    return date(y, m, 1)

# Returns the date of the first day of the prev month
def get_prev_month(this_month):
    (m, y) = fix_month_year(this_month.month - 1, this_month.year)
    return date(y, m, 1)

valid_paths = ['/', '/login', '/logout', '/register']

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
        return redirect(url_for('calendar_route'))
    return decorated_function

################################################################################
# / redirects to calendar
@current_app.route('/')
def root():
    return redirect(url_for('calendar_route'))

################################################################################
# Login form
# Get request displays a login-form
# Post checks user credentials and loggs in the user, redirects to calendar
@current_app.route('/login', methods=['GET', 'POST'])
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
        return redirect(url_for('calendar_route'))

    return render_template('login.html', title='Sign In', form=form)

################################################################################
# Loggs out the user
# Redirects to calendar
@current_app.route('/logout')
@login_required
def logout_route():
    logout_user()
    return redirect(url_for('calendar_route'))

################################################################################
# On GET displays a register new user form
# On post checks if the username is already taken
# Adds a user-entry and redirects to login
@current_app.route('/register', methods=['GET','POST'])
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

################################################################################
# get_month_and_events :: [Week [Day Name Date [Event]]]
# get_month_and_events :: [Week [Day Name Date (Bool, Bool, Bool))]]
def get_month_and_events(year, month):
    cal = Calendar(0) # default replace by user db?
    the_month = cal.monthdatescalendar(year, month)

    begin = the_month[0][0]
    end = the_month[-1][-1]
    events = Event.query.filter(
        Event.event_date > begin.strftime('%Y-%m-%d'),
        Event.event_date < end.strftime('%Y-%m-%d')) \
        .options(lazyload('creator')).all()

    your_subscriptions = []
    if not current_user.is_anonymous:
        your_subscriptions = db.session.query(Subscription.event_id) \
            .filter(Subscription.user_id == current_user.id).all()
        your_subscriptions = [x for (x,) in your_subscriptions]

    def per_day(day):
        some_events = False
        created = False
        subscribed = False

        datetime_day = datetime.combine(day, time())
        next_day = datetime_day + timedelta(days = 1)

        for e in events:
            if e.event_date >= datetime_day and e.event_date < next_day:
                some_events = True
                if not current_user.is_anonymous:
                    created |= e.creator_id == current_user.id
                    subscribed |= e.id in your_subscriptions

        return (day.strftime('%A'), day, some_events, created, subscribed)

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

################################################################################
# displays the calendar.
# If year and month are submitted, displays a month views
# If the day is also submitted displays a day-view
# POST requests "subscribe" and "unsubscribe"  perform the named actions
# and redirect back to the calendar
@current_app.route('/calendar', methods=['GET','POST'])
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
            else:
                flash('Already subscribed to that event')

        next = request.form.get('next') or url_for('calendar_route')
        return redirect(next)

    now = date.today()
    year = int(request.args.get('year') or now.year)
    month = int(request.args.get('month') or now.month)
    day = request.args.get('day')

    at_month = date(year, month, 1)
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

################################################################################
# Route for /event
# Handles GET requests, which display the event. Event owners are presented with an edit form
# Right side of this view contains the list of subscribers, which can edit their own subscriptions.
@current_app.route('/event', methods=['GET'])
def event_route():
    event_id = request.args.get('id')
    if event_id is None:
        flash('Event id required for "/event"')
        return redirect(url_for('calendar_route'))

    event = Event.query.filter(Event.id == event_id).first()
    if event is None:
        flash('Event with id ' + event_id + ' not found')
        return redirect(url_for('calendar_route'))

    # Helper function to create a subscription_form on the fly.
    def make_subscription_form(subscr):
        subscr_form = SubscriptionForm()
        subscr_form.subscriptionid.data = subscr.id
        subscr_form.comment.data = subscr.comment
        subscr_form.commitment.data = subscr.commitment
        return subscr_form

    event_form = EditForm()
    event_form.eventid.data = event.id
    event_form.eventname.data = event.name
    event_form.starttime.data = event.event_date
    event_form.eventdescr.data = event.description
    now = datetime.now()
    event_form.timeleft = timedelta_to_string(event.event_date - now)
    event_form.creatorid = event.creator_id

    return render_template(
        'event.html',
        title = 'Event',
        subscriptions = event.subscriptions,
        make_subscription_form = make_subscription_form,
        event_form = event_form)

################################################################################
# Handles POST requests, which are used to edit the event.
# Redirects to /event?id={{request.form['eventid']}}
@current_app.route('/edit_event', methods=['POST'])
def edit_event_route():
    id = request.form['eventid']

    event_form = EditForm()
    if event_form.validate_on_submit():
        event = Event.query.filter(Event.id == int(id)).one()

        if event.creator_id == current_user.id:
            event.name = request.form['eventname']
            event.event_date = event_form.starttime.data # ?
            event.description = request.form['eventdescr']
            db.session.commit()
        else:
            flash('You cannot edit this event')

    return redirect(url_for('event_route', id=id))

################################################################################
@current_app.route('/edit_subscription', methods=['POST'])
def edit_subscription_route():
    form = SubscriptionForm()
    if form.validate_on_submit():
        subscription = Subscription.query \
            .filter(Subscription.id == request.form.get('subscriptionid')) \
            .options(lazyload('user')) \
            .options(lazyload('event')).one()

        subscription.comment = request.form.get('comment')
        subscription.commitment = request.form.get('commitment')
        db.session.commit()

    return redirect(url_for('event_route', id=subscription.event_id))

################################################################################
@current_app.route('/subscriptions', methods=['GET', 'POST'])
@login_required
def subscriptions_route():
    if request.method == 'POST':
        unsubscribe = request.form.get('unsubscribe')
        if unsubscribe is not None:
            optionally_redundant_subscriptions = Subscription.query\
                .filter(Subscription.event_id == int(unsubscribe))\
                .filter(Subscription.user_id == current_user.id)

            optionally_redundant_subscriptions.delete()
            db.session.commit()
            flash('Unsubscribed from event')

        return redirect(url_for('subscriptions_route'))

    # events = current_user.subscriptions
    events = db.session.query(Event).join(Subscription) \
        .filter(Subscription.user_id==current_user.id) \
        .order_by(Event.event_date).all()

    now = datetime.now()
    for e in events:
        e.remaining_time = timedelta_to_string(e.event_date - now)

    return render_template(
        'subscriptions.html',
        title='Your subscriptions',
        events=events)

@current_app.route('/add', methods=['GET', 'POST'])
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

@current_app.route('/<other>', methods=['GET', 'POST'])
def not_found(other = None):
    flash('Invalid path: {}'.format(other))
    return redirect(url_for('calendar_route'))


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

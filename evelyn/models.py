
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from flask_sqlalchemy import SQLAlchemy
import enum

#TODO mixin created_at, modified_at

print('Initializing database')
db = SQLAlchemy()

# A registered user
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(128))
    registration_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # The events a user has created and has the right to modify
    events_created = db.relationship('Event', back_populates='creator', lazy='joined')

    # The events a user has subscribed to
    subscriptions = db.relationship('Subscription', back_populates='user', lazy='joined')

    @property
    def subscription_ids(self): #poly-orm rewrite
        return [ s.event.id for s in self.subscriptions ]


    def __init__(self, username, password, email=None):
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return '<User {}: {}>'.format(self.id, self.username)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def visit(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# An event (aka calendar entry)
class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)

    event_date = db.Column(db.DateTime())
    name = db.Column(db.String(80))
    description = db.Column(db.Text)

    # The creator of this particular event
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', back_populates='events_created', lazy='joined')

    # All the users which have subscribed to this event
    subscriptions = db.relationship('Subscription', back_populates='event', lazy='joined')

    def __init__(self, event_date, name, description, user_id):
        self.event_date = event_date
        self.name = name
        self.description = description
        self.creator_id = user_id

    def __repr__(self):
        return '<Event {}: {}>'.format(self.id, self.name, self.event_date)

class Commitment(enum.Enum):
    yes = 'yes'
    no = 'no'
    maybe = 'maybe'

# A subscription of a user to an event. M to N relation
class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='subscriptions', lazy='joined')

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    event = db.relationship('Event', back_populates='subscriptions', lazy='joined')

    # Whether the user actively takes part in the event or not
    commitment = db.Column(db.Enum('Yes', 'No', 'Maybe'))

    # Each user can add a comment (for example the role he is going to play in the event)
    comment = db.Column(db.Text)

    def __init__(self, user_id, event_id):
        self.user_id = user_id
        self.event_id = event_id
        self.commitment = 'Yes'

    def __repr__(self):
        return '<Subscr {}: {} to {}>'.format(self.id, self.user.username, self.event.name)

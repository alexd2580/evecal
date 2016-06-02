
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import app, db, login_manager

#TODO mixin created_at, modified_at

print('Processing models.py')



class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(128))
    registration_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    events_created = db.relationship('Event', back_populates='creator')


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

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.DateTime())
    name = db.Column(db.String(80))
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', back_populates='events_created')
        #backref=db.backref('own_events', lazy='dynamic'))

    def __init__(self, event_date, name, description, user):
        self.event_date = event_date
        self.name = name
        self.description = description
        self.creator_id = user.id

    def __repr__(self):
        return '<Event {}: {}>'.format(self.id, self.name, self.event_date)

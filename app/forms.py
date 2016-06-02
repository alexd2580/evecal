from wtforms.validators import DataRequired, Email
from wtforms import \
    StringField, BooleanField, \
    PasswordField, DateField

from wtforms.fields.html5 import EmailField

from flask_wtf import Form

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(Form):
    username = StringField('username', validators=[DataRequired()])
    email = EmailField('email', validators=[Email()])
    password = PasswordField('password', validators=[DataRequired()])
    retype_password = PasswordField('retype_password', validators=[DataRequired()])

class EventForm(Form):
    eventname = StringField('eventname', validators=[DataRequired()])
    starttime = DateField('starttime', validators=[DataRequired()])
    eventdescr = StringField('eventdescr', validators=[])

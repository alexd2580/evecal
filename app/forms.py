from wtforms import \
    StringField, BooleanField, \
    PasswordField, DateTimeField, \
    HiddenField
from wtforms.validators import DataRequired, Email
from wtforms.widgets import TextArea
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
    starttime = DateTimeField('starttime', validators=[DataRequired()])
    eventdescr = StringField('eventdescr', validators=[], widget=TextArea())

class EditForm(Form):
    eventid = HiddenField('id')
    eventname = StringField('eventname', validators=[DataRequired()])
    starttime = DateTimeField('starttime', validators=[DataRequired()])
    eventdescr = StringField('eventdescr', validators=[], widget=TextArea())

from wtforms.validators import DataRequired
from wtforms import StringField, BooleanField, PasswordField

from flask_wtf import Form

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class RegisterForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    retype_password = PasswordField('retype_password', validators=[DataRequired()])

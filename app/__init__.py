"""
Initializes the app, a login_manager and the database
"""

# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../eventsandusers.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'tanks for all ze zsh'
app.config['WTF_CSRF_ENABLED'] = True

Bootstrap(app)

# Init database
db = SQLAlchemy()
db.init_app(app)

# Init LoginManager
login_manager = LoginManager()
#login_manager.session_protection = 'strong'
#login_manager.login_view = 'auth.login'
login_manager.init_app(app)
login_manager.login_view = '/login'

from . import views
# After the views are imported (indirect import of models) - create_db
with app.app_context():
    # Extensions like Flask-SQLAlchemy now know what the "current" app
    # is while within this block. Therefore, you can now run........
    db.create_all()
    

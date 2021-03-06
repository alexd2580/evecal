
# TODO add instantiation to the factory
from flask_login import LoginManager
login_manager = LoginManager()

def create_app(config_filename):
    from flask import Flask
    app = Flask(__name__)

    # Load defaults
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../eventsandusers.db'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SECRET_KEY'] = 'veryverysecret'
    app.config['WTF_CSRF_ENABLED'] = True
    # Load from config_filename
    app.config.from_pyfile(config_filename)

    # Init LoginManager
    #login_manager.session_protection = 'strong'
    #login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    login_manager.login_view = '/login'

    # Init Bootstrap
    from flask_bootstrap import Bootstrap
    Bootstrap(app)

    # Init Database
    from .models import db, User, Event, Commitment, Subscription
    db.init_app(app)
    with app.app_context():
        import evelyn.views
        db.create_all()

    # Init Admin view
    from flask_admin import Admin
    from flask_admin.contrib.sqla import ModelView

    admin = Admin(app, name='microblog', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Event, db.session))
    admin.add_view(ModelView(Subscription, db.session))

    return app

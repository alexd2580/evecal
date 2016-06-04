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


"""
    class Event(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80), unique=False)
        description = db.Column(db.Text, unique=False)
        date = db.Column(db.DateTime, unique=False)
        date_submitted = db.Column(db.DateTime, unique=False)
        submitter = db.Column(db.Integer, db.ForeignKey('user.id'))

        def __init__(self, name, description, date):
            self.name = name
            self.description = description
            self.date = date
            self.date_submitted = datetime.utcnow()

        def __repr__(self):
            return '<{} {}>'.format(self.a, self.b)


    class NewEventForm(Form):
        name =
        dt = DateField('DatePicker', format='%Y-%m-%d')

    # Handlers

    def commit_entry(a,b):
        print('Adding new relation ' + a + ' - ' + b)
        db.session.add(Relation(a,b))
        db.session.commit()
        print('Done')

    @app.route('/submit_entry', methods=['POST'])
    def submit_entry():
        commit_entry(request.form['a'], request.form['b'])
        return list_all()

    @app.route('/list_all', methods=['GET'])
    def list_all():
        return render_template('list_all.html', navigation = Relation.query.all())

    @app.route('/add_entry')
    def add_entry():
        form = ExampleForm()
        if form.validate_on_submit():
            return form.dt.data.strftime('%Y-%m-%d')
        return render_template('example.html', form=form)
        return render_template('add_entry.html')


    """

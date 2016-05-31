"""
Initializes the app, a login_manager and the database
"""

# Imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SECRET_KEY'] = 'tanks for all ze zsh'
app.config['WTF_CSRF_ENABLED'] = True

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

    def commit_new_user(uname, pw, pw_retype):
        print('Adding new user ' + uname)
        same_count = User.query.filter_by(username=uname).count()
        if(same_count != 0):
            username_taken = True
        if(pw != pw_retype):
            password_mismatch = True
        if(username_taken or password_mismatch):
            return register_user(
                username = username,
                username_taken=username_taken,
                password_mismatch=password_mismatch)
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        print('Done')
        return hello()

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

    @app.route('/verify_registered', methods=['POST'])
    def verify_registered():
        commit_new_user(
            request.form["username"],
            request.form["password"],
            request.form["password_retype"])
        return hello()

    @app.route('/register_user')
    def register_user():
        return render_template('register_user.html')

    @app.route('/<other>', methods=['GET', 'POST'])
    def not_found(other = None):
        return '<html> '+other+' not found </html>'

    """

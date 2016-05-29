from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Relation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    a = db.Column(db.String(80), unique=False)
    b = db.Column(db.String(80), unique=False)

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __repr__(self):
        return '<{} {}>'.format(self.a, self.b)


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/list_all")
def list_all():
    return render_template('list_all.html', navigation = Relation.query.all())

@app.route("/add_entry")
def add_entry():
    return "<form><input type=\"text\" /><input type=\"submit\" /></form>"

if __name__ == "__main__":
    app.run()

print("Exiting application")

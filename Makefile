all:
	virtualenv venv	;\
	. venv/bon/activate ;\
	pip install Flask ;\
	pip install flask-bootstrap ;\
	pip install flask_login ;\
	pip install Flask-WTF ;\
	pip install Flask-SQLAlchemy

clean:
	rm -rf venv


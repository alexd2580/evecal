.PHONY: all clean

all:
	pyvenv venv
	venv/bin/pip install -r requirements.txt

clean:
	rm -rf venv

run:
	uwsgi --plugin python --http 0.0.0.0:8081 --virtualenv venv -w main:app --py-tracebacker --py-autoreload

.PHONY: all install setup check

all: install setup

# Install all dependencies and build static files.
install:
	pip install --disable-pip-version-check --upgrade pip
	pip install --upgrade --ignore-installed setuptools wheel
	python setup.py build_resources

# Set up the database for development.
setup:
	python manage.py migrate
	python manage.py init_project
	python manage.py load_config

check:
	black .
	isort .
	flake8

# Zues

Zues is a Django-based web application developed for the Jonge Democraten.
The JD regularly organizes political conferences. Members can send proposals
to the conference teams using this web application.

## Setup

### Prerequsites

MacOS:

1. Have Xcode command-line tools installed. `xcode-select --install`
2. Install dependencies
2.1. Make sure you have Python 3 installed. `brew install python` MacOS comes with Python 2.7 by default.
2.2. Install `virtualenv`. `brew install virtualenv`
2.3. Install `mysql`. `brew install mysql`

### Main

1. Use `build_env.sh` to setup an environment.
2. `source env/bin/activate` to activate the environment.
3. Copy `zuessite/local_settings_example.py` to `zuessite/local_settings.py`.
4. Follow instructions in `zuessite/local_settings.py`.
5. Use `python manage.py migrate` to setup the database.
6. Use `python manage.py createsuperuser` to create a superuser.
7. Use `python manage.py loaddata demo_data` to load some demo data _optional_
8. Use `python manage.py runserver` to start the server.

You can also run `docker-compose up -d` and in the webapp container run steps 5 till 8. Step 6 requires an interactive shell.

*Note that the server actually requires https*

## Using HTTPS for development environment

1. `pip install django-extensions Werkzeug pyOpenSSL`
2. Edit `zuessite/local_settings.py` to add `django_extensions` to `INSTALLED_APPS`.
3. Make an SSL certificate, e.g. with openssl and some filename like foobar.cert
4. Use `python manage.py runserver_plus --cert foobar.cert`

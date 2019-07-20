Zues
====
Zues is a Django-based web application developed for the Jonge Democraten.
The JD regularly organizes political conferences. Members can send proposals
to the conference teams using this web application.

Setup
=====
* Use `build_env.sh` to setup an environment.
* `source env/bin/activate.sh` to activate the environment.
* Copy `zuessite/local_settings_example.py` to `zuessite/local_settings.py`.
* Follow instructions in `zuessite/local_settings.py`.
* Use `python manage.py migrate` to setup the database.
* Use `python manage.py createsuperuser` to create a superuser.
* Use `python manage.py loaddata demo_data` to load some demo data [optional]
* Use `python manage.py runserver` to start the server.
  Note that the server actually requires https

Using HTTPS for development environment
=======================================
* `pip install django-extensions Werkzeug pyOpenSSL`
* Edit `zuessite/local_settings.py` to add `django_extensions` to `INSTALLED_APPS`.
* Make an SSL certificate, e.g. with openssl and some filename like foobar.cert
* Use `python manage.py runserver_plus --cert foobar.cert`

# Local settings for Zues.

# Step 1: generate a secret key and set it here.
# For example, run 'pwgen -s 50 1' and set the result here.
# Do not reuse a secret key from another place.
SECRET_KEY = ''

# Debug should be False in production
DEBUG = False
TEMPLATE_DEBUG = False

# Step 2: put all the domain names under which the site should be reachable
# in this list.
ALLOWED_HOSTS = []

# Step 3: when deploying in production, set STATIC_ROOT to the actual location
# of the site's static files.
# Do not set this value when runnig for development (i.e. manage.py runserver).
# STATIC_ROOT = '/usr/share/jonge-democraten/visie/static/'

# Step 4: set a database to store the application's information
# For development, SQLite is fine. For production, use MySQL.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'db.sqlite3',                   # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

# Step 5: set an LDAP server that stores the identity and access management data 
JANEUS_SERVER = "ldap://127.0.0.1:389/"
JANEUS_DN = "cn=readall,ou=sysUsers,dc=jd,dc=nl"
JANEUS_PASS = ""
from zues.utils import current_site_id
JANEUS_CURRENT_SITE = current_site_id

# Step 6: set Recaptcha-credentials.
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_USE_SSL = True
NOCAPTCHA = True

# Step 7: set an email host.
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587

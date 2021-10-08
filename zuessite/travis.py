from __future__ import absolute_import

from zuessite.settings import *

# Key only used for builds.
SECRET_KEY = 'travistravistravistravistravistravistravistravistravis'

# We do not need real Recaptcha keys in development.
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

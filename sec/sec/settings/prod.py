import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '$n%^#g%qx#82w6t^dvjqwv)q*1cy+fwh1ohku7-rbjqcei2^jr'

DEBUG = False

ALLOWED_HOSTS = ["example.com"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

""" Sessions """

SESSION_COOKIE_AGE = 1209600  # (default)
SESSION_COOKIE_SECURE = True    # Sets the SECURE flag on the session cookie (forces HTTPS on cookies)
SESSION_COOKIE_HTTPONLY = True  # Prevents client side scripting accessing the cookie (through document.cookie)
SESSION_SAVE_EVERY_REQUEST = True  # Renew session on every request

""" SSL """
SECURE_SSL_REDIRECT = True # Redirects to HTTPS if http protocol is requested

import os
from .base import *  # noqa

DEBUG = False

CSRF_TRUSTED_ORIGINS = [
    'https://sinalize.nodx.uk',
    'http://sinalize.nodx.uk',
]

if 'ALLOWED_HOSTS' not in os.environ:
    ALLOWED_HOSTS = [
        'sinalize.nodx.uk',
        'www.sinalize.nodx.uk',
    ]

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Traefik
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# USE_X_FORWARDED_HOST = True
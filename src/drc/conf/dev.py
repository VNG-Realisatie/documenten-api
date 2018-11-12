import os

os.environ.setdefault('SECRET_KEY', '%jp_t1u42ldzeb4s2d4tqj3ythtm)2)^ph%-b71#$*7_=&-(!g')
os.environ.setdefault('DB_NAME', 'drc')
os.environ.setdefault('DB_USER', 'drc')
os.environ.setdefault('DB_PASSWORD', 'drc')

os.environ.setdefault('ZTC_JWT_SECRET', 'drc-to-ztc')
os.environ.setdefault('ZRC_JWT_SECRET', 'drc-to-zrc')

from .base import *  # noqa isort:skip

#
# Standard Django settings.
#

DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ADMINS = ()
MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

LOGGING['loggers'].update({
    'drc': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'django': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
    'django.db.backends': {
        'handlers': ['django'],
        'level': 'DEBUG',
        'propagate': False,
    },
    'performance': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': True,
    },
})

#
# Additional Django settings
#

# Disable security measures for development
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False

#
# Custom settings
#
ENVIRONMENT = 'development'

#
# Library settings
#

# Django debug toolbar
INSTALLED_APPS += [
    'debug_toolbar',
]
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

AXES_BEHIND_REVERSE_PROXY = False  # Default: False (we are typically using Nginx as reverse proxy)

# in memory cache and django-axes don't get along.
# https://django-axes.readthedocs.io/en/latest/configuration.html#known-configuration-problems
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'axes_cache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

AXES_CACHE = 'axes_cache'

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += (
    'rest_framework.renderers.BrowsableAPIRenderer',
)

IS_HTTPS = False

# Override settings with local settings.
try:
    from .local import *  # noqa
except ImportError:
    pass

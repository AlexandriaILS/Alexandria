# Bespoke. Books. Battlestar Galactica.

The plan here is to design and implement, mostly for the sake of practice, an integrated library system for a small library.

It should include:

* open web view for patrons
* searching by various fields
* a locked-down web view for library staff
* ability to add new titles
* ability to import titles by MARC record
* hold management
* email notification capabilities
* handle fines with Stripe
* support for multiple locations
* support for books checked out by staff (no due date)
* support for books that need to be weeded
* support for replacing weeded books

* investigate adding bookstore functionality for sale of weeded materials

...and probably more. ¯\\\_(ツ)_/¯

## Local Development

Start by creating a `local_settings.py` file at the top level of the project. This allows you to modify settings and adjust things without making longer-lasting modifications and also allows you to configure the server however you wish by selectively overwriting settings. Example config:

```python
from alexandria.settings.local import *
import better_exceptions
import os

# trust me, this will make your life better.
better_exceptions.MAX_LENGTH = None
# Use this file when developing locally -- it has some helpful additions which
# change how the server runs.
DEBUG = True

ALLOWED_HOSTS = ['*']
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
# ideally this should be postgres, but developing against sqlite3 will work.
# Just be aware of potential issues where sqlite3 and postgres do not play well
# together -- namely, django migrations for sqlite3 will allow a field creation
# and field alter call in the same transaction. Postgres... will not.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'alexandria': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG')
        }
    },
}

MIDDLEWARE = ["alexandria.middleware.BetterExceptionsMiddleware"] + MIDDLEWARE
```

Running `behave` tests requires that you have `geckodriver` and Firefox installed -- you can get it from [the release page](https://github.com/mozilla/geckodriver/releases).

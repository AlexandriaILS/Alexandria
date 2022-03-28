---
icon: codespaces
order:100
---
# Getting Started

Going from nothing to 'up and running' doesn't take a lot, but it might take a few minutes! There are only a few things that you'll need to do.

## Local Setup

You will need:

* make
* git
* python3.10+
* [poetry](https://python-poetry.org/)

If you don't already have a modern version of Python installed, we recommend using [pyenv](https://github.com/pyenv/pyenv) to handle installing the appropriate Python version. Here's some example commands to get you started:

```shell
# There's more to installing pyenv than this covers.
# You'll need to make sure it's configured in your shell before it's usable.
pyenv install 3.10.2
pyenv global 3.10.2
# After you get the new version installed and activated, make sure pip is up
# to date
pip install --upgrade pip
# if you don't install poetry globally with the above link, this will do the
# trick. Otherwise skip this one.
pip install poetry
```

## The App

Alexandria can be found on GitHub [here](https://github.com/AlexandriaILS/Alexandria). Now that you have Poetry set up, we can clone the repository to your local machine and get dependencies installed.

!!!
This assumes you have ssh authentication configured in GitHub. See [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) for more info.
!!!

```shell
git clone git@github.com:AlexandriaILS/Alexandria.git
cd Alexandria
# Same as with pyenv, make sure that poetry is configured correctly in your
# shell. After you confirm it's working, the below command will install all
# of the dependencies needed by Alexandria.
poetry config virtualenvs.in-project true
poetry install
# Activate your new environment that Poetry just helpfully made for you with
# the following:
poetry shell
```

Create a file at the root of the repository called `local_settings.py`. This is where you'll put any settings overrides while you're working on the app; it's also required to even run in debug mode. Copy the below into your new file:

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

## Database Operations

Local dev can be done entirely with SQLite; it's not perfect, but it is more than enough to handle almost everything that Alexandria needs. All the initial setup commands are built into the `Makefile`, so just run the following to get set up:

!!!
Get a notice about not being able to import Django? Make sure that you've run `poetry shell` and that you've installed the dependencies first!
!!!

```shell
make migrate
make dev_data
```

The `migrate` command will set up the database to accept data and the `dev_data` command will create all the information needed for you to start working on the system. The default admin login is:

> username: 1234  
> password: asdf

Run `make run` to start the development server -- you should be able to access the site on `http://localhost:8000`!

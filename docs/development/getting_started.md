---
order: 100
icon: codespaces
tags: [dev, development]
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
#
# Now, that being said: though sqlite is the default dev database, you can work
# with Postgres if you have it installed locally (or installed through docker,
# which is the slightly easier method if you don't want to pollute your computer.)
# If you need to install docker, start here:
# https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'alexandria',
#         'USER': 'alexandria',
#         'PASSWORD': 'asdf',
#         'HOST': '127.0.0.1',
#         'PORT': '5432',
#     }
# }
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

## Developing with PostgreSQL

Alexandria is set up to be functional with the sqlite3 database out of the box because it's a bit easier to get running, but it's not representative of how it should be run in production. Alexandria is designed to take advantage of PostgreSQL's fantastic feature set, so if you really want to work on the cool stuff, you'll need to get Postgres working. There are two ways to do that.

!!!
In your `local_settings.py`, make sure that the `DATABASES` key that refers to sqlite3 is commented out and the `DATABASES` key that refers to postgres is uncommented; you shouldn't have to modify any of the fields.
!!!

### Running PostgreSQL in Docker

The preferred method for working with Postgres and Alexandria is this option: Postgres in a docker image. It allows much more standardization and lets you effectively start over quickly without worrying about other services that are on your local machine that might be using Postgres. Getting started is very quick as everything is already in makefile commands.

Start by making sure that Docker is installed -- [this is a great tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04) if you don't already have the docker CLI installed.

!!! :warning: Watch out, gotcha ahead! :warning:
The Makefile expects that you've configured `docker` to run without `sudo`. If you haven't done that, you'll need to modify your local copy of the Makefile by just adding `sudo` before each of the docker commands.
!!!

```shell
# bring up the db
make psql_up

# configure the container for our use
make psql_setup

# push the db schema to the container
make migrate

# bring down the db when you're down
make psql_down
```

At this point, running `make run` should just work and have all of your queries passed through the Postgres Docker container!

### Install PostgreSQL on your local machine

The first thing you'll need to do is install a new version of PostgreSQL that works for your operating system. After that's done, there's a little bit of setup that needs to happen:

Activate the Postgres shell using `psql`:

```shell
psql -h localhost -U postgres
```

After that, you should land at a shell that looks like this:

```
psql (14.2 (Debian 14.2-1.pgdg110+1))
Type "help" for help.

postgres=#
```

Run the following commands in your new shell to configure the database:

!!!danger Hey! Listen! :sparkles:
Make sure to end every command with a semicolon (`;`) AND press Enter when you're done to execute the command. The shell will print out the name of the command that you just ran (for example, after you run the first "CREATE DATABASE" command, it should print "CREATE") back into the console. That's how you know the command just ran. If you don't see that line, try typing a semicolon and pressing enter again; usually that line terminator just got misplaced.
!!!

```sql
CREATE DATABASE alexandria;
CREATE USER alexandria WITH SUPERUSER PASSWORD 'asdf';
GRANT ALL ON DATABASE alexandria TO alexandria;
```

If everything ran correctly, you should see the following responses to your commands:

```shell
CREATE
CREATE
GRANT
```

After that's done, go ahead and run `make psql_setup` -- that should try to connect to the db and verify that everything's working. If the command finishes, then Alexandria can talk to your install!

Run `make migrate` to push the db schema and then finally `make run` to start Alexandria -- at this point you're off to the races!

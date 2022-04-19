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
* Docker (Probably. More on that later.)

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'alexandria',
        'USER': 'alexandria',
        'PASSWORD': 'asdf',
        'HOST': '127.0.0.1',
        'PORT': '5432',
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

Alexandria requires [PostgreSQL](https://www.postgresql.org/download/), a free and open source database, to function. We rely heavily on the fantastic features provided, so you will need to have an instance of Postgres running before you can bring up Alexandria locally. This is easiest if you have Docker installed -- here are instructions for [Ubuntu and WSL2](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04) or [MacOS](https://docs.docker.com/desktop/mac/install/).

!!!warning
Before continuing, make sure you can access docker by running `docker version` (without sudo!). It should print out two sections: one about the Client and one about the Server. If you only see the block about the Client and you get an error about the Server section (usually something like "cannot connect to docker client -- is it running?") then check the following:

* make sure the server is running
* if `sudo docker version` works, you need to fix your permissions

==- Instructions for running docker without sudo (Ubuntu / WSL2 only)
Add your user to the docker group by running the following command in your terminal:

```shell
sudo usermod -aG docker ${USER}
```

You can then either log out and log back in OR force the changes to take effect immediately by running this:

```shell
su - ${USER}
```

Verify that you see the `docker` group listed for your account by running:

```shell
groups
```
It should look something like this:

![](/static/wsl_groups_screenshot.png)

===

!!!

All the initial setup commands are built into the `Makefile`, so just run the following to get set up:

!!!
Get a notice about not being able to import Django? Make sure that you've run `poetry shell` and that you've installed the dependencies first!
!!!

```shell
make db_up
# wait a few seconds after it completes before running the next one
make db_setup

# now we can put data in it!
make migrate
make dev_data
```

The `migrate` command will set up the database to accept data and the `dev_data` command will create all the information needed for you to start working on the system. The default admin login is:

> username: 1234  
> password: asdf

Run `make run` to start the development server -- you should be able to access the site on `http://localhost:8000`! You can bring the database down separately at any time by running `make db_down`.


### Install PostgreSQL on your local machine

We recommend the docker method over this one, as this will leave Postgres running locally on your machine after you're finished working with Alexandria, and you may not want or need that. If you still want to run Postgres locally (and not involve Docker), then read on.

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
-- Note: if this fails, you need to install postgresql-contrib. pg_trgm is NOT optional.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- After you get pg_trgm installed, you can build the rest:
CREATE DATABASE alexandria;
CREATE USER alexandria WITH SUPERUSER PASSWORD 'asdf';
GRANT ALL ON DATABASE alexandria TO alexandria;
```

If everything ran correctly, you should see the following responses to your commands:

```shell
CREATE
CREATE
CREATE
GRANT
```

After that's done, go ahead and run `make db_setup` -- that should try to connect to the db and verify that everything's working. If the command finishes, then Alexandria can talk to your install!

Run `make migrate` to push the db schema and then finally `make run` to start Alexandria -- at this point you're off to the races!

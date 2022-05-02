---
order: 90
icon: device-desktop
tags: [dev, development, postgres, psql]
---
# Using Alexandria Locally

## Introduction

Now that you have everything installed and working, in this page we'll cover how to interact with Alexandria from the command line and all the common commands that you might need.

## Prerequisites

* completed [Environment Setup](environment_setup.md)
* completed [Getting It Running](getting_started.md)

## Interacting with Alexandria

Start by bringing up the database; you will always need to have PosgreSQL running before running Alexandria.

```shell
make db_up
```

Once that completes, we're ready to start Alexandria.

```shell
make run
```

This will start the local server running at [http://localhost:8000/](http://localhost:8000/). If you load that page now, you should see logs start to fill your terminal screen. If you change any code, the server will automatically reload in your terminal. Wait a moment, refresh the page in your web browsers, and you'll be running the new version of the code!

!!!
Did you get a long error that has `django.db.utils.OperationalError:` at the end? Make sure the database is running from the previous step: `make db_up`!
!!!

The default admin login is:

> username: 1234  
> password: asdf

Stop Alexandria in your terminal by pressing CTRL+C.

If you're done working and need to bring down the database, you can do so with:

```shell
make db_down
```

## Resetting the Database

!!!danger Danger!
:arrow_right: **THIS WILL DELETE ALL YOUR DATA IN POSTGRES.** :arrow_left:

Do not do this unless you actually want to reset your database!
!!!

To reset your data, run the following command:

```shell
make clean
```

This removes all the data in Postgres and leaves it empty. If you're doing development work, you will need to repopulate the database with the development data again by running:

```shell
make dev_data
```

## Testing Alexandria

Tests make sure that we don't break existing functionality while working on new features and make sure that new features work the way they're supposed to! If you just want to run the tests directly, make sure that the Python environment is activated (`poetry shell`) and run the following:

```shell
pytest
```

You can run a specific file of tests (or a group of tests) by specifying the folder for `pytest` to check:

```shell
pytest alexandria/api
```

If you want to run all the tests the fast way, run:

```shell
make test
```

## Launching the Docs Server

If you want to work on the documentation (these pages!) then [you will need to install Retype](https://retype.com/) -- more information [in the Documentation page](documentation.md).

After Retype is installed, run the Retype server by running the following:

```shell
make docs
```

## Interacting with Alexandria on the Command Line

Sometimes you need to access Alexandria or the database directly; you can do so with the below commands.

Access Alexandria's command line:

```shell
make shell
```

Open the database (`psql`) command line:

```shell
make psql_shell
```

Congratulations! You now have all the commands and resources you need to work on Alexandria locally.

---
order: 0
icon: database
tags: [dev, development, postgres, psql]
---

# Local PostgreSQL Install

## Introduction

!!!danger :rotating_light: Stop! :rotating_light:
You don't need to do this if you take the recommended Docker route.

:arrow_right: **This method is not supported.** :arrow_left: 

Unless you really need this or cannot use Docker, please use the method outlined in the regular Environment Setup.

[!ref](environment_setup.md)
!!!

We recommend the docker method over this one, as this will leave Postgres running locally on your machine after you're finished working with Alexandria and you may not want or need that. If you still want to run Postgres locally (and not involve Docker), then read on.

The first thing you'll need to do is install a new version of PostgreSQL that works for your operating system. After that's done, there's a little bit of setup that needs to happen.

Run the following commands in your new shell to configure the database:

!!!warning Hey! Listen! :sparkles:
Make sure to end every command with a semicolon (`;`) AND press Enter when you're done to execute the command. The shell will print out the name of the command that you just ran (for example, after you run the first "CREATE DATABASE" command, it should print "CREATE") back into the console. That's how you know the command just ran. If you don't see that line, try typing a semicolon and pressing enter again; usually that line terminator just got misplaced.
!!!

Install the `pg_trgm` extension on the default template database with the following command:

```shell
psql -h localhost -U postgres -d template1 -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'
```

This will make it so that the extension is always available, even for tests. Note: if this fails, you need to install `postgresql-contrib`. **`pg_trgm` is NOT optional**.

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

Run the following commands to create the database information needed by Alexandria:

```sql
-- After you get pg_trgm installed, you can build the rest:
CREATE DATABASE alexandria;
CREATE DATABASE queue;
CREATE USER alexandria WITH SUPERUSER PASSWORD 'asdf';
GRANT ALL ON DATABASE alexandria TO alexandria;
GRANT ALL ON DATABASE queue TO alexandria;
```

If everything ran correctly, you should see the following responses to your commands:

```shell
CREATE
CREATE
CREATE
CREATE
GRANT
GRANT
```

After that's done, go ahead and run `make db_setup` -- that should try to connect to the db and verify that everything's working. If the command finishes, then Alexandria can talk to your install!

Run `make migrate` to push the db schema and then finally `make run` to start Alexandria -- at this point you're off to the races!

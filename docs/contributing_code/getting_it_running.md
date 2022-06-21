---
order: 100
icon: codespaces
tags: [dev, development]
---
# Getting It Running

## Introduction

In this page, you will use the tooling you installed [from the previous page](environment_setup.md) to get Alexandria and its dependencies installed on your computer.

## Prerequisites

[!ref](environment_setup.md)

* SSH authentication configured with GitHub ([See here for instructions.](https://docs.github.com/en/authentication/connecting-to-github-with-ssh))
* A text / code editor (don't have one? [VS Code is a great place to start!](https://code.visualstudio.com/download))

## The App

We'll start by cloning the repository to your machine in your home directory.

```shell
cd ~
git clone git@github.com:AlexandriaILS/Alexandria.git
```

Once that completes, `cd` (change directory) into the new folder:

```shell
cd Alexandria
```

Now we're inside the project directory. Since we installed Poetry earlier, we can use it to install the dependencies for Alexandria. This will take a minute or two.

```shell
poetry install
```

Activate our new Python environment:

```shell
poetry shell
```

Create a new file here called `local_settings.py` -- you'll use this to override any settings you need while working on Alexandria. More on that later!

```shell
touch local_settings.py
```

Open the file in your preferred editor and paste the following lines into it as your starting point:

:::code source="../../local_settings.py" :::

Any setting specified here will override the setting in `alexandria/settings/base.py` without having to change anything in that file! It's a great way to test whatever you want without having to worry about undoing your changes.

## The Database

Alexandria requires [PostgreSQL](https://en.wikipedia.org/wiki/PostgreSQL), a free and open source database, to function. We rely heavily on the fantastic features provided, so you will need to have an instance of Postgres running before you can bring up Alexandria locally. We use Docker to make it easily accessible and controllable.

!!!warning
Before continuing, make sure you can access docker by running `docker version` (without sudo!). It should print out two sections: one about the Client and one about the Server. If you only see the block about the Client and you get an error about the Server section (usually something like "cannot connect to docker client -- is it running?") then check the following:

* make sure the server is running
* if `sudo docker version` works, you need to fix your permissions (see below)

==- Starting the Server (Ubuntu / WSL2 + MacOS)
#### WSL2

WSL2, despite running Ubuntu, still runs a _version_ of Ubuntu, and this is one of the times that it differs from the full OS. Start the server by running:

```shell
sudo service docker start
```

You should get something like the following as a response:

```shell Result:
❯ sudo service docker start
 * Starting Docker: docker     [ OK ]
```

#### Ubuntu

Start it by running the following command:

```shell
sudo systemctl start docker
```

#### MacOS

Docker is controlled through Docker Desktop for Mac, so if it's currently running, close the software. Then start the program again from Applications.

===

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

```shell Result:
❯ groups
joe adm dialout cdrom floppy sudo audio dip video plugdev netdev docker
```

===
!!!

All the initial setup commands are built into the `Makefile`, so download and start the Postgres Docker image:

```shell
make db_up
```

Once it finishes, set up the database by running the configuration command:

```shell
make db_setup
```

Now that it's set up, write our database schema to it by running:

```shell
make migrate
```

!!!
Get a notice about not being able to import Django? Make sure that you've run `poetry shell` and that you've installed the dependencies first!
!!!

Since we're doing this for development purposes, now the database is ready for writing actual data. Alexandria includes all 67,000 titles currently on [Project Gutenberg](https://www.gutenberg.org/) and we use these titles as our test data. Run the below command to import all the data:

```shell
make dev_data
```

Congratulations! You now have a local copy of Alexandria and a running database ready to interact with! Go to the next page to learn how to interact with your new install.

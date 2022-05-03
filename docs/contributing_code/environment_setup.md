---
order: 1000
icon: desktop-download
tags: [dev, development]
---
# Environment Setup

## Introduction
In order to work on Alexandria, you will need to set up your local environment. In this page, you will install and configure `pyenv`, Python, and Poetry, the three tools you need to work on Alexandria on your computer.

!!!danger For Microsoft Windows Users
Alexandria uses several features that are not available on Windows. If you are using a Windows computer, you will need to [install and configure WSL2](https://docs.microsoft.com/en-us/windows/wsl/install) to get a version of Ubuntu Linux working on your machine. You won't be able to work on / use Alexandria normally without it, so go ahead and get that installed and working before continuing. All commands shown will need to be run inside WSL2.

If your computer is running MacOS or Linux as its operating system (these docs assume Ubuntu / Debian Linux) then you're already good to go. Any other version of Linux is probably fine as well, but it's up to you to translate the requirements to your distro.
!!!

## Prerequisites

* A computer running MacOS, Ubuntu, or Windows with WSL2 (Ubuntu)
* Docker as configured by [following steps one and two from this tutorial for Ubuntu 22.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04) or by [following this tutorial for MacOS](https://docs.docker.com/desktop/mac/install/)
* If you're on MacOS, you will need [homebrew](https://brew.sh/) to install some of the dependencies

Can't use Docker? [!ref](install_psql_locally.md)

## Installing Pyenv and Python

### Pyenv

Most computers already have Python installed, but we want to make sure that we're using the proper version and modifying the version that comes with your computer can cause serious unexpected problems. To get around that, we recommend using `pyenv`, a version manager for Python.

In your terminal application, start by installing some prerequisite packages which will allow the next steps to run.

#### Ubuntu / WSL2

```shell
sudo apt update; sudo apt install git make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

#### MacOS
```shell
xcode-select --install  # installs the command line tools for Mac
brew install openssl readline sqlite3 xz zlib
```

Now you'll install `pyenv` and ensure that it's working.

```shell
curl https://pyenv.run | bash
```

Now that it's installed, restart your terminal shell (the command line interface) so that it picks up the changes:

```shell
exec $SHELL
```

!!!
Want to know more or run into issues? [Take a look at the `pyenv-installer` documentation here](https://github.com/pyenv/pyenv-installer)!
!!!

Check to make sure that your shell has `pyenv` installed and active:

```shell
pyenv --version
```

You should see something like this, although the version number will likely be different:

```shell Result:
❯ pyenv --version
pyenv 2.2.4-1-6-g44db3b03
```

### Python

Now that `pyenv` is installed, we can safely install any version of Python we want without worry and can also easily change versions later if we need to.

List all the versions of Python available by running the following in your terminal -- be warned that there will be a lot of results!

```shell
pyenv install --list
```

Scroll up in the list until you find lines that are just numbers -- they'll look like this:

```shell Result:
  ...
  3.9.12
  3.10.0
  3.10-dev
  3.10.1
  3.10.2
  3.10.3
  3.10.4
  3.11.0a7
  3.11-dev
  ...
```

Make a note of the version that is the highest number **without** letters or hyphens in it. At the time of this writing, the highest number is `3.10.4`.

Install that version of Python with `pyenv` with the following command:

```shell
pyenv install 3.10.4  # replace the number here with the number you have!
```

This will take a little bit. Stretch your limbs and grab some water while we wait for that to run :smile:

Alright! Now that it's installed, we'll set it as the default version for your computer -- don't worry, your system version of Python (if you have one) isn't going anywhere -- this will just change which version of Python is run when you just ask for "python" instead of a specific version.

First we'll check to make sure it's installed and visible:

```shell
pyenv versions
```

You should see something like this (again, with the version that you just installed instead of my version):

```shell Result:
❯ pyenv versions
* system (set by /home/tester/.pyenv/version)
  3.10.4
```

See that asterisk next to `system`? That means that the version of Python that's currently installed is set as the default. We'll change that now to your version:

```shell
pyenv global 3.10.4  # replace with your version number!
```

Now you should be done -- check the version of Python that your shell gets by running:

```shell
python --version
```

It should return something like this:

```shell Result:
❯ python --version
Python 3.10.4
```

## Poetry

Alexandria (and the other applications that surround it) uses Poetry as its dependency manager. We'll install it now.

```shell
curl -sSL https://install.python-poetry.org | python -
```

Because we installed the latest version of Python 3 above and set it to the global version with `pyenv`, Poetry will install automatically using the version we just installed.

Now we need to tell your shell how to find it. Because there many different terminal shells that you might be running, the shell that you have determines how we do the next step. To find out what shell you have, run:

```shell
basename $SHELL
```

It should print out the name of the shell you're using now. Mine may be different than yours, but the output should look like this:

```shell Result:
❯ basename $SHELL
zsh
```

...so the shell that I'm running (and, most likely, you as well) is `zsh`. Once you've identified your shell, you can tell it where to find Poetry:

```shell
# zsh
echo 'export PATH=$HOME/.poetry/bin:$PATH' >> ~/.zshrc

# bash
echo 'export PATH=$HOME/.poetry/bin:$PATH' >> ~/.bashrc
```

If your shell is different from one of the two listed above (like `fish`) then you will likely know where to add the PATH addition.

Restart your shell again by running:

```shell
exec $SHELL
```

Verify that Poetry can be found by asking for its version:

```shell
poetry --version
```

Though the version number may be different, you should see something like the following:

```shell Result:
❯ poetry --version
Poetry version 1.1.13
```

Congrats, you've installed `pyenv`, the latest version of Python, and Poetry; you're ready to set up Alexandria!

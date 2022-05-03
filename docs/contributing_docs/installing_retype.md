---
order: 100
icon: checklist
tags: [docs, documentation, retype, npm, nvm, node, nodejs]
---
# Installing Retype
## Introduction

Our documentation is [powered by Retype](https://retype.com), a Javascript-based documentation generator. In this page, you will install Node Version Manager (`nvm`), NodeJS and NPM, and finally Retype.

## Prerequisites

* A desire to write great documentation!

## Installing NodeJS + NPM

We use a Javascript package called Retype to generate our documentation from [markdown files](https://www.markdownguide.org/getting-started/) located in the `docs` folder. In order to install Retype, we need to install `nvm` and NPM first.

Because NPM can be... tricky at best, we use `nvm` (Node Version Manager) to help us wrangle NodeJS and NPM. Install it with the following command:

```shell
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
```

_Note: This may be out of date. [Verify that this is the current version here](https://github.com/nvm-sh/nvm#install--update-script)._

Restart your shell so we can use the new changes:

```shell
exec $SHELL
```

Verify that `nvm` is available and can be called:

```shell
nvm --version
```

You should see something like the following:

```shell Result:
❯ nvm --version
0.39.1
```

Now that `nvm` is installed and accessible, install the latest version of NodeJS by running the following command:

```shell
nvm install node
```

!!! success
Close your terminal and open a new terminal window to completely reset it.
!!!

Congrats! :tada: NodeJS is now installed and we're ready to install and use Retype.

## Installing Retype

To install Retype, run the following command:

```shell
npm install -g retypeapp
```

After this completes, it should be immediately available for use. Verify by checking the version:

```shell
retype --version
```

You should see something like this:

```shell Result:
❯ retype --version
2.2.0
```

## Running the Docs Server

Now that Retype is installed, you can run the Retype local server to compile the documentation and test it locally so that you can check your changes in real time:

```shell
make docs
```

The compiled and hosted documentation is available at [http://localhost:5000/Alexandria/](http://localhost:5000/Alexandria/). The page will automatically reload when you save any `.md` file in the docs folder.

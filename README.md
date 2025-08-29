# ksvotes (v3)

[![Build Status](https://github.com/BlueprintKansas/v3.ksvotes.org/actions/workflows/pull_request.yml/badge.svg)](https://github.com/BlueprintKansas/v3.ksvotes.org)

## Overview

A Django implementation of ksvotes.org.

## Local Development Setup

This project uses Python 3.10.x, Node 14.x or newer (we suggest using [pyenv](https://github.com/pyenv/pyenv)), Docker, and Docker Compose.

Make a Python 3.10.x (or newer) virtualenv (we suggest using [nvm](https://github.com/nvm-sh/nvm)).

```shell
$ python3 -m venv venv
$ . venv/bin/activate
```

Copy .env-dist to .env and adjust values to match your local environment:

```shell
$ cp .env-dist .env
```

Then run:

```shell
# install dev dependencies
$ make dev-setup
# browser test dependencies
$ playwright install --with-deps
# rebuild our services
$ make setup

# interactive bash shell in web container
$ make console
    # start the server (once in the console)
    root@randomdockerstring:/app# make run

# start our services with daemon mode
# for interative development, probably instead use $ make console (see above)
$ make server

# see all make targets available
$ make

```

### Cleaning up

To shut down our database and any long running services, we shut everyone down using:

```shell
$ make services-stop
```


## Running the tests

To run the tests, execute:

```shell
$ make test

```

## Deploying

Deploy via the Github Action menu, or via the Heroku web UI, or via the command line with `make deploy-stage` and/or `make deploy-prod`.

Note that deploying via `make` likely requires you run `heroku login` first.

## Production Environment Considerations

TDB

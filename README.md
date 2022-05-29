# ksvotes (v3)

## Overview

A Django implementation of ksvotes.org.

## Local Development Setup

This project uses Python 3.10.x, Node 14.x or newer, Docker, and Docker Compose.

Make a Python 3.9.x (or newer) virtualenv.

```shell
$ python3 -m venv venv
$ . venv/bin/activate
```

Copy .env-dist to .env and adjust values to match your local environment:

```shell
$ cp .env-dist .env
$ cp docker-compose.override.yml-dist docker-compose.override.yml
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

# start our services with daemon mode
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

TDB

## Production Environment Considerations

TDB

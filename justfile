set dotenv-load := false

@_default:
    just --list

# ----
# Research:
# - https://www.encode.io/reports/april-2020#our-workflow-approach
# - https://github.blog/2015-06-30-scripts-to-rule-them-all/
# ----

bootstrap:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ ! -f ".env" ]; then
        echo ".env created"
        cp .env-dist .env
    fi

    # if [ ! -f "docker-compose.override.yml" ]; then
    #     echo "docker-compose.override.yml created"
    #     cp docker-compose.override.yml-dist docker-compose.override.yml
    # fi

    # docker-compose build --force-rm

@cibuild:
    python -m pytest
    python -m black --check .
    interrogate -c pyproject.toml .

@console:
    docker-compose run --rm web bash

@server:
    docker-compose run --rm web python manage.py migrate --noinput
    docker-compose up

@setup:
    docker-compose build --force-rm
    docker-compose run --rm web python manage.py migrate --noinput

@test_interrogate:
    docker-compose run --rm web interrogate -vv --fail-under 100 --whitelist-regex "test_.*" .

@test_pytest +ARGS="":
    -docker-compose run --rm web pytest -s {{ ARGS }}

@test +ARGS="":
    just test_pytest {{ ARGS }}
    just test_interrogate
    docker-compose down

@update:
    docker-compose rm --force web
    docker-compose pull
    docker-compose build --force-rm
    docker-compose run --rm web python manage.py migrate --noinput

# ----

@fmt:
    just --fmt --unstable

@pip-compile:
    docker-compose run --rm web \
        bash -c "pip install --upgrade --requirement ./requirements.in && \
            rm -rf ./requirements.txt && \
            pip-compile ./requirements.in --output-file ./requirements.txt"

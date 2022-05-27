COMPOSE_FILE := docker-compose.yml

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

# ----
# Research:
# - https://www.encode.io/reports/april-2020#our-workflow-approach
# - https://github.blog/2015-06-30-scripts-to-rule-them-all/
# ----

.PHONY: bootstrap
bootstrap:  ## installs/updates all dependencies
	@docker-compose --file $(COMPOSE_FILE) build --force-rm

.PHONY: cibuild
cibuild:  ## invoked by continuous integration servers to run tests
	@python -m pytest
	@python -m black --check .
	@interrogate -c pyproject.toml .

.PHONY: console
console:  ## opens a console
	@docker-compose run -p 8000:8000 -v $(PWD):/code --rm web bash

.PHONY: server
server:  ## starts app
	@docker-compose --file docker-compose.yml run --rm web python manage.py migrate --noinput
	@docker-compose up

.PHONY: setup
setup: ## sets up a project to be used for the first time
	@docker-compose --file $(COMPOSE_FILE) build --force-rm
	@docker-compose --file docker-compose.yml run --rm web python manage.py migrate --noinput

.PHONY: dev-setup
dev-setup: ## install local development dependencies
	pip install -U pre-commit black
	pip install -r requirements-ci.txt
	npm install

.PHONY: test_interrogate
test_interrogate:
	@docker-compose run --rm web interrogate -vv --fail-under 100 --whitelist-regex "test_.*" --exclude "node_modules" .

.PHONY: test_pytest
test_pytest:
	@docker-compose run --rm web make coverage

.PHONY: test
test: test_interrogate test_pytest

.PHONY: update
update:  ## updates a project to run at its current version
	@docker-compose --file $(COMPOSE_FILE) rm --force celery
	@docker-compose --file $(COMPOSE_FILE) rm --force celery-beat
	@docker-compose --file $(COMPOSE_FILE) rm --force web
	@docker-compose --file $(COMPOSE_FILE) pull
	@docker-compose --file $(COMPOSE_FILE) build --force-rm
	@docker-compose --file docker-compose.yml run --rm web python manage.py migrate --noinput

.PHONY: lint
lint: ## run the pre-commit linters manually
	pre-commit run --all-files
	black .

.PHONY: ci-logs
ci-logs: ## view all the docker-compose logs
	@docker-compose --file $(COMPOSE_FILE) logs --tail="all"

.PHONY: ci-logs-tail
ci-logs-tail: ## tail the docker-compose logs
	@docker-compose --file $(COMPOSE_FILE) logs -f

.PHONY: css
css: ## Build css artifacts from scss (
	npm run css

.PHONY: playwright
playwright: ## Run playwrite tests
	pytest -s -vv --noconftest -c /dev/null --base-url=http://test.ksvotes.org:8000 playwright/


# ----

.PHONY: pip-compile
pip-compile:  ## rebuilds our pip requirements
	pip-compile ./requirements.in --output-file ./requirements.txt

# targets intended to be run *inside* a container
.PHONY: run
run:
	DJANGO_READ_DOT_ENV_FILE=true python manage.py runserver 0:8000

.PHONY: locales
locales: ## Build i18n files (inside container)
	rm -f ksvotes/locale/*/*/*o
	python manage.py build_locales
	python manage.py compilemessages

.PHONY: coverage
coverage: ## Run Django tests with coverage (inside container)
	pytest -s --cov=ksvotes --cov-report=term-missing:skip-covered --cov-fail-under=90

.PHONY: services-stop
services-stop:
	docker-compose down

.PHONY: fernet-key
fernet-key: ## Create Fernet encrypt key and echo to stdout
	dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64

.PHONY: fixtures
fixtures: ## Load fixtures (inside container)
	python manage.py load_clerks
	python manage.py load_zipcodes
	python manage.py load_demo

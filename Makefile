COMPOSE_FILE := docker-compose.yml

.PHONY: help
help: ## View this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

# ----
# Research:
# - https://www.encode.io/reports/april-2020#our-workflow-approach
# - https://github.blog/2015-06-30-scripts-to-rule-them-all/
# ----

.PHONY: bootstrap
bootstrap:  ## installs/updates all dependencies
	@docker-compose --file $(COMPOSE_FILE) build --force-rm

.PHONY: console
console:  ## opens a console
	@docker-compose run -p 8000:8000 -v $(PWD):/code --rm web bash

.PHONY: server
server:  ## starts app
	@docker-compose --file $(COMPOSE_FILE) run --rm web python manage.py migrate --noinput
	@docker-compose up

.PHONY: setup
setup: bootstrap ## sets up a project to be used for the first time
	docker-compose --file $(COMPOSE_FILE) run --rm web make migrate

.PHONY: dev-setup
dev-setup: ## install local development dependencies
	pip install -U pre-commit black
	pip install -r requirements-ci.txt
	npm install

.PHONY: test_pytest
test_pytest: ## Run coverage tests
	@docker-compose run --rm web make coverage

.PHONY: test
test: test_pytest

.PHONY: update
update:  ## updates a project to run at its current version
	@docker-compose --file $(COMPOSE_FILE) rm --force web
	@docker-compose --file $(COMPOSE_FILE) pull
	@docker-compose --file $(COMPOSE_FILE) build --force-rm
	@docker-compose --file $(COMPOSE_FILE) run --rm web make migrate

.PHONY: lint
lint: ## run the pre-commit linters manually
	pre-commit run --all-files
	black .

.PHONY: ci-start
ci-start: ## start CI services
	docker-compose up -d

.PHONY: ci-stop
ci-stop: ## Stop CI services
	@docker-compose --file $(COMPOSE_FILE) down

.PHONY: ci-logs
ci-logs: ## view all the docker-compose logs
	@docker-compose --file $(COMPOSE_FILE) logs --tail="all"

.PHONY: ci-logs-tail
ci-logs-tail: ## tail the docker-compose logs
	@docker-compose --file $(COMPOSE_FILE) logs -f

DOCKER_IMG=ksvotes:v3ksvotesorg-web
DOCKER_NAME=ksvotes-v3-web
ifeq (, $(shell which docker))
DOCKER_CONTAINER_ID := docker-is-not-installed
else
DOCKER_CONTAINER_ID := $(shell docker ps --filter ancestor=$(DOCKER_IMG) --format "{{.ID}}" -a)
endif

.PHONY: attach
attach: ## Attach to a running container and open a shell (like login for running container)
	docker exec -it $(DOCKER_CONTAINER_ID) /bin/bash

.PHONY: ci-test
ci-test: ## run CI tests
	ENV_NAME=ci docker-compose exec -T web /code/run-ci-tests.sh

.PHONY: css
css: ## Build css artifacts from scss
	npm run css

.PHONY: playwright
playwright: ## Run playwrite tests
	pytest -s -vv --noconftest -c /dev/null --base-url=http://test.ksvotes.org:8000 playwright/

.PHONY: pip-compile
pip-compile:  ## rebuilds our pip requirements
	pip-compile ./requirements.in --output-file ./requirements.txt

.PHONY: fernet-key
fernet-key: ## Create Fernet encrypt key and echo to stdout
	dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64

.PHONY: deploy-prod
deploy-prod: ## Deploy to production
	heroku container:push web --app ksvotes-v3
	heroku container:release web --app ksvotes-v3

##################################################
# targets intended to be run *inside* a container
.PHONY: run
run: ## Run django dev server (inside container)
	DJANGO_READ_DOT_ENV_FILE=true python manage.py runserver 0:8000

.PHONY: locales
locales: ## Build i18n files (inside container)
	python manage.py build_locales
	python manage.py compilemessages

.PHONY: coverage
coverage: ## Run Django tests with coverage (inside container)
	pytest -s --cov=ksvotes --cov-report=term-missing:skip-covered --cov-fail-under=90

.PHONY: services-stop
services-stop: ## stop dev services
	docker-compose down

.PHONY: fixtures
fixtures: ## Load fixtures (inside container)
	python manage.py load_clerks
	python manage.py load_zipcodes
	python manage.py load_demo

v2-patch:
	perl -pi -e 's/\{phone\}\\n/{phone}/g' ksvotes/translations.json

DATABASE_HOST := $(shell echo $${DATABASE_URL:-db} | perl -n -e 's,.+@,,; s,:5432/.+,,; print' )
.PHONY: migrate
migrate: ## Run db migrations (inside container)
	wait-for-it -h $(DATABASE_HOST) -p 5432 -t 20
	python manage.py migrate --noinput

.PHONY: static
static: ## Build static assets (inside container)
	python manage.py collectstatic --noinput

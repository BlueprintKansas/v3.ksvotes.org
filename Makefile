COMPOSE_FILE := docker-compose.yml
DOCKER_IMG=ksvotes:v3ksvotesorg-web
DOCKER_NAME=ksvotes-v3-web
ifeq (, $(shell which docker))
DOCKER_CONTAINER_ID := docker-is-not-installed
else
DOCKER_CONTAINER_ID := $(shell docker ps --filter ancestor=$(DOCKER_IMG) --format "{{.ID}}")
endif

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
	@docker compose --file $(COMPOSE_FILE) build --force-rm

.PHONY: console
console:  ## opens a one-off console -- see attach for connecting to running container
	@docker run -p 8000:8000 -v $(PWD):/code \
   -e DJANGO_READ_DOT_ENV_FILE=true \
   --network v3ksvotesorg_default \
   --rm --name ksvotes-web-console -it \
   $(DOCKER_IMG) bash
	@docker rm ksvotes-web-console

.PHONY: server
server:  ## starts app
	@docker compose --file $(COMPOSE_FILE) run --rm web python manage.py migrate --noinput
	@docker compose up

.PHONY: start
start: services-start ## Alias for make services-start

.PHONY: setup
setup: bootstrap ## sets up a project to be used for the first time
	docker compose --file $(COMPOSE_FILE) run --rm web make migrate

.PHONY: dev-setup
dev-setup: ## install local development dependencies
	pip install -U pre-commit black pip-tools
	pip install -r requirements-ci.txt
	npm install

.PHONY: test_pytest
test_pytest: ## Run coverage tests
	@docker compose run --rm web make coverage

.PHONY: test
test: test_pytest

.PHONY: update
update:  ## updates a project to run at its current version
	docker compose --file $(COMPOSE_FILE) rm --force web
	docker compose --file $(COMPOSE_FILE) pull
	docker compose --file $(COMPOSE_FILE) build --force-rm
	docker compose --file $(COMPOSE_FILE) run --rm web make migrate

.PHONY: lint
lint: ## run the pre-commit linters manually
	pre-commit run --all-files
	black .

.PHONY: ci-start
ci-start: ## start CI services
	docker compose up -d

.PHONY: ci-stop
ci-stop: ## Stop CI services
	@docker compose --file $(COMPOSE_FILE) down

.PHONY: ci-logs
ci-logs: ## view all the docker compose logs
	@docker compose --file $(COMPOSE_FILE) logs --tail="all"

.PHONY: ci-logs-tail
ci-logs-tail: ## tail the docker compose logs
	@docker compose --file $(COMPOSE_FILE) logs -f

.PHONY: attach
attach: ## Attach to a running container and open a shell (like console for running container)
	docker exec -it $(DOCKER_CONTAINER_ID) /bin/bash

.PHONY: login
login: attach ## Alias for make attach

.PHONY: ci-test
ci-test: ## run CI tests
	ENV_NAME=ci docker compose exec -T web /code/run-ci-tests.sh

.PHONY: css
css: ## Build css artifacts from scss
	npm run css

.PHONY: playwright
playwright: ## Run playwrite tests
	python -m pytest -s -vv --noconftest -c /dev/null --base-url=http://test.ksvotes.org:8000 playwright/

.PHONY: pip-compile
pip-compile:  ## rebuilds our pip requirements
	pip-compile requirements.in --output-file ./requirements.txt

.PHONY: fernet-key
fernet-key: ## Create Fernet encrypt key and echo to stdout
	dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64

.PHONY: deploy-prod
deploy-prod: ## Deploy to production
	heroku container:login
	heroku container:push web --app ksvotes-v3
	heroku container:release web --app ksvotes-v3

.PHONY: deploy-stage
deploy-stage:  ## Deploy to stage
	heroku container:login
	heroku container:push web --app ksvotes-staging
	heroku container:release web --app ksvotes-staging

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
	pytest -s --cov=ksvotes --cov-report=term-missing:skip-covered --cov-fail-under=90 --create-db

.PHONY: services-stop
services-stop: ## stop dev services
	docker compose down

.PHONY: stop
stop: services-stop ## Alias for make services-stop

.PHONY: services-start
services-start:
	docker compose up db redis

.PHONY: fixtures
fixtures: ## Load fixtures (inside container)
	DJANGO_DEBUG=0 python manage.py load_clerks
	DJANGO_DEBUG=0 make early-voting-locations
	python manage.py load_demo

.PHONY: zipcodes
zipcodes:
	python manage.py load_zipcodes

.PHONY: early-voting-locations
early-voting-locations:
	python manage.py load_early_voting_locations

v2-patch:
	perl -pi -e 's/\{phone\}\\n/{phone}/g' ksvotes/translations.json

DATABASE_HOST := $(shell echo $${DATABASE_URL:-db} | perl -n -e 's,.+@,,; s,:5432/.+,,; print' )
.PHONY: migrate
migrate: ## Run db migrations (inside container)
	wait-for-it -h $(DATABASE_HOST) -p 5432 -t 20
	python manage.py migrate --noinput

.PHONY: migrations
migrations:
	python manage.py makemigrations ksvotes

.PHONY: static
static: ## Build static assets (inside container)
	python manage.py collectstatic --noinput

.PHONY: shell
shell: ## Open django python shell
	python manage.py shell

.PHONY: export
export: ## Export registrants, decrypted, in CSV format
ifeq ($(SINCE),)
	python manage.py export_registrants
else
	python manage.py export_registrants --since $(SINCE)
endif

.PHONY: redact
redact: ## Remove sensitive PII older than OLDER days (default 2)
ifeq ($(OLDER),)
	python manage.py redact_registrants
else
	python manage.py redact_registrants --older $(OLDER)
endif

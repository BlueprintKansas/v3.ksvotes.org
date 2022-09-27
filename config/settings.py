# -*- coding: utf-8 -*-
import environs
import logging
import logging.config
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path

env = environs.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env.read_env()
    print("The .env file has been loaded. See config/settings.py for more information")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=False)

# tie together multiple log lines with a common id
REQUEST_ID_CONFIG = {
    "REQUEST_ID_HEADER": "HTTP_X_REQUEST_ID",
    "GENERATE_REQUEST_ID_IF_NOT_FOUND": True,
    "RESPONSE_HEADER_REQUEST_ID": "HTTP_X_REQUEST_ID",
}

# Configure Python logging
LOG_LEVEL = env.str("LOG_LEVEL", default="INFO")
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
LOGGING_CONFIG = None  # This empties out Django's logging config
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "request_id_django_log.filters.RequestIDFilter"}},
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",  # colored output
            # --> %(log_color)s is very important, that's what colors the line
            "format": "%(log_color)s[%(levelname)s] %(reset)s %(green)s[%(request_id)s] %(reset)s%(blue)s%(name)s - %(asctime)s :: %(reset)s %(message)s",
            "log_colors": {
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "verbose": {
            "format": "[%(levelname)s] [%(request_id)s] %(name)s - %(asctime)s :: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": ("DEBUG" if DEBUG else LOG_LEVEL),
            "class": "colorlog.StreamHandler",
            "formatter": (
                "colored" if env.bool("COLOR_LOGGING", default=False) else "verbose"
            ),
            "filters": ["request_id"],
        },
    },
    "loggers": {
        "django.utils.autoreload": {"level": LOG_LEVEL},
        "django": {
            "handlers": ["console"],
            "level": logging.DEBUG if DEBUG else LOG_LEVEL,
            "propagate": False,
        },
        "": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
    },
}
logging.config.dictConfig(LOGGING)  # Finally replace our config in python logging

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent.parent
APPS_DIR = BASE_DIR.joinpath("config")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")


host_list = env.list("ALLOWED_HOSTS", default="localhost")
ALLOWED_HOSTS = [el.strip() for el in host_list]
CSRF_TRUSTED_ORIGINS = [f"https://{el.strip()}" for el in host_list]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "request_id_django_log",
    "whitenoise.runserver_nostatic",
]

# Third-party apps
INSTALLED_APPS += [
    "rest_framework",
    "django_extensions",
    #    "health_check",
    #    "health_check.db",
    #    "health_check.contrib.celery",
]

# Our Apps
INSTALLED_APPS += ["ak", "ksvotes", "users"]

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "ksvotes.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "request_id_django_log.middleware.RequestIdDjangoLog",
    "ksvotes.middleware.session.SessionTimeout",
]

if env.bool("REQUIRE_SSL", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True

if DEBUG:
    # These are necessary to turn on Whitenoise which will serve our static
    # files while doing local development
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR.joinpath("ksvotes", "templates").as_posix(),
            BASE_DIR.joinpath("templates").as_posix(),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.base_url",
                "config.context_processors.common_vars",
                "ksvotes.context_processors.steps",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

try:
    DATABASES = {"default": env.dj_db_url("DATABASE_URL")}
except (ImproperlyConfigured, environs.EnvError):
    DATABASES = {
        "default": {
            "ENGINE": "django_db_geventpool.backends.postgresql_psycopg2",
            "HOST": env("PGHOST"),
            "NAME": env("PGDATABASE"),
            "PASSWORD": env("PGPASSWORD"),
            "PORT": env.int("PGPORT", default=5432),
            "USER": env("PGUSER"),
            "CONN_MAX_AGE": 0,
            "OPTIONS": {"MAX_CONNS": 100},
        }
    }

# Password validation
# Only used in production
AUTH_PASSWORD_VALIDATORS = []

# Sessions

# Give each project their own session cookie name to avoid local development
# login conflicts
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_NAME = "ksvotes-sessionid"
SESSION_TTL = env.int("SESSION_TTL", 60 * 5)
SESSION_COOKIE_AGE = SESSION_TTL
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_USE_SESSIONS = True

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# The relative URL of where we serve our static files from
STATIC_URL = "/static/"

# Additional directories from where we should collect static files from
STATICFILES_DIRS = [BASE_DIR.joinpath("static").as_posix()]

# This is the directory where all of the collected static files are put
# after running collectstatic
STATIC_ROOT = BASE_DIR.joinpath("deployed_static").as_posix()

# Default auto keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Configure Redis
REDIS_DB = 0
REDIS_HOST = env("REDIS_HOST", default="redis")
REDIS_URL = env("REDIS_URL", default=f"redis://{REDIS_HOST}:6379/{REDIS_DB}")
redis_options = {}
heroku_redis_options = {
    "ssl_cert_reqs": None,
}
if env("REDIS_TLS_URL", None):
    REDIS_URL = env("REDIS_TLS_URL")  # prefer ssl
    redis_options = heroku_redis_options
elif REDIS_URL.startswith("rediss://"):
    print("REDIS_URL startswith rediss://")
    redis_options = heroku_redis_options

print("redis options: {}".format(redis_options))
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "ksvotes-session",
        # expire in 30 minutes after last activity - TODO this might be ignored by session ttl logic
        "TIMEOUT": 60 * 30,
        "OPTIONS": redis_options,
    },
}

# ksvotes
APP_CONFIG = env("APP_CONFIG", default="development")
GA_KEY = env("GA_KEY", default=None)
EMAIL_FROM = env("EMAIL_FROM", "noreply@ksvotes.org")
EMAIL_BCC = env("EMAIL_BCC", "registration@ksvotes.org")
AWS_DEFAULT_REGION = env("AWS_DEFAULT_REGION", "us-east-1")
SES_ACCESS_KEY_ID = env("SES_ACCESS_KEY_ID", default=None)
SES_SECRET_ACCESS_KEY = env("SES_SECRET_ACCESS_KEY", default=None)
SEND_EMAIL = env.bool("SEND_EMAIL", default=False)
DEMO_UUID = env("DEMO_UUID", default=None)
ENABLE_AB = env.bool("ENABLE_AB", default=False)
ENABLE_AB_TRACKER = env.bool("ENABLE_AB_TRACKER", default=False)
ENABLE_VOTING_LOCATION = env.bool("ENABLE_VOTING_LOCATION", default=False)
FAIL_EMAIL = env("FAIL_EMAIL", default="fail@ksvotes.org")
STAGE_BANNER = env.bool("STAGE_BANNER", default=False)

# registrants.registration encryption
FERNET_KEYS = env.list("FERNET_KEYS")

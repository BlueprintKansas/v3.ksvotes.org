FROM revolutionsystems/python:3.10.8-wee-optimized-lto as ksvotes

# build ImageMagick with gslib for formfiller
USER root

# match postgresql-client-xx with docker-compose server version
# https://stackoverflow.com/a/66325795
RUN apt-get update && apt-get install -y gnupg dirmngr curl
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN curl -s https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update && apt-get install --yes --no-install-recommends nginx xz-utils build-essential \
      gettext postgresql-client-14 libpq-dev libffi-dev libgs-dev ghostscript fonts-liberation imagemagick wait-for-it \
      openssh-server iproute2

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements*txt ./
RUN pip install -U pip pip-tools
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY . /code/

# configure nginx
# heroku will inject PORT env at run time. this is our default when not at heroku.
ENV PORT=8000
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# bash for heroku ps:exec
RUN rm /bin/sh \
 && ln -s /bin/bash /bin/sh \
 && mkdir -p /app/.profile.d/ \
 && printf '#!/usr/bin/env bash\n\nset +o posix\n\n[ -z "$SSH_CLIENT" ] && source <(curl --fail --retry 7 -sSL "$HEROKU_EXEC_URL")\n' > /app/.profile.d/heroku-exec.sh \
 && chmod +x /app/.profile.d/heroku-exec.sh

# finish with app user and app
RUN groupadd ksvotesapp && \
  useradd -g ksvotesapp ksvotesapp && \
  apt-get purge -y --auto-remove build-essential && \
  apt-get -y install make && \
  chown -R ksvotesapp:ksvotesapp /code /etc/nginx /var/lib/nginx /var/log/nginx

ARG ENV_NAME=""
ENV ENV_NAME=${ENV_NAME}
ARG GIT_SHA=""
ENV GIT_SHA=${GIT_SHA}

USER ksvotesapp
CMD ["/bin/bash", "/code/compose-start.sh"]


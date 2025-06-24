FROM revolutionsystems/python:3.10.18-wee-lto-optimized as ksvotes

# build ImageMagick with gslib for formfiller
USER root

RUN apt-get update && apt-get install -y gnupg dirmngr curl
RUN apt-get update && apt-get install --yes --no-install-recommends nginx xz-utils build-essential \
      gettext postgresql-client libpq-dev libffi-dev libgs-dev ghostscript fonts-liberation imagemagick wait-for-it \
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


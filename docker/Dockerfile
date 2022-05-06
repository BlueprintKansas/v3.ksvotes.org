FROM revolutionsystems/python:3.10.4-wee-optimized-lto as ksvotes

# build ImageMagick with gslib for formfiller
USER root

RUN apt-get update && \
    apt-get install --yes --no-install-recommends wget xz-utils build-essential \
      gettext postgresql-client libpq-dev libffi-dev libgs-dev ghostscript fonts-liberation imagemagick wait-for-it

WORKDIR /code

COPY requirements*txt .
RUN pip install -U pip pip-tools
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY . /code/

# RUN make locales

# finish with app user and app
RUN groupadd ksvotesapp && \
  useradd -g ksvotesapp ksvotesapp && \
  apt-get purge -y --auto-remove build-essential && \
  apt-get -y install make && \
  chown -R ksvotesapp:ksvotesapp /code

ARG ENV_NAME=""
ENV ENV_NAME=${ENV_NAME}
ARG GIT_SHA=""
ENV GIT_SHA=${GIT_SHA}

USER ksvotesapp
CMD ["gunicorn", "-c", "/code/gunicorn.conf.py", "config.wsgi"]


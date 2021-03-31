FROM python:3.5
LABEL maintainer "DataMade <info@datamade.us>"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gettext binutils libproj-dev gdal-bin postgresql-client \
        osm2pgsql curl

RUN mkdir /app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV DJANGO_SECRET_KEY 'super secret key'
ENV IMPORTER_USER_PASSWORD 'super secret password'
RUN python manage.py collectstatic --noinput

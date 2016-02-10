# Security Force Monitor: Backend

## Development

    mkvirtualenv sfm
    git clone git@github.com:caravancoop/sfm.git
    cd sfm/sfm_pc

Install the requirements:

    pip install -r requirements.txt

Create a database:

    createdb sfm-db
    python manage.py migrate --noinput

Edit the project's settings:

    cp sfm_pc/settings.py.template sfm_pc/settings.py
    # Edit the DATABASES variable.

Start the web server:

    python manage.py runserver

## Deployment

    heroku apps:create

[Generate a secret key in Python](https://github.com/django/django/blob/master/django/core/management/commands/startproject.py):

```python
from django.utils.crypto import get_random_string
get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
```

Add configuration variables (replace `<SECRET-KEY>`):

    heroku config:set DJANGO_SECRET_KEY=<SECRET-KEY>

You'll need a [production tier PostgreSQL database](https://devcenter.heroku.com/articles/postgis) to use PostGIS (replace `<DATABASE>`):

    heroku addons:add heroku-postgresql:standard-0
    heroku pg:wait
    heroku pg:promote <DATABASE>
    heroku addons:remove heroku-postgresql:dev
    heroku pg:psql

In the PostgreSQL shell, run:

    CREATE EXTENSION postgis;

You'll need the [geo](https://github.com/cyberdelia/heroku-geo-buildpack/) buildpack for GeoDjango:

    heroku config:add BUILDPACK_URL=https://github.com/ddollar/heroku-buildpack-multi.git

Setup the database:

    heroku run python manage.py migrate --noinput

Deploy:

    git push heroku master

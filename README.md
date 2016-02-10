# Security Force Monitor: Backend

## Development

    mkvirtualenv sfm
    git clone git@github.com:caravancoop/sfm.git
    cd sfm/sfm_pc

Install the requirements:

    pip install -r requirements.txt

Create a database:

    createdb sfm-db
    psql sfm-db -c "CREATE EXTENSION postgis;"
    export DATABASE_URL=postgis://localhost/sfm-db
    ./manage.py migrate --noinput

Create an admin user:

    ./manage.py createsuperuser

Start the web server:

    ./manage.py runserver

Open http://127.0.0.1:8000/ and sign in with your email and password.

## Deployment

    heroku apps:create

[Generate a secret key in Python](https://github.com/django/django/blob/master/django/core/management/commands/startproject.py):

```python
from django.utils.crypto import get_random_string
get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
```

Add configuration variables (replace `<SECRET-KEY>`):

    heroku config:set DJANGO_SECRET_KEY=<SECRET-KEY>

Add a [production tier PostgreSQL database](https://devcenter.heroku.com/articles/postgis) ($50/mo) to use PostGIS (replace `<DATABASE>`):

    heroku addons:create heroku-postgresql:standard-0
    heroku pg:wait
    heroku pg:psql

In the PostgreSQL shell, run:

    CREATE EXTENSION postgis;

To enable the [geo](https://github.com/cyberdelia/heroku-geo-buildpack/) buildpack for GeoDjango:

    heroku config:add BUILDPACK_URL=https://github.com/ddollar/heroku-buildpack-multi.git

Add this addon to access dependencies in private repositories:

    heroku addons:create gemfury:hello
    echo `heroku config:get GEMFURY_URL`

Deploy:

    git push heroku dev:master

Setup the database:

    heroku run python manage.py migrate --noinput

Create an admin user:

    heroku run python manage.py createsuperuser

Open the website:

    

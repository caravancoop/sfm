# Security Force Monitor: Backend

## OS Level dependencies

* Python 3.5
* PostgreSQL 9.4+ 
* PostGIS
* osm2pgsql

## Development

    mkvirtualenv sfm
    git clone git@github.com:security-force-monitor/sfm-cms.git
    cd sfm-cms

Install the requirements:

    pip install -r requirements.txt
    
Create a local settings file:

    cp sfm_pc/settings_local.py.example sfm_pc/settings_local.py
    # You can change some of the variables if you want, but it's not necessary to get the app running    

Create a database:

    createdb sfm-db
    psql sfm-db -c "CREATE EXTENSION postgis;"
    ./manage.py migrate --noinput

Load static data:

```
# Load fixtures for Violation Types, Organization classification types, and countries
./manage.py loaddata violation_types
./manage.py loaddata classification_types
./manage.py update_countries_plus
```

Create Materialized Views for global search, and looking up a Geoname object based upon a geoname id: 

    python manage.py import_osm
    python manage.py import_google_doc
    python manage.py make_flattened_views

You're almost done! The last step is to get solr and the search index setup. Start by following the instructions in [SOLR-SETUP.md](https://github.com/security-force-monitor/sfm-cms/blob/master/SOLR-SETUP.md) to get solr installed and running on your machine.

Then, create the search index: 

    python manage.py make_search_index

Create an admin user:

    ./manage.py createsuperuser

Start the web server:

    ./manage.py runserver

Open http://127.0.0.1:8000/ and sign in with your email and password.

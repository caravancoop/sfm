# Security Force Monitor: Backend [![Build Status](https://travis-ci.org/security-force-monitor/sfm-cms.svg?branch=master)](https://travis-ci.org/security-force-monitor/sfm-cms)

## OS Level dependencies

* Docker and Docker Compose

## Development

### Basic setup

Clone the repo:

    git clone git@github.com:security-force-monitor/sfm-cms.git
    cd sfm-cms

Next, create a local settings file. If you're on the Blackbox keyring for the repo,
decrypt the development settings file:

    blackbox_cat configs/settings_local_dev.py.gpg > sfm_pc/settings_local.dev.py

If you're not on the keyring, you can copy the example settings file and set
your own secret variables:

    cp sfm_pc/settings_local.example.py sfm_pc/settings_local.dev.py

Be sure to set the `GOOGLE_MAPS_KEY` in order to load maps.

Build application container images:

    docker-compose build

Once you have container images, there are two ways that you can load data into your database.

### Option 1: Load a database dump

The standard data loading process for the app can take many hours to complete. If you're working with a developer who already has a database set up, you can save time by having them make a dump of their database for you:

    docker-compose run --rm app pg_dump -Fc -h postgres -U postgres -d sfm -O > sfm_empty.dump

Then, load this dump into your own database:

    docker-compose run --rm app pg_restore -h postgres -U postgres -d sfm -O sfm.dump

Once the dump has been restored, move on to the step `Set up the search index` below.

### Option 2: Load data via management commands

#### Location data

The standard way to load data into the app is to use the app's management commands for loading data. Start by updating the `Countries` models:

    docker-compose run --rm app ./manage.py update_countries_plus

OSM data is provided by the SFM team in a special GeoJSON format. You can import
location data from a local file by running the `import_locations` command
directly –

    # import fixtures/locations.geojson
    docker-compose run --rm app ./manage.py import_locations

    # import geojson file from arbitrary path
    docker-compose run --rm app .manage.py import_locations --location_file path/to/your/file

– or, you can pass an optional `--location_file_id` argument to `import_google_docs`
to retrieve the specified file from Google Drive and import it before importing
entity data. (Read on for instructions!)

#### Entity data

The `import_google_docs` expects to find credentials for the Google
Sheets and Google Drive APIs in `sfm_pc/management/commands/credentials.json`.
If you are on the keyring for this project, run the following Blackbox commands
decrypt and create the expected credentials files, before you run `import_google_docs`.
(N.b., the data import service account lives under the `SFM - Data Import` project.)

    blackbox_cat configs/credentials.json.gpg > sfm_pc/management/commands/credentials.json

If you are not on the keyring, enable the Google Sheets and Google Drive APIs in
[the Google API Console](https://console.developers.google.com/apis/library), then
create a service account to access them. [This blog post](https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html)
provides a helpful walkthrough! Be sure to save your credentials in
`sfm_pc_management/commands/credentials.json` and give your service account
access to the correct files before you run `import_google_docs`.

Finally, import entity data from Google Drive:

    # Import entity data from default files
    docker-compose run --rm app make import_google_docs

    # Import entity data from specified files
    docker-compose run --rm app python manage.py import_google_doc --doc_id ${SOME_ID} --source_doc_id ${SOME_ID} --location_doc_id ${SOME_ID}

### Set up the search index

Build and start the Docker image for the Solr server:

    docker-compose up --build solr

Open up another shell and create the search index:

    docker-compose run --rm app ./manage.py make_search_index

Create an admin user:

    docker-compose run --rm app ./manage.py createsuperuser

Start the web server:

    docker-compose run --rm app ./manage.py runserver

Open http://127.0.0.1:8000/ and sign in with your email and password.

## Translations

We use [Django translation](https://docs.djangoproject.com/en/1.11/topics/i18n/translation/) together with [Rosetta](https://github.com/mbi/django-rosetta) and [django-complex-fields](https://github.com/security-force-monitor/complex_fields).

Template translations appear inside `trans` tags, like so:

```python
{% trans "Countries" %}
```

Model field and form error translations appear inside `_()` hooks, as such:

```python
from django.utils.translation import ugettext as _

...

field_name = _("End date")
```

This nomenclature signals that the text can be translated into the user's specified language. But first, someone with language expertise must provide the appropriate translation. Happily, Django can extract all translatable strings into a message file:

```bash
docker-compose run --rm app ./manage.py makemessages -l es
docker-compose run --rm app ./manage.py makemessages -l fr
```

This command generates a `.po` file for each language. Rosetta facilitates the editing and compiling of these files. Go to `/rosetta/`, and view the snippets of code, requiring translation, organized by language. Then, translate some text, click "Save and translate next block," and Rosetta compiles the code into Django-friendly translations.

## Tests

Run all tests from the root folder:

```
docker-compose -f docker-compose.yml -f tests/docker-compose.yml run --rm app
```

You can also run a collection of tests, like so:

```
docker-compose -f docker-compose.yml -f tests/docker-compose.yml run --rm app pytest tests/test_person.py
```

Or run a single test, like so:

```
docker-compose -f docker-compose.yml -f tests/docker-compose.yml run --rm app pytest tests/test_person.py::test_no_existing_sources
```

## Using the Google Sheet import script

If you're reading this and you're asking yourself, "Why on earth would I ever
want to import data into this system from a Google Sheet? What a nightmare!"
well, greetings from the past where that was a regular feature of our routine.
However, it was not as bad as you might think thanks to the brilliant work of
the SFM team.

The script to import data from a Google Sheet exists as a management command
within the `sfm_pc` directory of this project predictably called
`import_google_doc`. Before actually running the script, you'll need to take
a few steps.

The google sheets need to follow this format: https://docs.google.com/spreadsheets/d/12Kap4YtzWPtCdJy-iknF1aDaoIDMij4GU8E2-HlZkAo/edit#gid=597380077

### Import OpenStreetMap data

As the Google Sheet importer is importing, it is creating relationships between
the various entities within the data and OSM nodes, ways and relations. In
order to speed that process up, we bulk download the data and insert it into
the location data table directly (rather than making API calls for every lookup
or some such thing). To do that, update your settings file so that it includes
the countries you'd like to import. You should see a setting called `OSM_DATA`
that includes a list of dictionaries that look like this:

```
{
    'country': 'Mexico',
    'pbf_url': 'http://download.geofabrik.de/north-america/mexico-latest.osm.pbf',
    'relation_id': '114686',
    'country_code': 'mx',
}
```

* `country` is the nice name for the country
* `pbf_url` is a location on the internet where you can download a PBF snapshot
  of the OSM data for that country (we've been using Geofabrik and it's been
  working just fine)
* `relation_id` is the OSM id for the relation that represents the country's
  boundary
* `country_code` is the two letter ISO country code for the country

Once you have that sorted out, you'll need to make sure you have `osm2pgsql`
installed (this is the command line tool we use under the hood to turn the PBF
file into a PostgreSQL table). Once that is installed, you should be able to
run the `import_osm` management command:

```
python manage.py import_osm
```

If you're importing more than one country, this process can take a few hours,
depending on what kind of coverage each country has in OSM.

### Import data from Google Sheets

The data that powers WWIC is imported from two key Google Sheets: a "sources"
spreadsheet, and a "data" spreadsheet. Typically, a new import will involve
running import commands against a new pair of source and data spreadsheets that
represent either a new country, or updated data for an existing country.

The following sections explain our process for running these imports locally
and on live instances of WWIC.

#### Local import

When performing an import of new data, the first step should always be to
test the import in your development environment using the `import_google_doc`
management command.

This management command relies upon a [Service
Account](https://cloud.google.com/iam/docs/understanding-service-accounts)
having access to the spreadsheet. Luckily, one is already setup, you just need
to go into the permission settings for the spreadsheets and give the account read access.
If you decrypt the `credentials.json` file within the `configs` folder of this
project, you'll see that there is a `client_email` key. This is the email
address that you'll use to give the service account read access to the
spreadsheets. Navigate to the `Share` button on both the source spreadsheet
and the data spreadsheet and give the email address read access to both sheets.

Once that is setup, you should decrypt and copy the `credentials.json` file to
the same folder where the file for the management command is stored:

```
gpg -d configs/credentials.json.gpg > sfm_pc/management/commands/credentials.json
```

One more thing to do before running the Google Sheet importer. You'll need to
get the document ID for the sheet that you want to import plus the sheet that
contains the sources. If you open up those sheets in a browser, you should be
able to grab the document ID from the URL:

```
https://docs.google.com/spreadsheets/d/<doc id (very long hash looking thing)>/edit
```

Once you have those, you should be able to run the importer like so:

```
docker-compose run --rm app ./manage.py import_google_doc --source_doc_id <source doc id> --doc_id <doc id for the doc you want to import>
```

If the importer raises warnings during the import, it will log them to logfiles
following the logfile pattern `${country_code}_errors`. Once the import is complete,
take a look at your repo to check to see if the importer generated any of these
warning logfiles. If it did, send these logfiles to the SFM team so they can make
necessary adjustments to the data. We typically delete logfiles between import runs,
since the importer will append to a logfile if one exists already.


Finally, check to confirm that the search index update command works properly:

```
docker-compose run --rm app ./manage.py make_search_index --recreate
```

#### Importing data to a live site

Once you've tested an import of a new dataset locally, you're ready to run the import
on a live instance.

Since all live instances should already have credentials, you should be ready to run
a live import using the management commands:

```
tmux new -s fresh-import

# remember to switch to the correct <user> and <doc ids>
sudo su <user>
workon sfm
cd ~/sfm-cms
python manage.py import_google_doc --source_doc_id <source_doc_id> --doc_id <doc_id>
python manage.py make_search_index --recreate
```

#### Importing all data without disrupting servers

In case you need to fully rerun the entire WWIC import for all countries without
disrupting a live instance, this repo includes a Makefile for doing just that.

On every deploy, our build scripts create a separate directory, `sfm-importer`. This
directory is a copy of the app that uses a separate database with the name `importer`.
We'll use this database for our imports, so that the server can keep on serving
data normally during that process (which can take up to 8 hours!)

To perform a new import, start by creating a tmux session so your work doesn't
get interrupted. Then, activate the virtualenv for the project and change to the
`sfm-importer` directory:

```
tmux new -s fresh-import

# remember to switch to the correct user instead of <user>
sudo su <user>
workon sfm
cd ~/sfm-importer
make update_db
python manage.py make_materialized_views --recreate
python manage.py make_search_index --recreate
```

Finally, switch the `sfm` and `importer` databases:

```
# Renames the databases in a transaction -- the app doesn't need to stop
psql importer < sfm_pc/management/commands/flush/rename.sql
```

Presto! A fresh import, with no server downtime.

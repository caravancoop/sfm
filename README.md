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

Replace OSM_API_Key in `settings_local.py` with a Wambacher cliKey. Generate a key [here](https://wambachers-osm.website/boundaries/) by enabling OAuth, selecting a boundary, checking CLI, hitting Export, and looking at the generated URL.

Create a database:

    createdb sfm
    psql sfm -c "CREATE EXTENSION postgis;"
    ./manage.py migrate


Create Materialized Views for global search, and looking up a Geoname object based upon a geoname id:

    python manage.py import_osm
    python manage.py import_google_doc --source_doc_id 1IL4yJMG7KBpOdGZbFsAcGFjSPpVVSNbKLMsRdKC3-XM --doc_id <hash from URL of sheet>
    python manage.py link_locations
    python manage.py make_flattened_views

TODO - document the service account setup necessary to import from google doc
TODO - document the solr docker

Then, create the search index:

    python manage.py make_search_index

Create an admin user:

    ./manage.py createsuperuser

Start the web server:

    ./manage.py runserver

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
django-admin.py makemessages -l es
django-admin.py makemessages -l fr
```

This command generates a `.po` file for each language. Rosetta facilitates the editing and compiling of these files. Go to `/rosetta/`, and view the snippets of code, requiring translation, organized by language. Then, translate some text, click "Save and translate next block," and Rosetta compiles the code into Django-friendly translations.

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

**Import OpenStreetMap data**

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

**Import data from Google Sheet**

This management command relies upon a [Service
Account](https://cloud.google.com/iam/docs/understanding-service-accounts)
having access to the spreadsheet. Luckily, one is already setup, you just need
to go into the permission settings for the spreadsheet and give it read access.
If you decrypt the `credentials.json` file within the `configs` folder of this
project, you'll see that there is a `client_email` key. This is the email
address that you'll use to give the service account read access to the
spreadsheet.

Once that is setup, you should decrypt and copy the `credentials.json` file to
the same folder where the file for the management command is stored:

```
gpg -d configs/credentials.json.gpg
> sfm_pc/management/commands/credentials.json
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
python manage.py import_google_doc --source_doc_id <source doc id> --doc_id
<doc id for the doc you want to import>
```

## Importing new data without disrupting servers

_This documentation was written in early 2018 before some major changes to the
data structure happened that fall. There's a chance this will not work as
advertized anymore._

This repo has a system for performing fresh data imports without disrupting
the normal activity of the server.

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
sudo su - <user>
workon sfm
cd sfm-importer
```

Although the `importer` database should already be a copy of the production
database, you can redo the copy to be safe:

```
dropdb importer

# Add our typical user here instead of <user>
psql -U postgres -c "CREATE DATABASE importer WITH TEMPLATE sfm OWNER <user>"
```

If you want to drop existing tables containing data in the database, you can
use a SQL script that we have for that purpose:

```
psql importer < sfm_pc/management/commands/flush/flush.sql

# Refresh the country data, which gets dropped in flush.sql
python manage.py update_countries_plus
```

Next, perform the import as normal. This can take a long time, so go get some
fresh air.

```
python manage.py import_google_doc
python manage.py make_flattened_views --recreate
python manage.py update_search_index
```

Finally, switch the `sfm` and `importer` databases:

```
# Renames the databases in a transaction -- the app doesn't need to stop
psql importer < sfm_pc/management/commands/flush/rename.sql
```

Presto! A fresh import, with no server downtime.

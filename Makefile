SHELL := /bin/bash
DB=sfm
IMPORT_DB=importer

.PHONY : import_directory import_db flush_db recreate_db

import_directory :
	# Fail if we are not in the correct directory
	[[ "$$PWD" =~ "$(IMPORT_DIRECTORY)" ]]

import_db : import_directory
	# Drop and recreate the importer database from the live database
	PGPASSWORD=$(PG_PW) dropdb -U postgres -h $(PG_HOST) $(IMPORT_DB) || echo "$(IMPORT_DB) does not exist"
	PGPASSWORD=$(PG_PW) psql -U postgres -h $(PG_HOST) -c "CREATE DATABASE $(IMPORT_DB) WITH TEMPLATE $(DB) OWNER $(PG_USER)"

auth_models.json : import_directory import_db
	# Dump the existing user data
	python manage.py dumpdata auth.User > $@

flush_db : import_directory auth_models.json
	# Remove all data from the database
	python manage.py flush
	# Reload the user data
	python manage.py loaddata auth_models.json
	# Reload country codes
	python manage.py update_countries_plus

recreate_db : import_directory flush_db import_docket_import
	# Update data derived from entity tables
	python manage.py make_materialized_views --recreate
	python manage.py make_search_index --recreate

clean :
	rm auth_models.json *.csv

include docket.mk

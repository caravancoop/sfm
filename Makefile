SHELL := /bin/bash
LIVE_DB=sfm
IMPORT_DB=importer
IMPORT_DIRECTORY=sfm-importer
PG_HOST=localhost
PG_USER=datamade
PG_PASSWORD=


.PHONY : import_directory import_db flush_db recreate_db

import_directory :
	# Fail if we are not in the correct directory
	[[ "$$PWD" =~ "$(IMPORT_DIRECTORY)" ]]

import_db : import_directory
	# Drop and recreate the importer database from the live database
	if [ -n "$(PG_PASSWORD)" ]; then \
		PGPASSWORD=$(PG_PASSWORD) dropdb -U postgres -h $(PG_HOST) $(IMPORT_DB) || echo "$(IMPORT_DB) does not exist"; \
		PGPASSWORD=$(PG_PASSWORD) psql -U postgres -h $(PG_HOST) -c "CREATE DATABASE $(IMPORT_DB) WITH TEMPLATE $(LIVE_DB) OWNER $(PG_USER)"; \
	else \
		dropdb -U postgres -h $(PG_HOST) $(IMPORT_DB) || echo "$(IMPORT_DB) does not exist"; \
		psql -U postgres -h $(PG_HOST) -c "CREATE DATABASE $(IMPORT_DB) WITH TEMPLATE $(LIVE_DB) OWNER $(PG_USER)"; \
	fi

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
	python manage.py rebuild_index --noinput
	python manage.py update_composition_index --recreate

clean :
	rm auth_models.json *errors.csv

include docket.mk

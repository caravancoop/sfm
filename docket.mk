%_import : %.csv sfm_pc/management/commands/country_data sfm_download.zip
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Loading data for country code $$3" && (\
			python -u manage.py load_country_data \
				--country_code $$3 \
				--country_directory country_data/countries/$$3 \
				--sources_path country_data/sources.csv || \
			exit 255 \
		)'

sfm_download.zip : sfm_pc/management/commands/country_data
	zip -r $@ $<

.INTERMEDIATE :
sfm_pc/management/commands/country_data : import_docket.csv
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Importing data for country code $$3" && (\
			python -u manage.py import_google_doc \
				--sources_doc_id $$0 \
				--location_doc_id $$1 \
				--entity_doc_id $$2 \
				--country_code $$3 \
				--parent_directory $@ || \
			exit 255 \
		)'

%_cc.csv : fixtures/import_docket.csv
	grep ,$* $< > $@

%.csv : fixtures/%.csv
	tail -n +2 $< > $@

next.csv : fixtures/import_docket.csv
	tail -n +2 $< | head -n 1 > $@

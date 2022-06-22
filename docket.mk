%_import : %.csv data
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Importing data for country code $$3" && (\
			python -u manage.py import_google_doc \
				--source_doc_id $$0 \
				--location_doc_id $$1 \
				--doc_id $$2 \
				--country_code $$3 || \
			exit 255 \
		)'

sfm_download.zip : data
	zip -r $@ $<

data : import_docket.csv
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Importing data for country code $$3" && (\
			python -u manage.py download_data \
				--sources_doc_id $$0 \
				--location_doc_id $$1 \
				--entity_doc_id $$2 \
				--country_code $$3 || \
			exit 255 \
		)'

%_cc.csv : fixtures/import_docket.csv
	grep ,$* $< > $@

%.csv : fixtures/%.csv
	tail -n +2 $< > $@

next.csv : fixtures/import_docket.csv
	tail -n +2 $< | head -n 1 > $@

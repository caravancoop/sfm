.PHONY: sfm_pc/management/commands/country_data

%_import : %.csv sfm_pc/management/commands/country_data
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Loading data for country code $$3" && (\
			python -u manage.py import_country_data \
				--country_code $$3 \
				--country_path $(word 2, $^)/countries/$$3 \
				--sources_path $(word 2, $^)/sources.csv || \
			exit 255 \
		)'

DATA_ARCHIVE_BUCKET := $(shell cat configs/s3_config.json | jq -r '.data_archive_bucket')

data_archive : wwic_download.zip
	aws s3 cp $< s3://$(DATA_ARCHIVE_BUCKET)/

wwic_download.zip : sfm_pc/management/commands/country_data
	# move into the target directory, zip to the root dir
	cd $< && zip -r ../../../../$@ .

sfm_pc/management/commands/country_data : import_docket.csv
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Importing data for country code $$3" && (\
			python -u manage.py download_country_data \
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

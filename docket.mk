clean_import : 
	rm -rf $(SOURCE_DATA_PATH)/*

.PHONY: $(SOURCE_DATA_PATH) source_import clean_import

%_import : %.csv # $(SOURCE_DATA_PATH) source_import
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Loading data for country code $$3 from $(SOURCE_DATA_PATH)/$$4" && (\
			python -u manage.py import_country_data \
				--country_code $$3 \
				--country_path $(SOURCE_DATA_PATH)/$$4 || \
			exit 255 \
		)'

source_import : $(SOURCE_DATA_PATH)
	echo "Loading source data" && \
		python -u manage.py import_source_data \
			--sources_path $(SOURCE_DATA_PATH)/sources.csv

$(SOURCE_DATA_PATH) : import_docket.csv
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Downloading data for country $$4" && (\
			python -u manage.py download_country_data \
				--sources_doc_id $$0 \
				--location_doc_id $$1 \
				--entity_doc_id $$2 \
				--country_name $$4 \
				--target_directory $@ || \
			exit 255 \
		)'

%_cc.csv : fixtures/import_docket.csv
	grep ,$* $< > $@

%.csv : fixtures/%.csv
	tail -n +2 $< > $@

next.csv : fixtures/import_docket.csv
	tail -n +2 $< | head -n 1 > $@

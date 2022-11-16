# Variables for the data paths
DATA_ARCHIVE_TARGET_PATH=data/wwic_download/countries
SOURCE_DATA_TARGET_PATH=sfm_pc/management/commands/country_data/countries

# Variables for the archive data
COUNTRY_NAMES=$(shell perl -pe "s/,/ /g" import_docket.csv | cut -d' ' -f5)
ENTITIES=units.csv persons.csv incidents.csv locations.csv locations.geojson sources.csv

.PHONY: $(SOURCE_DATA_TARGET_PATH) data/wwic_download/countries data_archive wwic_download.zip directories data/wwic_download/metadata/sfm_research_handbook.pdf


# Create the data archive and upload it to S3
data_archive : wwic_download.zip
	aws s3 cp $< s3://$(shell cat configs/s3_config.json | jq -r '.data_archive_bucket')/
	rm $<

wwic_download.zip : filtered_data data/wwic_download/metadata/sfm_research_handbook.pdf
	cd data/wwic_download && zip -r ../../$@ .

filtered_data: directories $(SOURCE_DATA_TARGET_PATH) $(foreach country,$(COUNTRY_NAMES),$(patsubst %,$(country)_%,$(ENTITIES)))
	echo "filtered csvs for entities"

directories : 
	mkdir -p $(foreach country,$(COUNTRY_NAMES),$(DATA_ARCHIVE_TARGET_PATH)/$(country))

define filter_entity_data
	$(shell csvgrep --columns $(1):status:admin --match 3 $< | \
					python data/processors/blank_columns.py --entity $(1) > $(DATA_ARCHIVE_TARGET_PATH)/$*/$@)
endef

%_units.csv : $(SOURCE_DATA_TARGET_PATH)/%/units.csv
	$(call filter_entity_data,unit)

%_persons.csv : $(SOURCE_DATA_TARGET_PATH)/%/persons.csv
	$(call filter_entity_data,person)

%_incidents.csv : $(SOURCE_DATA_TARGET_PATH)/%/incidents.csv
	$(call filter_entity_data,incident)

%_sources.csv : $(SOURCE_DATA_TARGET_PATH)/%/sources.csv
	cp $< $(DATA_ARCHIVE_TARGET_PATH)/$*/$@

%_locations.csv : $(SOURCE_DATA_TARGET_PATH)/%/locations.csv
	cp $< $(DATA_ARCHIVE_TARGET_PATH)/$*/$@

%_locations.geojson : $(SOURCE_DATA_TARGET_PATH)/%/locations.geojson
	cp $< $(DATA_ARCHIVE_TARGET_PATH)/$*/$@

data/wwic_download/metadata/sfm_research_handbook.pdf : 
	curl -o $@ https://help.securityforcemonitor.org/_/downloads/en/latest/pdf/


# Download the source data and load it into the database
%_import : %.csv $(SOURCE_DATA_TARGET_PATH)
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Loading data for country code $$3" && (\
			python -u manage.py import_country_data \
				--country_code $$3 \
				--country_path $(word 2, $^)/$$4 \
				--sources_path $(word 2, $^)/sources.csv || \
			exit 255 \
		)'

$(SOURCE_DATA_TARGET_PATH) : import_docket.csv
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

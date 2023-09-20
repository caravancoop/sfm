# Variables for the archive data
COUNTRY_NAMES=$(shell perl -pe "s/,/ /g" import_docket.csv | cut -d' ' -f5)
ENTITIES=units.csv persons.csv incidents.csv locations.csv locations.geojson sources.csv

clean_archive :
	rm -rf $(DATA_ARCHIVE_PATH)/*

.PHONY : $(DATA_ARCHIVE_PATH) data_archive wwic_download.zip directories \
	data/wwic_download/metadata/sfm_research_handbook.pdf clean_archive

# Create the data archive and upload it to S3
data_archive : wwic_download.zip
	aws s3 cp $< s3://$(shell cat configs/s3_config.json | jq -r '.data_archive_bucket')/
	rm $<

wwic_download.zip : filtered_data data/wwic_download/metadata/sfm_research_handbook.pdf
	cd data/wwic_download && zip -r ../../$@ .

filtered_data: directories $(SOURCE_DATA_PATH) $(foreach country,$(COUNTRY_NAMES),$(patsubst %,$(country)_%,$(ENTITIES)))
	echo "filtered csvs for entities"

directories : 
	mkdir -p $(foreach country,$(COUNTRY_NAMES),$(DATA_ARCHIVE_PATH)/$(country))

define filter_entity_data
	$(shell csvgrep --columns $(1):status:admin --match 3 $< | \
					python data/processors/blank_columns.py --entity $(1) > $(DATA_ARCHIVE_PATH)/$*/$@)
endef

%_units.csv : $(SOURCE_DATA_PATH)/%/units.csv
	$(call filter_entity_data,unit)

%_persons.csv : $(SOURCE_DATA_PATH)/%/persons.csv
	$(call filter_entity_data,person)

%_incidents.csv : $(SOURCE_DATA_PATH)/%/incidents.csv
	$(call filter_entity_data,incident)

%_sources.csv : $(SOURCE_DATA_PATH)/%/sources.csv
	cp $< $(DATA_ARCHIVE_PATH)/$*/$@

%_locations.csv : $(SOURCE_DATA_PATH)/%/locations.csv
	cp $< $(DATA_ARCHIVE_PATH)/$*/$@

%_locations.geojson : $(SOURCE_DATA_PATH)/%/locations.geojson
	cp $< $(DATA_ARCHIVE_PATH)/$*/$@

data/wwic_download/metadata/sfm_research_handbook.pdf : 
	curl -o $@ https://help.securityforcemonitor.org/_/downloads/en/latest/pdf/

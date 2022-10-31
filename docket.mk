.PHONY: sfm_pc/management/commands/country_data/countries

DATA_ARCHIVE_BUCKET := $(shell cat configs/s3_config.json | jq -r '.data_archive_bucket')

data_archive : wwic_download.zip
	aws s3 cp $< s3://$(DATA_ARCHIVE_BUCKET)/

wwic_download.zip : filtered_data data/wwic_download/sources.csv data/wwic_download/sfm_research_handbook.pdf
	cd data && zip -r ../$@ .

COUNTRY_NAMES=$(shell perl -pe "s/,/ /g" import_docket.csv | cut -d' ' -f5)
ENTITIES=units.csv persons.csv incidents.csv locations.csv locations.geojson

.PHONY : filtered_data
filtered_data: $(foreach country,$(COUNTRY_NAMES),$(patsubst %,data/wwic_download/$(country)_%,$(ENTITIES)))
	echo "filtered csvs for entities"

define filter_entity_data
	$(shell csvgrep --columns $(1):status:admin --match 3 $< | \
					python data/processors/blank_columns.py --entity $(1) > $@)
endef

data/wwic_download/%_units.csv : sfm_pc/management/commands/country_data/countries/%/units.csv
	$(call filter_entity_data,unit)

data/wwic_download/%_persons.csv : sfm_pc/management/commands/country_data/countries/%/persons.csv
	$(call filter_entity_data,person)

data/wwic_download/%_incidents.csv : sfm_pc/management/commands/country_data/countries/%/incidents.csv
	$(call filter_entity_data,incident)

data/wwic_download/sources.csv : sfm_pc/management/commands/country_data/countries/sources.csv
	$(call filter_entity_data,source)

data/wwic_download/%_locations.csv : sfm_pc/management/commands/country_data/countries/%/locations.csv
	python data/processors/blank_columns.py --entity location > $@

data/wwic_download/%_locations.geojson : sfm_pc/management/commands/country_data/countries/%/locations.geojson
	cp $< $@

data/wwic_download/sfm_research_handbook.pdf : 
	curl -o $@ https://help.securityforcemonitor.org/_/downloads/en/latest/pdf/

%_import : %.csv sfm_pc/management/commands/country_data/countries
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Loading data for country code $$3" && (\
			python -u manage.py import_country_data \
				--country_code $$3 \
				--country_path $(word 2, $^)/$$4 \
				--sources_path $(word 2, $^)/sources.csv || \
			exit 255 \
		)'

sfm_pc/management/commands/country_data/countries : import_docket.csv
	perl -pe "s/,/ /g" $< | \
	xargs -L1 bash -c ' \
		echo "Importing data for country $$4" && (\
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

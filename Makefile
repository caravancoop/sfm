%_import :
	python manage.py import_google_doc --source_doc_id 1IL4yJMG7KBpOdGZbFsAcGFjSPpVVSNbKLMsRdKC3-XM --doc_id $(GOOGLE_DOC_ID)
	touch $@

bgd_import : GOOGLE_DOC_ID = 1P8gnl3m8LZTIi1Ms3byNyOZhQqLteMGg6wdR0qm0cdo
eg_import : GOOGLE_DOC_ID = 16dPPuY_GhRlCRkkR0oa8w9SJxSl9bynok63cT_TrZDE
mx_import : GOOGLE_DOC_ID = 1OYD42hi6Pl-Bd0urltdzDmXwhEVecPmnXOUnQUnd5RA
my_import : GOOGLE_DOC_ID = 1_YPIcXni4QJFITAx9WRQy0aLDiirgGHu3tP05BLkkJU
ng_import : GOOGLE_DOC_ID = 1rZPNL2of96vy1oO9umZDOrDZ-63yg-fxCdQt6J4F_BA
ph_import : GOOGLE_DOC_ID = 16KxRokqcpjKEaiyGEppNvhnuYF5m0jxy6HniASwefcA
rwa_import : GOOGLE_DOC_ID = 138aYP9yirsZ_--F9KFWzZfRuzlmKYd-Zfk6oWmMFPcs
sa_import : GOOGLE_DOC_ID = 17lrD9wcakpX5Vecdgg5RV9xuQlCGR3zeY4QnMc8kUAc
ug_import : GOOGLE_DOC_ID = 1HyjiqJtThYL-erEWh9-DI8pW85oh2jI8CWgVQNwv0Ng

.PHONY : import_google_docs
import_google_docs : bgd_import mx_import	\
	             ng_import ph_import rwa_import sa_import	\
	             ug_import eg_import my_import


.PHONY : clean
clean :
	rm bgd_import eg_import mx_import my_import ng_import	\
           ph_import rwa_import sa_import ug_import

.PHONY : foo
foo : 
	python manage.py make_flattened_views --recreate
	python manage.py make_search_index --recreate


osm :
	python manage.py import_osm --download_only
	python manage.py import_osm --import_only
	python manage.py link_locations


make_search_index : import_google_docs

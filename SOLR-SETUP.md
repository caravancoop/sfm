1. Download latest from http://mirror.dsrg.utoronto.ca/apache/lucene/solr/
2. Unpack into /opt
3. cd into server/solr directory
4. Make a dir for your core
5. Copy everything from server/solr/configsets/basic_configs into that folder
6. Download JTS: https://repo1.maven.org/maven2/com/vividsolutions/jts-core/1.14.0/jts-core-1.14.0.jar
7. mv it into server/solr-webapp/webapp/WEB-INF/lib/
6. cd into bin directory
7. Do ./solr start
8. Visit http://127.0.0.1:8983 in a browser and enjoy

Things to note:

* Schemas are stored in a file called managed-schema in server/solr/<core name>/conf/

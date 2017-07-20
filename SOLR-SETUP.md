## Solr Setup

1. `sudo apt-get install openjdk-8-jre-headless`
2. Download latest solr distfrom http://mirror.dsrg.utoronto.ca/apache/lucene/solr/
2a. [Verify the package](https://www.apache.org/info/verification.html) using the `.asc` signature and `KEYS` file from the official solr mirror
3. `tar xvf` into `/opt`
4. cd into `server/solr` directory
5. Make a dir for your core
6. `touch core.properties`
7. Copy everything from solr/configsets/basic_configs into that folder
8. Add `conf` folder to `basic_configs` and configure it
9. Download JTS: https://repo1.maven.org/maven2/com/vividsolutions/jts-core/1.14.0/jts-core-1.14.0.jar
10. mv it into server/solr-webapp/webapp/WEB-INF/lib/
11. Copy `schema.xml` file from the `configs` folder in the sfm-cms project into server/solr/<core name>/conf
12. Edit `solrconfig.xml` located in the folder for your core to add the following anywhere in between the `<config>` tags:

```
  <schemaFactory class="ClassicIndexSchemaFactory"/>
```

13. cd into bin directory
14. Do ./solr start
15. Visit http://127.0.0.1:8983 in a browser and enjoy


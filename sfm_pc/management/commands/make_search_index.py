from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError

class Command(BaseCommand):
    help = 'Add global search index'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate',
            default=False,
            help='Recreate search index'
        )
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            dest='force_refresh',
            default=False,
            help='Force search index to refresh'
        )
    
    def handle(self, *args, **options):
        
        if options['force_refresh']:
            with connection.cursor() as c:
                c.execute('REFRESH MATERIALIZED VIEW search_index')
            
            self.stdout.write(self.style.SUCCESS('Successfully refreshed index'))
            return None

        if options['recreate']:
            with connection.cursor() as c:
                c.execute('DROP MATERIALIZED VIEW IF EXISTS search_index')

            self.stdout.write(self.style.SUCCESS('Successfully dropped existing index'))
        
        c = connection.cursor()
        
        try:
            create_table = ''' 
                CREATE MATERIALIZED VIEW search_index AS 
                  SELECT 
                    to_tsvector('english', title) AS content,
                    'Source' AS content_type,
                    'source' AS value_type,
                    id AS object_ref_id,
                    id,
                    NULL::geometry(Point, 4326) AS site,
                    NULL::geometry(Polygon, 4326) AS area
                  FROM source_source
                  UNION
                  SELECT
                    to_tsvector('english', sp.title) AS content,
                    'Source' AS content_type,
                    'publication' AS value_type,
                    s.id AS object_ref_id,
                    s.id,
                    NULL::geometry(Point, 4326) AS site,
                    NULL::geometry(Polygon, 4326) AS area
                  FROM source_publication AS sp
                  JOIN source_source AS s
                    ON sp.id = s.publication_id
                  UNION
                  SELECT DISTINCT ON(o.object_ref_id, o.id)
                    to_tsvector('english', o.value) AS content,
                    'Organization' AS content_type,
                    'organizationname' AS value_type,
                    o.object_ref_id,
                    o.id,
                    coordinates.value AS site,
                    area.value AS area
                  FROM organization_organizationname AS o
                  LEFT JOIN (
                    SELECT 
                      eo.value_id,
                      gc.value
                    FROM emplacement_emplacementorganization AS eo 
                    JOIN emplacement_emplacement AS e 
                      ON eo.object_ref_id = e.id 
                    JOIN emplacement_emplacementsite AS es 
                      ON e.id = es.object_ref_id 
                    JOIN geosite_geosite AS g 
                      ON es.value_id = g.id 
                    JOIN geosite_geositecoordinates AS gc 
                      ON g.id = gc.object_ref_id
                  ) AS coordinates
                    ON o.object_ref_id = coordinates.value_id
                  LEFT JOIN (
                    SELECT
                      ao.value_id,
                      ag.value
                    FROM association_associationorganization AS ao
                    JOIN association_association AS aa
                      ON ao.object_ref_id = aa.id
                    JOIN association_associationarea AS aaa
                      ON aaa.object_ref_id = aa.id
                    JOIN area_area AS area
                      ON aaa.value_id = area.id
                    JOIN area_areageometry AS ag
                      ON area.id = ag.object_ref_id
                  ) AS area
                    ON o.object_ref_id = area.value_id
                  UNION
                  SELECT DISTINCT ON(oa.object_ref_id, oa.id)
                    to_tsvector('english', a.value) AS content,
                    'Organization' AS content_type,
                    'organizationalias' AS value_type,
                    oa.object_ref_id,
                    oa.id,
                    coordinates.value AS site,
                    area.value AS area
                  FROM organization_organizationalias AS oa
                  JOIN organization_alias AS a
                    ON oa.value_id = a.id
                  LEFT JOIN (
                    SELECT 
                      eo.value_id,
                      gc.value
                    FROM emplacement_emplacementorganization AS eo 
                    JOIN emplacement_emplacement AS e 
                      ON eo.object_ref_id = e.id 
                    JOIN emplacement_emplacementsite AS es 
                      ON e.id = es.object_ref_id 
                    JOIN geosite_geosite AS g 
                      ON es.value_id = g.id 
                    JOIN geosite_geositecoordinates AS gc 
                      ON g.id = gc.object_ref_id
                  ) AS coordinates
                    ON oa.object_ref_id = coordinates.value_id
                  LEFT JOIN (
                    SELECT
                      ao.value_id,
                      ag.value
                    FROM association_associationorganization AS ao
                    JOIN association_association AS aa
                      ON ao.object_ref_id = aa.id
                    JOIN association_associationarea AS aaa
                      ON aaa.object_ref_id = aa.id
                    JOIN area_area AS area
                      ON aaa.value_id = area.id
                    JOIN area_areageometry AS ag
                      ON area.id = ag.object_ref_id
                  ) AS area
                    ON oa.object_ref_id = area.value_id
                  UNION
                  SELECT DISTINCT ON(pn.object_ref_id, pn.id)
                    to_tsvector('english', pn.value) AS content,
                    'Person' AS content_type,
                    'personname' AS value_type,
                    pn.object_ref_id,
                    pn.id,
                    coordinates.value AS site,
                    area.value AS area
                  FROM person_personname AS pn
                  LEFT JOIN (
                    SELECT 
                      mpmpm.value_id, 
                      gc.value
                    FROM membershipperson_membershippersonmember AS mpmpm 
                    JOIN membershipperson_membershipperson AS mpmp 
                      ON mpmpm.object_ref_id = mpmp.id 
                    JOIN membershipperson_membershippersonorganization AS mpmpo 
                      ON mpmp.id = mpmpo.object_ref_id 
                    JOIN organization_organization AS o 
                      ON mpmpo.value_id = o.id 
                    JOIN emplacement_emplacementorganization AS eeo 
                      ON o.id = eeo.value_id 
                    JOIN emplacement_emplacement AS ee 
                      ON ee.id = eeo.object_ref_id 
                    JOIN emplacement_emplacementsite AS ees 
                      ON ees.object_ref_id = ee.id 
                    JOIN geosite_geosite AS g 
                      ON ees.value_id = g.id 
                    JOIN geosite_geositecoordinates AS gc 
                      ON gc.object_ref_id = g.id
                  ) AS coordinates
                    ON pn.object_ref_id = coordinates.value_id
                  LEFT JOIN (
                    SELECT 
                      mpmpm.value_id, 
                      ag.value
                    FROM membershipperson_membershippersonmember AS mpmpm 
                    JOIN membershipperson_membershipperson AS mpmp 
                      ON mpmpm.object_ref_id = mpmp.id 
                    JOIN membershipperson_membershippersonorganization AS mpmpo 
                      ON mpmp.id = mpmpo.object_ref_id 
                    JOIN organization_organization AS o 
                      ON mpmpo.value_id = o.id 
                    JOIN association_associationorganization AS ao
                      ON ao.value_id = o.id
                    JOIN association_association AS aa
                      ON ao.object_ref_id = aa.id
                    JOIN association_associationarea AS aaa
                      ON aaa.object_ref_id = aa.id
                    JOIN area_area AS area
                      ON aaa.value_id = area.id
                    JOIN area_areageometry AS ag
                      ON area.id = ag.object_ref_id
                  ) AS area
                    ON pn.object_ref_id = area.value_id
                  UNION
                  SELECT DISTINCT ON(pa.object_ref_id, pa.id)
                    to_tsvector('english', a.value) AS content,
                    'Person' AS content_type,
                    'personalias' AS value_type,
                    pa.object_ref_id,
                    pa.id,
                    coordinates.value AS site,
                    area.value AS area
                  FROM person_personalias AS pa
                  JOIN person_alias AS a
                    ON pa.value_id = a.id
                  LEFT JOIN (
                    SELECT 
                      mpmpm.value_id, 
                      gc.value
                    FROM membershipperson_membershippersonmember AS mpmpm 
                    JOIN membershipperson_membershipperson AS mpmp 
                      ON mpmpm.object_ref_id = mpmp.id 
                    JOIN membershipperson_membershippersonorganization AS mpmpo 
                      ON mpmp.id = mpmpo.object_ref_id 
                    JOIN organization_organization AS o 
                      ON mpmpo.value_id = o.id 
                    JOIN emplacement_emplacementorganization AS eeo 
                      ON o.id = eeo.value_id 
                    JOIN emplacement_emplacement AS ee 
                      ON ee.id = eeo.object_ref_id 
                    JOIN emplacement_emplacementsite AS ees 
                      ON ees.object_ref_id = ee.id 
                    JOIN geosite_geosite AS g 
                      ON ees.value_id = g.id 
                    JOIN geosite_geositecoordinates AS gc 
                      ON gc.object_ref_id = g.id
                  ) AS coordinates
                    ON pa.object_ref_id = coordinates.value_id
                  LEFT JOIN (
                    SELECT 
                      mpmpm.value_id, 
                      ag.value
                    FROM membershipperson_membershippersonmember AS mpmpm 
                    JOIN membershipperson_membershipperson AS mpmp 
                      ON mpmpm.object_ref_id = mpmp.id 
                    JOIN membershipperson_membershippersonorganization AS mpmpo 
                      ON mpmp.id = mpmpo.object_ref_id 
                    JOIN organization_organization AS o 
                      ON mpmpo.value_id = o.id 
                    JOIN association_associationorganization AS ao
                      ON ao.value_id = o.id
                    JOIN association_association AS aa
                      ON ao.object_ref_id = aa.id
                    JOIN association_associationarea AS aaa
                      ON aaa.object_ref_id = aa.id
                    JOIN area_area AS area
                      ON aaa.value_id = area.id
                    JOIN area_areageometry AS ag
                      ON area.id = ag.object_ref_id
                  ) AS area
                    ON pa.object_ref_id = area.value_id
                  UNION
                  SELECT
                    to_tsvector('english', vvd.value) AS content,
                    'Violation' AS content_type,
                    'violationdescription' AS value_type,
                    vvd.object_ref_id,
                    vvd.id,
                    coordinates.value AS site,
                    NULL::geometry(Polygon, 4326) AS area
                  FROM violation_violationdescription AS vvd
                  JOIN violation_violation AS vv
                    ON vvd.object_ref_id = vv.id
                  JOIN violation_violationlocation AS coordinates
                    ON coordinates.object_ref_id = vv.id
            '''
            
            create_gin_index = ''' 
                CREATE INDEX ON search_index USING gin(content)
            '''
            
            create_unique_index = ''' 
                CREATE UNIQUE INDEX ON search_index (value_type, object_ref_id, id) 
            '''
            
            # Create a couple functions to make buffers in meters easier: 
            # http://www.gistutor.com/postgresqlpostgis/6-advanced-postgresqlpostgis-tutorials/58-postgis-buffer-latlong-and-other-projections-using-meters-units-custom-stbuffermeters-function.html
            
            create_utm_func = ''' 
                CREATE OR REPLACE FUNCTION utmzone(geometry)
                    RETURNS integer AS
                    $BODY$
                    DECLARE
                    geomgeog geometry;
                    zone int;
                    pref int;
                     
                    BEGIN
                    geomgeog:= ST_Transform($1,4326);
                     
                    IF (ST_Y(geomgeog))>0 THEN
                    pref:=32600;
                    ELSE
                    pref:=32700;
                    END IF;
                     
                    zone:=floor((ST_X(geomgeog)+180)/6)+1;
                     
                    RETURN zone+pref;
                    END;
                    $BODY$ LANGUAGE 'plpgsql' IMMUTABLE
                    COST 100;
            '''
            
            create_buffer_func = '''
                CREATE OR REPLACE FUNCTION ST_Buffer_Meters(geometry, double precision)
                    RETURNS geometry AS
                    $BODY$
                    DECLARE
                    orig_srid int;
                    utm_srid int;
                     
                    BEGIN
                    orig_srid:= ST_SRID($1);
                    utm_srid:= utmzone(ST_Centroid($1));
                     
                    RETURN ST_transform(ST_Buffer(ST_transform($1, utm_srid), $2), orig_srid);
                    END;
                    $BODY$ LANGUAGE 'plpgsql' IMMUTABLE
                    COST 100;
            '''

            c.execute(create_table)
            c.execute(create_gin_index)
            c.execute(create_unique_index)
            c.execute(create_utm_func)
            c.execute(create_buffer_func)
            self.stdout.write(self.style.SUCCESS('Successfully created global search index'))
        
        except ProgrammingError as e:
            print(e)
            self.stdout.write(self.style.ERROR('Search index already exists. To recreate, use the --recreate flag'))
        
        c.close()

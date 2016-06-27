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
    
    def handle(self, *args, **options):
        
        if options['recreate']:
            with connection.cursor() as c:
                c.execute('DROP TABLE IF EXISTS search_index')

            self.stdout.write(self.style.SUCCESS('Successfully dropped existing index'))

        c = connection.cursor()
        
        try:
            create_table = ''' 
                CREATE TABLE search_index AS 
                  SELECT 
                    to_tsvector('english', title) AS content,
                    'Source' AS content_type,
                    'source' AS value_type,
                    id AS object_ref_id,
                    id
                  FROM source_source
                  UNION
                  SELECT
                    to_tsvector('english', sp.title) AS content,
                    'Source' AS content_type,
                    'publication' AS value_type,
                    s.id AS object_ref_id,
                    s.id
                  FROM source_publication AS sp
                  JOIN source_source AS s
                    ON sp.id = s.publication_id
                  UNION
                  SELECT
                    to_tsvector('english', value) AS content,
                    'Organization' AS content_type,
                    'organizationname' AS value_type,
                    object_ref_id,
                    id
                  FROM organization_organizationname
                  UNION
                  SELECT
                    to_tsvector('english', a.value) AS content,
                    'Organization' AS content_type,
                    'organizationalias' AS value_type,
                    oa.object_ref_id,
                    oa.id
                  FROM organization_organizationalias AS oa
                  JOIN organization_alias AS a
                    ON oa.value_id = a.id
                  UNION
                  SELECT
                    to_tsvector('english', value) AS content,
                    'Person' AS content_type,
                    'personname' AS value_type,
                    object_ref_id,
                    id
                  FROM person_personname
                  UNION
                  SELECT
                    to_tsvector('english', a.value) AS content,
                    'Person' AS content_type,
                    'personalias' AS value_type,
                    pa.object_ref_id,
                    pa.id
                  FROM person_personalias AS pa
                  JOIN person_alias AS a
                    ON pa.value_id = a.id
                  UNION
                  SELECT
                    to_tsvector('english', value) AS content,
                    'Violation' AS content_type,
                    'violationdescription' AS value_type,
                    object_ref_id,
                    id
                  FROM violation_violationdescription
            '''
            
            create_index = ''' 
                CREATE INDEX ON search_index USING gin(content)
            '''
            
            c.execute(create_table)
            c.execute(create_index)
            c.close()
        
        except ProgrammingError as e:
            print(e)
            self.stdout.write(self.style.ERROR('Search index already exists. To recreate, use the --recreate flag'))
            c.close()

            return None
        
        indexed_attributes = [
            ('source_source', 'title',),
            ('source_publication', 'title',),
            ('organization_organizationname', 'value',),
            ('organization_alias', 'value',),
            ('person_personname', 'value',),
            ('person_alias', 'value',),
            ('violation_violationdescription', 'value',),
        ]

        with connection.cursor() as c:

            # Make sure to only create triggers of search_index is new
            for table_name, column_name in indexed_attributes:
                drop_trigger = ''' 
                    DROP TRIGGER IF EXISTS {table_name}_{column_name}_update
                    ON {table_name}
                '''.format(table_name=table_name,
                           column_name=column_name)
                
                create_update_trigger = ''' 
                    CREATE TRIGGER {table_name}_{column_name}_update
                    AFTER INSERT OR UPDATE OR DELETE ON {table_name}
                    FOR EACH ROW EXECUTE PROCEDURE update_search()
                '''.format(table_name=table_name,
                           column_name=column_name)
                
                c.execute(drop_trigger)
                # c.execute(create_update_trigger)

        self.stdout.write(self.style.SUCCESS('Successfully created global search index'))

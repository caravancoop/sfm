from os.path import join, abspath, dirname

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError
import pysolr

from search.search import Searcher


class Command(BaseCommand):
    help = 'Add global search index'

    def __init__(self, *args, **kwargs):

        super(Command, self).__init__(*args, **kwargs)

        self.searcher = Searcher()
        self.updated_count = 0
        self.added_count = 0

    def add_arguments(self, parser):

        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help="Add new items to an existing search index"
        )
        parser.add_argument(
            '--entity-types',
            dest='entity_types',
            help='Comma separated list of entity types to index',
            default="people,organizations,sources,events"
        )
        parser.add_argument(
            '--id',
            dest='doc_id',
            default=None,
            help="Specify a specific record ID to index"
        )

    def handle(self, *args, **options):

        entity_types = [e.strip() for e in options['entity_types'].split(',')]
        update = options.get('update')
        doc_id = options.get('doc_id')

        for entity_type in entity_types:

            getattr(self, 'index_{}'.format(entity_type))(update=update,
                                                          doc_id=doc_id)

        if update:
            success_message = 'Successfully updated global search index.'
            count = '{count} new indexes added.'.format(count=self.updated_count)
        else:
            success_message = 'Successfully created global search index.'
            count = '{count} new indexes added.'.format(count=self.added_count)

        self.stdout.write(self.style.SUCCESS(success_message))
        self.stdout.write(self.style.SUCCESS(count))

    def index_organizations(self, doc_id=None, update=False):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing organizations ... '))

        organizations = '''
            SELECT
              o.id,
              MAX(o.name) AS name,
              array_agg(DISTINCT TRIM(o.alias))
                FILTER (WHERE TRIM(o.alias) IS NOT NULL) AS other_names,
              array_agg(DISTINCT TRIM(o.classification))
                FILTER (WHERE TRIM(o.classification) IS NOT NULL) AS classifications,
              ST_AsText(
                COALESCE(MAX(g.coordinates),
                         MAX(ST_Centroid(a.geometry)))) AS location,
              COALESCE(MAX(e.start_date), MAX(ass.start_date))::timestamp AS start_date,
              COALESCE(MAX(e.end_date), MAX(ass.end_date))::timestamp AS end_date
            FROM organization AS o
            LEFT JOIN emplacement AS e
              ON o.id = e.organization_id
            LEFT JOIN geosite as g
              ON e.site_id = g.id
            LEFT JOIN association AS ass
              ON o.id = ass.organization_id
            LEFT JOIN area AS a
              ON ass.area_id = a.id
        '''

        # Optionally, filter the query so that we add just one specific record
        if doc_id:
            organizations += '''
                WHERE o.id = '{doc_id}'
            '''.format(doc_id=doc_id)

        # Finally, make sure to group the records by unique ID
        organizations += '''
            GROUP BY o.id
        '''
        country_cursor = connection.cursor()

        documents = []

        org_cursor = connection.cursor()
        org_cursor.execute(organizations)
        columns = [c[0] for c in org_cursor.description]

        for organization in org_cursor:
            organization = dict(zip(columns, organization))

            # Skip this record if we're updating and the document is already
            # in the index
            if update and self.check_index(organization['id']):
                continue

            content = [organization['name']]

            if organization['other_names']:
                content.extend(n for n in organization['other_names'])

            content = '; '.join(content)

            start_date = None
            end_date = None

            if organization['start_date']:
                start_date = organization['start_date'].strftime('%Y-%m-%dT%H:%M:%SZ')

            if organization['end_date']:
                end_date = organization['end_date'].strftime('%Y-%m-%dT%H:%M:%SZ')

            document = {
                'id': organization['id'],
                'entity_type': 'Organization',
                'content': content,
                'location': organization['location'],
                'start_date_dt': start_date,
                'end_date_dt': end_date,
                'organization_name_s': organization['name'],
                'organization_classification_ss': organization['classifications'],
                'organization_alias_ss': organization['other_names'],
                'organization_start_date_dt': start_date,
                'organization_end_date_dt': end_date,
                '_text_': content
            }

            documents.append(document)

            if update:
                self.updated_count += 1
            else:
                self.added_count += 1

        self.add_to_index(documents)

    def index_people(self, doc_id=None, update=False):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing people ... '))

        people = '''
            SELECT
              p.id,
              MAX(p.name) AS name,
              array_agg(DISTINCT TRIM(p.alias))
                FILTER (WHERE TRIM(p.alias) IS NOT NULL) AS other_names,
              MAX(p.division_id) AS division_id
            FROM person AS p
        '''

        if doc_id:
            people += '''
                WHERE p.id = '{doc_id}'
            '''.format(doc_id=doc_id)

        people += '''
            GROUP BY p.id
        '''

        person_cursor = connection.cursor()
        person_cursor.execute(people)
        person_columns = [c[0] for c in person_cursor.description]

        documents = []

        for person in person_cursor:
            person = dict(zip(person_columns, person))

            if update and self.check_index(person['id']):
                continue

            memberships = '''
                SELECT DISTINCT ON (member_id)
                  mp.organization_id,
                  o.name AS organization_name,
                  role,
                  rank,
                  title,
                  mp.first_cited::timestamp AS first_cited,
                  mp.last_cited::timestamp AS last_cited,
                  ST_AsText(
                    COALESCE(g.coordinates,
                             ST_Centroid(a.geometry))) AS location
                FROM membershipperson AS mp
                JOIN organization AS o
                  ON mp.organization_id = o.id
                LEFT JOIN emplacement AS e
                  ON o.id = e.organization_id
                LEFT JOIN geosite as g
                  ON e.site_id = g.id
                LEFT JOIN association AS ass
                  ON o.id = ass.organization_id
                LEFT JOIN area AS a
                  ON ass.area_id = a.id
                WHERE member_id = %s
                ORDER BY member_id, COALESCE(mp.last_cited, mp.first_cited) DESC
            '''

            membership_cursor = connection.cursor()
            membership_cursor.execute(memberships, [person['id']])
            member_columns = [c[0] for c in membership_cursor.description]

            member_row = membership_cursor.fetchone()

            if not member_row:
                continue

            membership = dict(zip(member_columns, member_row))

            content = [person['name']]

            if person['other_names']:
                content.extend(n for n in person['other_names'])

            content = '; '.join(content)

            first_cited = None
            last_cited = None

            if membership['first_cited']:
                first_cited = membership['first_cited'].strftime('%Y-%m-%dT%H:%M:%SZ')

            if membership['last_cited']:
                last_cited = membership['last_cited'].strftime('%Y-%m-%dT%H:%M:%SZ')

            document = {
                'id': person['id'],
                'entity_type': 'Person',
                'content': content,
                'location': membership['location'],
                'start_date_dt': first_cited,
                'end_date_dt': last_cited,
                'person_name_s': person['name'],
                'person_alias_ss': person['other_names'],
                'person_current_rank_s': membership['rank'],
                'person_current_role_s': membership['role'],
                'person_current_title_s':membership['title'],
                'person_first_cited_dt': first_cited,
                'person_last_cited_dt': last_cited,
                '_text_': content
            }

            documents.append(document)

            if update:
                self.updated_count += 1
            else:
                self.added_count += 1

        self.add_to_index(documents)

    def index_events(self, doc_id=None, update=False):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing events ... '))

        violation_query = '''
            SELECT
              v.id,
              ARRAY_AGG(DISTINCT v.violation_type)
                FILTER (WHERE v.violation_type IS NOT NULL) AS violation_type,
              MAX(v.admin_level_1) AS admin_level_1,
              MAX(v.admin_level_2) AS admin_level_2,
              MAX(v.location_description) AS location_description,
              MAX(v.description) AS description,
              MAX(v.start_date)::timestamp AS start_date,
              MAX(v.end_date)::timestamp AS end_date,
              ST_AsText(
                COALESCE(MAX(g.coordinates),
                         MAX(ST_Centroid(a.geometry)))) AS location,
              ARRAY_AGG(DISTINCT v.perpetrator_id)
                FILTER (WHERE v.perpetrator_id IS NOT NULL) AS perpetrator_id,
              ARRAY_AGG(v.perpetrator_organization_id)
                FILTER (WHERE v.perpetrator_organization_id IS NOT NULL)
                AS perpetrator_organization_id,
              ARRAY_AGG(DISTINCT v.perpetrator_classification)
                FILTER (WHERE v.perpetrator_classification IS NOT NULL)
                AS perp_class
            FROM violation AS v
            LEFT JOIN geosite as g
              ON (g.admin_id::varchar = v.osm_id)
            LEFT JOIN area AS a
              ON (a.osmid = g.admin_id)
        '''

        if doc_id:
            violation_query += '''
                WHERE v.id = '{doc_id}'
            '''.format(doc_id=doc_id)

        violation_query += '''
            GROUP BY v.id
        '''

        violation_cursor = connection.cursor()
        violation_cursor.execute(violation_query)
        violation_columns = [c[0] for c in violation_cursor.description]

        documents = []

        for violation in violation_cursor:

            violation = dict(zip(violation_columns, violation))

            if update and self.check_index(violation['id']):
                continue

            # Global index on the description field
            content = []
            if violation['description']:
                content.append(violation['description'])

            # To build location descriptions, start with the most reliable
            locations = [violation['admin_level_2']]

            if violation['admin_level_1']:
                locations.append(violation['admin_level_1'])

            if violation['location_description']:
                locations.append(violation['location_description'])

            start_date, end_date = None, None

            if violation['start_date']:
                start_date = violation['start_date'].strftime('%Y-%m-%dT%H:%M:%SZ')

            if violation['end_date']:
                end_date = violation['end_date'].strftime('%Y-%m-%dT%H:%M:%SZ')

            perp_query = '''
                SELECT
                  DISTINCT t.name,
                  ARRAY_AGG(DISTINCT TRIM(t.alias))
                    FILTER (WHERE TRIM(t.alias) IS NOT NULL)
                    AS aliases
                FROM {table} AS t
                WHERE id = '{perp_id}'
                GROUP BY t.name
            '''

            perp_name, perp_aliases = '', []

            if violation['perpetrator_id'] is not None:
                for perp_id in violation['perpetrator_id']:

                    query = perp_query.format(table='person', perp_id=perp_id)

                    perp_cursor = connection.cursor()
                    perp_cursor.execute(query)
                    perp_columns = [c[0] for c in perp_cursor.description]

                    perp_results = dict(zip(perp_columns,
                                            perp_cursor.fetchone()))

                    perp_name = perp_results['name']
                    perp_aliases = perp_results['aliases']

            perp_org_name, perp_org_aliases = '', []

            if violation['perpetrator_organization_id'] is not None:
                for org_id in violation['perpetrator_organization_id']:

                    query = perp_query.format(table='organization',
                                              perp_id=org_id)

                    perp_org_cursor = connection.cursor()
                    perp_org_cursor.execute(query)
                    perp_org_columns = [c[0] for c in
                                        perp_org_cursor.description]

                    perp_org_results = dict(zip(perp_org_columns,
                                                perp_org_cursor.fetchone()))

                    perp_org_name = perp_org_results['name']
                    perp_org_aliases = perp_org_results['aliases']

            for lst in (perp_name, perp_aliases, perp_org_name, perp_org_aliases):
                if lst:
                    content.extend(lst)

            content = '; '.join(content)


            document = {
                'id': violation['id'],
                'entity_type': 'Violation',
                'content': content,
                'location': violation['location'],
                'start_date_dt': start_date,
                'end_date_dt': end_date,
                'violation_location_description_ss': locations,
                'violation_type_ss': violation['violation_type'],
                'violation_description_t': violation['description'],
                'violation_start_date_dt': start_date,
                'violation_end_date_dt': end_date,
                'perpetrator_s': perp_name,
                'perpetrator_alias_ss': perp_aliases,
                'perpetrator_organization_ss': perp_org_name,
                'perpetrator_organization_alias_ss': perp_org_aliases,
                'perpetrator_classification_ss': violation['perp_class'],
                '_text_': content
            }

            documents.append(document)

            if update:
                self.updated_count += 1
            else:
                self.added_count += 1

        self.add_to_index(documents)

    def index_sources(self, doc_id=None, update=False):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing sources ... '))

        source_query= '''
            SELECT
              src.id,
              MAX(src.title) AS src_title,
              MAX(src.source_url) AS src_url,
              MAX(src.published_on)::timestamp as date_published,
              MAX(pub.title) AS pub_title,
              MAX(pub.country) AS pub_country
            FROM source_source as src
            LEFT JOIN source_publication as pub
              ON src.publication_id = pub.id
        '''

        if doc_id:
            source_query += '''
                WHERE src.id = '{doc_id}'
            '''.format(doc_id=doc_id)

        source_query += '''
            GROUP BY src.id
        '''

        source_cursor = connection.cursor()
        source_cursor.execute(source_query)
        source_columns = [c[0] for c in source_cursor.description]

        documents = []

        for source in source_cursor:

            source = dict(zip(source_columns, source))

            if update and self.check_index(source['id']):
                continue

            date_published = source['date_published'].strftime('%Y-%m-%dT%H:%M:%SZ')

            content = source['src_title']

            if len(content) == 0:
                # The import data script is missing one title - skip it for now
                continue

            document = {
                'id': source['id'],
                'entity_type': 'Source',
                'content': content,
                'source_url_s': source['src_url'],
                'source_title_t': source['src_title'],
                'source_date_published_dt': date_published,
                'publication_title_t': source['pub_title'],
                'publication_country_s': source['pub_country'],
                '_text_': content
            }

            documents.append(document)

            if update:
                self.updated_count += 1
            else:
                self.added_count += 1

        self.add_to_index(documents)

    def add_to_index(self, documents):

        self.searcher.add(documents)

    def check_index(self, doc_id):
        '''
        Check if a document with the id `doc_id` already exists in the index.

        Returns boolean.
        '''
        results = self.searcher.search('id:"{doc_id}"'.format(doc_id=doc_id))

        return len(results) > 0


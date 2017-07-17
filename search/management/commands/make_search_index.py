from os.path import join, abspath, dirname

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError

from search.search import Searcher


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
        parser.add_argument(
            '--entity-types',
            dest='entity_types',
            help='Comma separated list of entity types to index',
            default="people,organizations,sources,events"
        )

    def handle(self, *args, **options):

        entity_types = [e.strip() for e in options['entity_types'].split(',')]

        for entity_type in entity_types:

            getattr(self, 'index_{}'.format(entity_type))()

        self.stdout.write(self.style.SUCCESS('Successfully created global search index'))

    def index_organizations(self):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing organizations ... '))

        countries = '''
            SELECT DISTINCT division_id FROM organization
        '''

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
            WHERE o.division_id = %s
            GROUP BY o.id
        '''

        country_cursor = connection.cursor()
        country_cursor.execute(countries)

        documents = []

        for row in country_cursor:
            country = row[0]

            if country:

                org_cursor = connection.cursor()
                org_cursor.execute(organizations, [country])
                columns = [c[0] for c in org_cursor.description]

                for organization in org_cursor:
                    organization = dict(zip(columns, organization))

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
                        'content': content,
                        'location': organization['location'],
                        'organization_name_s': organization['name'],
                        'organization_classification_ss': organization['classifications'],
                        'organization_alias_ss': organization['other_names'],
                        'organization_start_date_dt': start_date,
                        'organization_end_date_dt': end_date,
                    }

                    documents.append(document)

        self.add_to_index(documents)

    def index_people(self):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing people ... '))

        people = '''
            SELECT
              p.id,
              MAX(p.name) AS name,
              array_agg(DISTINCT TRIM(p.alias))
                FILTER (WHERE TRIM(p.alias) IS NOT NULL) AS other_names,
              MAX(p.division_id) AS division_id
            FROM person AS p
            GROUP BY p.id
        '''

        person_cursor = connection.cursor()
        person_cursor.execute(people)
        person_columns = [c[0] for c in person_cursor.description]

        documents = []

        for person in person_cursor:
            person = dict(zip(person_columns, person))

            memberships = '''
                SELECT DISTINCT ON (member_id)
                  mp.organization_id,
                  o.name AS organization_name,
                  role,
                  rank,
                  title,
                  first_cited::timestamp AS first_cited,
                  last_cited::timestamp AS last_cited,
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
                ORDER BY member_id, COALESCE(last_cited, first_cited) DESC
            '''

            membership_cursor = connection.cursor()
            membership_cursor.execute(memberships, [person['id']])
            member_columns = [c[0] for c in membership_cursor.description]

            membership = dict(zip(member_columns, membership_cursor.fetchone()))

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
                'content': content,
                'location': membership['location'],
                'person_name_s': person['name'],
                'person_alias_ss': person['other_names'],
                'person_current_rank_s': membership['rank'],
                'person_current_role_s': membership['role'],
                'person_current_title_s':membership['title'],
                'person_first_cited_dt': first_cited,
                'person_last_cited_dt': last_cited,
            }

            documents.append(document)

        self.add_to_index(documents)

    def index_sources(self):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing sources ... '))

    def index_events(self):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing events ... '))

    def add_to_index(self, documents):

        searcher = Searcher()

        searcher.add(documents)


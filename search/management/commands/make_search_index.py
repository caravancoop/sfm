from os.path import join, abspath, dirname

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
from django.db.utils import ProgrammingError
from django.utils import dateformat
from countries_plus.models import Country
import pysolr

from search.search import Searcher
from person.models import Person
from membershipperson.models import MembershipPerson
from sfm_pc.templatetags.countries import country_name

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
            default="people,organizations,sources,violations"
        )
        parser.add_argument(
            '--id',
            dest='doc_id',
            default=None,
            help="Specify a specific record ID to index"
        )
        parser.add_argument(
            '--recreate',
            action='store_true',
            dest='recreate',
            default=False,
            help="Delete all existing documents before creating the search index."
        )

    def handle(self, *args, **options):

        # Get command line args
        entity_types = [e.strip() for e in options['entity_types'].split(',')]
        update = options.get('update')
        doc_id = options.get('doc_id')
        recreate = options.get('recreate')

        if recreate:
            self.stdout.write(self.style.SUCCESS('Dropping current search index...'))
            self.searcher.delete(q='*:*')

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

        if doc_id:
            people = Person.objects.filter(uuid=doc_id)
        else:
            people = Person.objects.all()

        documents = []

        for person in people:

            person_id = str(person.uuid)
            if update and self.check_index(person_id):
                continue

            name = person.name.get_value()
            content = [name.value]

            aliases = person.aliases.get_list()
            if aliases:
                content.extend(al.get_value().value.value for al in aliases)

            memberships = MembershipPerson.objects.filter(membershippersonmember__value=person)

            division_ids, countries = set(), set()

            # Start by getting the division ID recorded for the person
            person_division_id = person.division_id.get_value()
            if person_division_id:
                division_ids.update([person_division_id.value])
                person_country = country_name(person_division_id)
                countries.update([person_country])

            ranks, roles, titles = set(), set(), set()
            latest_rank, latest_role, latest_title = None, None, None

            first_cited = None
            last_cited = None

            for membership in memberships:

                role = membership.role.get_value()
                if role:
                    roles.update([role.value.value])

                rank = membership.rank.get_value()
                if rank:
                    ranks.update([rank.value.value])

                title = membership.title.get_value()
                if title:
                    titles.update([title.value])

                org = membership.organization.get_value()
                if org:
                    org = org.value

                    # We also want to index the person based on the countries
                    # their member units have operated in
                    org_division_id = org.division_id.get_value()
                    if org_division_id:
                        division_ids.update([org_division_id.value])
                        org_country = country_name(org_division_id)
                        countries.update([org_country])

                # Check to see if we can extend first/last cited dates
                fcd = membership.firstciteddate.get_value()
                if fcd:
                    if first_cited:
                        if fcd.value < first_cited.value:
                            first_cited = fcd
                    else:
                        first_cited = fcd

                lcd = membership.lastciteddate.get_value()
                if lcd:
                    if last_cited:
                        if lcd.value > last_cited.value:
                            last_cited = lcd
                            if rank:
                                latest_rank = rank
                            if role:
                                latest_role = role
                            if title:
                                latest_title = title
                    else:
                        last_cited = lcd
                        if rank:
                            latest_rank = rank
                        if role:
                            latest_role = role
                        if title:
                            latest_title = title

            # Convert sets to lists, for indexing
            division_ids, countries = list(division_ids), list(countries)
            roles, ranks, titles = list(roles), list(ranks), list(titles)

            # Add some attributes to the global index
            for attr in (roles, ranks, titles, countries):
                content.extend(attr)

            content = '; '.join(content)

            if first_cited:
                # For now, convert fuzzy dates to use Jan and/or the 1st
                first_cited = dateformat.format(first_cited.value, 'Y-m-d').replace('-00', '-01')
                first_cited += 'T00:00:00Z'

            if last_cited:
                last_cited = dateformat.format(last_cited.value, 'Y-m-d').replace('-00', '-01')
                last_cited += 'T00:00:00Z'

            document = {
                'id': person_id,
                'entity_type': 'Person',
                'content': content,
                'location': '',  # disabled until we implement map search
                'country_ss': countries,
                'division_id_ss': division_ids,
                'person_title_ss': titles,
                'person_name_s': name,
                'person_alias_ss': aliases,
                'person_role_ss': roles,
                'person_rank_ss': ranks,
                'person_title_ss': titles,
                'person_current_rank_s': latest_rank,
                'person_current_role_s': latest_role,
                'person_current_title_s': latest_title,
                'person_first_cited_dt': first_cited,
                'person_last_cited_dt': last_cited,
                'start_date_dt': first_cited,
                'end_date_dt': last_cited,
                '_text_': content
            }

            documents.append(document)

            if update:
                self.updated_count += 1
            else:
                self.added_count += 1

        self.add_to_index(documents)

    def index_violations(self, doc_id=None, update=False):
        self.stdout.write(self.style.HTTP_NOT_MODIFIED('\n Indexing violations ... '))

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

            for lst in ([perp_name], perp_aliases, [perp_org_name], perp_org_aliases):
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

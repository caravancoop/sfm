import os
import json
from collections import OrderedDict
import re
from uuid import uuid4
from datetime import datetime, date
import csv
import string

import httplib2

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

import datefinder

from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction, IntegrityError, connection
from django.db.utils import DataError, ProgrammingError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.management import call_command
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.conf import settings

from django_date_extensions.fields import ApproximateDateField

from dateparser import parse as dateparser

import reversion

from countries_plus.models import Country

from source.models import Source, AccessPoint
from organization.models import Organization, OrganizationAlias, \
    OrganizationClassification, OrganizationName, OrganizationRealStart

from sfm_pc.utils import (import_class, get_osm_by_id, get_hierarchy_by_id,
                          CONFIDENCE_MAP, execute_sql)

from emplacement.models import Emplacement, EmplacementOpenEnded, EmplacementRealStart
from association.models import Association, AssociationOpenEnded, AssociationRealStart
from composition.models import Composition, CompositionOpenEnded, CompositionRealStart
from person.models import Person, PersonExtra, PersonName, PersonAlias
from membershipperson.models import (MembershipPerson, Role, Rank,
                                     MembershipPersonRealStart,
                                     MembershipPersonRealEnd)
from membershiporganization.models import (MembershipOrganization,
                                           MembershipOrganizationRealStart,
                                           MembershipOrganizationRealEnd)
from violation.models import Violation, ViolationPerpetrator, \
    ViolationPerpetratorOrganization, ViolationDescription

from location.models import Location

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


class Command(BaseCommand):
    help = 'Import data from Google Drive Spreadsheet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--doc_id',
            dest='doc_id',
            default='1o-K13Od1pGc7FOQ-JS8LJW9Angk3_UPZHTmOU7hD3wU',
            help='Import data from specified Google Drive Document'
        )
        parser.add_argument(
            '--source_doc_id',
            dest='source_doc_id',
            default='15lChqP4cKsjk8uUbUTaUA5gOUM09-t9YMIODORHw--8',
            help='Import source data from specified Google Drive Document'
        )
        parser.add_argument(
            '--entity-types',
            dest='entity_types',
            default='organization,person,event',
            help='Comma separated list of entity types to import'
        )
        parser.add_argument(
            '--country_code',
            dest='country_code',
            default='mx',
            help='Two letter ISO code for the country that the Google Sheets are about'
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            dest='flush',
            default=False,
            help='Flush the existing database before importing data.'
        )
        parser.add_argument(
            '--start',
            dest='start',
            default=1,
            help='First row to begin parsing (for debugging)'
        )
        parser.add_argument(
            '--folder',
            dest='folder',
            help='Path to a folder containing data (for testing)'
        )

    def sourcesList(self, obj, attribute):
        sources = [s for s in getattr(obj, attribute).get_sources()]
        return list(set(s for s in sources if s))

    def get_credentials(self):
        '''make sure relevant accounts have access to the sheets at console.developers.google.com'''

        this_dir = os.path.dirname(__file__)
        secrets_path = os.path.join(this_dir, 'credentials.json')

        credentials = ServiceAccountCredentials.from_json_keyfile_name(secrets_path,
                                                                       SCOPES)
        return credentials

    def disconnectSignals(self):
        from django.db.models.signals import post_save
        from complex_fields.base_models import object_ref_saved
        from sfm_pc.signals import (
            update_organization_index, update_person_index, update_violation_index,
            update_membership_index, update_composition_index, update_source_index
        )

        object_ref_saved.disconnect(receiver=update_organization_index, sender=Organization)
        object_ref_saved.disconnect(receiver=update_person_index, sender=Person)
        object_ref_saved.disconnect(receiver=update_violation_index, sender=Violation)
        object_ref_saved.disconnect(receiver=update_membership_index, sender=MembershipPerson)
        object_ref_saved.disconnect(receiver=update_composition_index, sender=Composition)
        post_save.disconnect(receiver=update_source_index, sender=Source)

    def connectSignals(self):
        from django.db.models.signals import post_save
        from complex_fields.base_models import object_ref_saved
        from sfm_pc.signals import (
            update_organization_index, update_person_index, update_violation_index,
            update_membership_index, update_composition_index, update_source_index
        )

        object_ref_saved.connect(receiver=update_organization_index, sender=Organization)
        object_ref_saved.connect(receiver=update_person_index, sender=Person)
        object_ref_saved.connect(receiver=update_violation_index, sender=Violation)
        object_ref_saved.connect(receiver=update_membership_index, sender=MembershipPerson)
        object_ref_saved.connect(receiver=update_composition_index, sender=Composition)
        post_save.connect(receiver=update_source_index, sender=Source)

    def handle(self, *args, **options):

        if options['flush']:
            self.stdout.write(self.style.SUCCESS('Dropping current database...'))

            # Flush database
            this_dir = os.path.abspath(os.path.dirname(__file__))
            flush_sql = os.path.join(this_dir, 'flush', 'flush.sql')
            execute_sql(flush_sql)

            # Recreate country codes
            call_command('update_countries_plus')

        # Get a handle on the "user" that will be doing the work
        importer_user = settings.IMPORTER_USER
        try:
            self.user = User.objects.create_user(importer_user['username'],
                                                 email=importer_user['email'],
                                                 password=importer_user['password'])
        except IntegrityError:
            self.user = User.objects.get(username=importer_user['username'])

        # Disconnect post save signals
        self.disconnectSignals()

        # Set the country code for the work
        self.country_code = options['country_code']

        if options.get('folder'):
            self.stdout.write('Loading data from folder {}...'.format(options['folder']))
            all_sheets = self.get_sheets_from_folder(options['folder'])
        else:
            self.stdout.write('Loading data from Google Sheets...')
            all_sheets = self.get_sheets_from_doc(options['doc_id'], options['source_doc_id'])

        self.create_sources(all_sheets['source'])

        skippers = ['Play Copy of Events']
        start = int(options['start'])

        # These are used for the mapping that we need to make below
        entity_mapping_entities = [
            ('organization', 'unit:id:admin', 'unit:name'),
            ('person', 'person:id:admin', 'person:name'),
        ]

        # Create entity maps for persons and units
        for entity_type, id_key, name_key in entity_mapping_entities:

            sheets = all_sheets[entity_type]

            for sheet in sheets.values():

                entity_map = {}

                for row in sheet[start:]:
                    if row:
                        entity_name = row[name_key]
                        entity_uuid = row[id_key]
                        entity_map[entity_name] = entity_uuid

                setattr(self, '{}_entity_map'.format(entity_type), entity_map)

        for entity_type in options['entity_types'].split(','):

            sheets = all_sheets[entity_type]

            for title, sheet in sheets.items():

                self.stdout.write(self.style.SUCCESS('Creating {0}s from {1} ... '.format(entity_type, title)))
                self.current_sheet = title

                if not title in skippers:

                    # Skip header row
                    for index, row in enumerate(sheet[start:]):
                        if row:
                            self.current_row = index + start
                            getattr(self, 'create_{}'.format(entity_type))(row)

        data_src = options['folder'] if options.get('folder') else options['doc_id']
        self.stdout.write(self.style.SUCCESS('Successfully imported data from {}'.format(data_src)))
        # connect post save signals
        self.connectSignals()

    def get_sheets_from_doc(self, doc_id, source_doc_id):
        """
        Load data from Google Sheets. Required params include a Google Doc ID
        for top-level entities and a Doc ID for sources.
        """
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = build('sheets', 'v4', http=http)

        result = service.spreadsheets().get(
            spreadsheetId=doc_id,
            includeGridData=False
        ).execute()
        sheets = result['sheets']
        sheet_mapping = {}

        for sheet in sheets:
            title = sheet['properties']['title']
            sheet_data = service.spreadsheets().values().get(
                spreadsheetId=doc_id,
                range=title + sheet_range
            ).execute()
            sheet_mapping[title] = sheet_data['values']

        org_sheets = {title: self.format_dict_reader(data)
                      for title, data in sheet_mapping.items()
                      if 'units' in title.lower()}
        person_sheets = {title: self.format_dict_reader(data)
                         for title, data in sheet_mapping.items()
                         if 'persons' in title.lower() and 'persons_extra' not in title.lower()}
        person_extra_sheets = {title: self.format_dict_reader(data)
                               for title, data in sheet_mapping.items()
                               if 'persons_extra' in title.lower()}
        event_sheets = {title: self.format_dict_reader(data)
                        for title, data in sheet_mapping.items()
                        if 'events' in title.lower()}

        # Get data about sources
        source_sheet = service.spreadsheets().values().get(
            spreadsheetId=source_doc_id
        ).execute()

        return {
            'organization': org_sheets,
            'person': person_sheets,
            'person_extra': person_extra_sheets,
            'event': event_sheets,
            'source': source_sheet,
        }

    def get_sheets_from_folder(self, folder):
        """
        Load data from a folder on disk. Data must be stored as CSV files with the
        name of the entities represented therein (e.g. 'person.csv') and must be
        stored under the directory represented by the path string 'folder'.
        """
        all_sheets = {}
        entities = (
            ('organization', 'units', 'orgs'),
            ('person', 'persons', 'persons'),
            ('person_extra', 'persons_extra', 'persons_extra'),
            ('event', 'incidents', 'events'),
            ('source', 'sources', 'values')
        )
        for entity_type, filename, title in entities:
            path = os.path.join(folder, filename + '.csv')
            if not os.path.isfile(path):
                raise OSError('Required file {path} not found.'.format(path=path))

            with open(path) as fobj:
                reader = csv.reader(fobj)
                # We could use csv.DictReader directly here, but instead use
                # the format_dict_reader convenience method to test it
                records = self.format_dict_reader(list(reader))

            # Match the Google Sheets API response format
            all_sheets[entity_type] = {title: records}

        return all_sheets

    def format_dict_reader(self, lst):
        """
        Format a nested list, 'lst', as a list of dictionaries (like a
        csv.DictReader object).
        """
        header = lst[0]
        return [dict(zip(header, row)) for row in lst[1:]]

    def log_error(self, message):
        log_message = message + ' (context: Sheet {0}, Row {1})'.format(self.current_sheet, self.current_row)
        self.stdout.write(self.style.ERROR(log_message))
        file_name = '{}-errors.csv'.format(slugify(self.current_sheet))
        if not os.path.isfile(file_name):
            with open(file_name, 'w') as f:
                header = ['row', 'message']
                writer = csv.writer(f)
                writer.writerow(header)

        with open(file_name, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([self.current_row,
                             message])

    def get_confidence(self, confidence_key):
        key = confidence_key.strip().lower()
        if key:
            return CONFIDENCE_MAP[key]
        else:
            return 1

    def parse_date(self, value):
        parsed = None

        # Map legal input formats to the way that we want to
        # store them in the database
        formats = {
            '%Y-%m-%d': '%Y-%m-%d',
            '%Y': '%Y-0-0',
            '%Y-%m': '%Y-%m-0',
            '%B %Y': '%Y-%m-0',
            '%m/%Y': '%Y-%m-0',
            '%m/%d/%Y': '%Y-%m-%d',
        }

        for in_format, out_format in formats.items():
            try:
                parsed_input = datetime.strptime(value, in_format)

                if datetime.today() < parsed_input:
                    self.log_error('Date {value} is in the future'.format(value=value))
                    return None

                parsed = datetime.strftime(parsed_input, out_format)
                break
            except ValueError:
                pass

        return parsed

    def create_organization(self, org_data):
        organization = None

        org_positions = {
            'Name': {
                'value': 'unit:name',
                'confidence': 'unit:name:confidence',
                'source': 'unit:name:source',
            },
            'Alias': {
                'value': 'unit:other_names',
                'confidence': 'unit:other_names:confidence',
                'source': 'unit:other_names:source',
            },
            'Classification': {
                'value': 'unit:classification',
                'confidence': 'unit:classification:confidence',
                'source': 'unit:classification:source',
            },
            'DivisionId': {
                'value': 'unit:country',
                'confidence': 'unit:country:confidence',
                'source': 'unit:country:source',
            },
            'FirstCitedDate': {
                'value': 'unit:first_cited_date',
                'day': 'unit:first_cited_date_day',
                'month': 'unit:first_cited_date_month',
                'year': 'unit:first_cited_date_year',
                'confidence': 'unit:first_cited_date:confidence',
                'source': 'unit:first_cited_date:source',
            },
            'RealStart': {
                'value': 'unit:first_cited_date_start',
                'confidence': 'unit:first_cited_date:confidence',
                'source': None,
            },
            'LastCitedDate': {
                'value': 'unit:last_cited_date',
                'day': 'unit:last_cited_date_day',
                'month': 'unit:last_cited_date_month',
                'year': 'unit:last_cited_date_year',
                'confidence': 'unit:last_cited_date:confidence',
                'source': 'unit:last_cited_date:source',
            },
            'OpenEnded': {
                'value': 'unit:last_cited_date_open',
                'confidence': 'unit:last_cited_date:confidence',
                'source': None,
            },
            'Headquarters': {
                'value': 'unit:base_name',
                'confidence': 'unit:base_name:confidence',
                'source': 'unit:base_name:source',
            }
        }

        composition_positions = {
            'Parent': {
                'value': 'unit:related_unit',
                'confidence': 'unit:related_unit:confidence',
                'source': 'unit:related_unit:source',
            },
            'Classification': {
                'value': 'unit:related_unit_class',
                'confidence': 'unit:related_unit_class:confidence',
                'source': 'unit:related_unit_class:source',
            },
            'StartDate': {
                'value': 'unit:related_unit_first_cited_date',
                'day': 'unit:related_unit_first_cited_date_day',
                'month': 'unit:related_unit_first_cited_date_month',
                'year': 'unit:related_unit_first_cited_date_year',
                'confidence': 'unit:related_unit_first_cited_date:confidence',
                'source': 'unit:related_unit_first_cited_date:source',
            },
            'RealStart': {
                'value': 'unit:related_unit_first_cited_date_start',
                'confidence': 'unit:related_unit_first_cited_date:confidence',
                'source': None,
            },
            'EndDate': {
                'value': 'unit:related_unit_last_cited_date',
                'day': 'unit:related_unit_last_cited_date_day',
                'month': 'unit:related_unit_last_cited_date_month',
                'year': 'unit:related_unit_last_cited_date_year',
                'confidence': 'unit:related_unit_last_cited_date:confidence',
                'source': 'unit:related_unit_last_cited_date:source',
            },
            'OpenEnded': {
                'value': 'unit:related_unit_open',
                'confidence': 'unit:related_unit_last_cited_date:confidence',
                'source': None,
            },
        }

        area_positions = {
            'OSMId': {
                'value': 'unit:area_ops_id',
                'confidence': 'unit:area_ops_name:confidence',
                'source': 'unit:area_ops_name:source',
            },
        }

        site_positions = {
            'OSMId': {
                'value': 'unit:site_nearest_settlement_id',
                'confidence': 'unit:site_nearest_settlement_name:confidence',
                'source': 'unit:site_nearest_settlement_name:source',
            },
        }

        membership_positions = {
            'OrganizationOrganization': {
                'value': 'unit:membership_name',
                'confidence': 'unit:membership_name:confidence',
                'source': 'unit:membership_name:source',
            },
            'FirstCitedDate': {
                'value': 'unit:membership_first_cited_date',
                'day': 'unit:membership_first_cited_date_day',
                'month': 'unit:membership_first_cited_date_month',
                'year': 'unit:membership_first_cited_date_year',
                'confidence': 'unit:membership_first_cited_date:confidence',
                'source': 'unit:membership_first_cited_date:source',
            },
            'RealStart': {
                'value': 'unit:membership_first_cited_date_start',
                'confidence': 'unit:membership_first_cited_date:confidence',
                'source': None,
            },
            'LastCitedDate': {
                'value': 'unit:membership_last_cited_date',
                'day': 'unit:membership_last_cited_date_day',
                'month': 'unit:membership_last_cited_date_month',
                'year': 'unit:membership_last_cited_date_year',
                'confidence': 'unit:membership_last_cited_date:confidence',
                'source': 'unit:membership_last_cited_date:source',
            },
            'RealEnd': {
                'value': 'unit:membership_last_cited_date_end',
                'confidence': 'unit:membership_last_cited_date:confidence',
                'source': None,
            },
        }

        # Need to get or create name first

        try:
            name_value = org_data[org_positions['Name']['value']]
            confidence = org_data[org_positions['Name']['confidence']]
            source = org_data[org_positions['Name']['source']]
        except IndexError:
            self.log_error('Row seems to be empty')
            return None

        try:
            country_code = org_data[org_positions['DivisionId']['value']]
        except IndexError:
            self.log_error('Country code missing')
            return None

        if confidence and source:

            try:
                confidence = self.get_confidence(confidence)
            except KeyError:
                confidence = None

            sources = self.get_sources(source)
            self.stdout.write(self.style.SUCCESS('Working on {}'.format(name_value)))

            if confidence and sources:

                division_id = 'ocd-division/country:{}'.format(country_code)
                division_confidence = self.get_confidence(
                    org_data[org_positions['DivisionId']['confidence']]
                )
                division_sources = self.get_sources(
                    org_data[org_positions['DivisionId']['source']]
                )

                org_info = {
                    'Organization_OrganizationName': {
                        'value': name_value,
                        'confidence': confidence,
                        'sources': sources.copy()
                    },
                    'Organization_OrganizationDivisionId': {
                        'value': division_id,
                        'confidence': division_confidence,
                        'sources': division_sources,
                    }
                }

                try:
                    uuid = self.organization_entity_map[name_value]
                except KeyError:
                    self.log_error('Could not find "{}" in list of organization names'.format(name_value))
                    return None

                try:
                    organization = Organization.objects.get(uuid=uuid)
                    existing_sources = self.sourcesList(organization, 'name')
                    org_info["Organization_OrganizationName"]['sources'] += existing_sources

                    organization.update(org_info)

                except Organization.DoesNotExist:
                    organization = Organization.objects.create(uuid=uuid,
                                                               published=True)
                    organization.update(org_info)

                org_attributes = ['Alias', 'Classification', 'OpenEnded', 'Headquarters']

                for attr in org_attributes:

                    self.make_relation(attr,
                                       org_positions[attr],
                                       org_data,
                                       organization)

                self.make_relation('FirstCitedDate',
                                   org_positions['FirstCitedDate'],
                                   org_data,
                                   organization,
                                   date=True)

                self.make_relation('LastCitedDate',
                                   org_positions['LastCitedDate'],
                                   org_data,
                                   organization,
                                   date=True)

                self.make_real_date(data=org_data,
                                    position=org_positions['RealStart']['value'],
                                    model=OrganizationRealStart,
                                    attribute='realstart',
                                    object_ref=organization)

                # Create Emplacements
                try:
                    site_osm_id = org_data[site_positions['OSMId']['value']]
                except IndexError:
                    # self.log_error('No Site OSM info for {}'.format(organization.name))
                    site_osm_id = None

                if site_osm_id:

                    emplacement = self.make_emplacement(site_osm_id,
                                                        org_data,
                                                        organization)

                # Create Areas
                try:
                    area_osm_id = org_data[area_positions['OSMId']['value']]
                except IndexError:
                    # self.log_error('No Area OSM info for {}'.format(organization.name))
                    area_osm_id = None

                if area_osm_id:

                    area = self.make_area(area_osm_id,
                                          org_data,
                                          organization)

                # Create Compositions

                try:
                    parent_org_name = org_data[composition_positions['Parent']['value']]
                except IndexError:
                    parent_org_name = None

                if parent_org_name:

                    try:
                        parent_confidence = self.get_confidence(org_data[composition_positions['Parent']['confidence']])
                    except (IndexError, KeyError):
                        self.log_error('Parent organization for {} does not have confidence'.format(organization.name))
                        parent_confidence = None

                    try:
                        parent_sources = self.get_sources(org_data[composition_positions['Parent']['source']])
                    except IndexError:
                        self.log_error('Parent organization for {} does not have a source'.format(organization.name))
                        parent_sources = None

                    if parent_confidence and parent_sources:
                        parent_org_info = {
                            'Organization_OrganizationName': {
                                'value': parent_org_name,
                                'confidence': parent_confidence,
                                'sources': parent_sources
                            },
                            'Organization_OrganizationDivisionId': {
                                'value': division_id,
                                'confidence': division_confidence,
                                'sources': division_sources,
                            },
                        }

                        try:
                            uuid = self.organization_entity_map[parent_org_name]
                        except KeyError:
                            self.log_error('Could not find "{}" in list of organization names'.format(parent_org_name))
                            return None

                        try:
                            parent_organization = Organization.objects.get(uuid=uuid)
                            existing_sources = self.sourcesList(parent_organization, 'name')
                            parent_org_info["Organization_OrganizationName"]['sources'] += existing_sources

                            parent_organization.update(parent_org_info)

                        except Organization.DoesNotExist:
                            parent_organization = Organization.objects.create(uuid=uuid,
                                                                              published=True)
                            parent_organization.update(parent_org_info)

                        comp_info = {
                            'Composition_CompositionParent': {
                                'value': parent_organization,
                                'confidence': parent_confidence,
                                'sources': parent_sources
                            },
                            'Composition_CompositionChild': {
                                'value': organization,
                                'confidence': parent_confidence,
                                'sources': parent_sources,
                            },
                        }

                        try:
                            composition = Composition.objects.get(compositionparent__value=parent_organization,
                                                                  compositionchild__value=organization)
                        except Composition.DoesNotExist:
                            composition = Composition.create(comp_info)

                        self.make_relation('StartDate',
                                           composition_positions['StartDate'],
                                           org_data,
                                           composition,
                                           date=True)

                        self.make_relation('EndDate',
                                           composition_positions['EndDate'],
                                           org_data,
                                           composition,
                                           date=True)

                        self.make_real_date(data=org_data,
                                            position=composition_positions['RealStart']['value'],
                                            model=CompositionRealStart,
                                            attribute='realstart',
                                            object_ref=composition)

                        self.make_relation('OpenEnded',
                                           composition_positions['OpenEnded'],
                                           org_data,
                                           composition)

                        self.make_relation('Classification',
                                           composition_positions['Classification'],
                                           org_data,
                                           composition)


                    else:
                        self.log_error('Parent organization for {} does not have source or confidence'.format(organization.name))

                # Make memberships

                try:
                    member_org_name = org_data[membership_positions['OrganizationOrganization']['value']]
                except IndexError:
                    member_org_name = None

                if member_org_name:
                    try:
                        confidence = self.get_confidence(org_data[membership_positions['OrganizationOrganization']['confidence']])
                    except (IndexError, KeyError):
                        self.log_error('Member organization for {} does not have confidence'.format(member_org_name))
                        confidence = None

                    try:
                        sources = self.get_sources(org_data[membership_positions['OrganizationOrganization']['source']])
                    except IndexError:
                        self.log_error('Member organization for {} does not have a source'.format(member_org_name))
                        sources = None

                    if confidence and sources:

                        member_org_info = {
                            'Organization_OrganizationName': {
                                'value': member_org_name,
                                'confidence': confidence,
                                'sources': sources.copy(),
                            },
                            'Organization_OrganizationDivisionId': {
                                'value': division_id,
                                'confidence': division_confidence,
                                'sources': division_sources,
                            },
                        }

                        try:
                            uuid = self.organization_entity_map[member_org_name]
                        except KeyError:
                            self.log_error('Could not find "{}" in list of organization names'.format(member_org_name))
                            return None

                        try:
                            member_organization = Organization.objects.get(uuid=uuid)
                            existing_sources = self.sourcesList(member_organization, 'name')
                            member_org_info["Organization_OrganizationName"]['sources'] += existing_sources

                            member_organization.update(member_org_info)

                        except Organization.DoesNotExist:
                            member_organization = Organization.objects.create(uuid=uuid,
                                                                              published=True)
                            member_organization.update(member_org_info)

                        membership_info = {
                            'MembershipOrganization_MembershipOrganizationMember': {
                                'value': organization,
                                'confidence': confidence,
                                'sources': sources.copy()
                            },
                            'MembershipOrganization_MembershipOrganizationOrganization': {
                                'value': member_organization,
                                'confidence': confidence,
                                'sources': sources.copy()
                            },
                        }

                        try:
                            date_parts = [
                                org_data[membership_positions['FirstCitedDateYear']['value']],
                                org_data[membership_positions['FirstCitedDateMonth']['value']],
                                org_data[membership_positions['FirstCitedDateDay']['value']]
                            ]
                            fcd = self.parse_date('-'.join(filter(None, date_parts)))
                        except IndexError:
                            fcd = None

                        try:
                            date_parts = [
                                org_data[membership_positions['LastCitedDateYear']['value']],
                                org_data[membership_positions['LastCitedDateMonth']['value']],
                                org_data[membership_positions['LastCitedDateDay']['value']]
                            ]
                            lcd = self.parse_date('-'.join(filter(None, date_parts)))
                        except IndexError:
                            lcd = None

                        try:
                            membership = MembershipOrganization.objects.get(membershiporganizationmember__value=organization,
                                                                            membershiporganizationorganization__value=member_organization,
                                                                            membershiporganizationfirstciteddate__value=fcd,
                                                                            membershiporganizationlastciteddate__value=lcd)
                            sources = set(self.sourcesList(membership, 'member') + \
                                          self.sourcesList(membership, 'organization'))
                            membership_info['MembershipOrganization_MembershipOrganizationMember']['sources'] += sources
                            membership.update(membership_info)

                        except MembershipOrganization.DoesNotExist:
                            membership = MembershipOrganization.create(membership_info)

                        self.make_relation('LastCitedDate',
                                           membership_positions['LastCitedDate'],
                                           org_data,
                                           membership,
                                           date=True)

                        self.make_real_date(data=org_data,
                                            position=membership_positions['RealEnd']['value'],
                                            model=MembershipOrganizationRealEnd,
                                            attribute='realend',
                                            object_ref=membership)

                        self.make_relation('FirstCitedDate',
                                           membership_positions['FirstCitedDate'],
                                           org_data,
                                           membership,
                                           date=True)

                        self.make_real_date(data=org_data,
                                            position=membership_positions['RealStart']['value'],
                                            model=MembershipOrganizationRealStart,
                                            attribute='realend',
                                            object_ref=membership)

                        membership.save()

                    else:
                        self.log_error('Member organization for {} does not have source or confidence'.format(member_org_name))


                self.stdout.write(self.style.SUCCESS('Created {}'.format(organization.get_value())))

            else:
                self.log_error('{} did not have a confidence or source'.format(name_value))

        else:
            missing = []
            if not confidence:
                missing.append('confidence')
            if not source:
                missing.append('sources')

            self.log_error('{0} did not have {1}'.format(name_value, ', '.join(missing)))

        return organization

    def make_relation(self,
                      field_name,
                      positions,
                      data,
                      instance,
                      required=False,
                      require_confidence=True,
                      date=False,
                      multiple=True):

        value_position = positions['value']

        if not require_confidence:
            confidence_required = False
        else:
            confidence_required = instance.confidence_required

        try:
            confidence_position = positions['confidence']
        except KeyError:
            confidence_position = None

            if confidence_required:
                self.log_error('No confidence for {}'.format(field_name))
                return None

        source_position = positions['source']

        try:
            if not date:
                value = data[value_position]
            else:
                date_parts = [
                    data[value_position + '_year'],
                    data[value_position + '_month'],
                    data[value_position + '_day']
                ]
                value = '-'.join(filter(None, date_parts))
            value = value.strip()
        except IndexError:
            value = None

        if required and not value:
            self.log_error('No {0} information for {1}'.format(field_name, instance.get_value()))
            return None

        elif value:

            app_name = instance._meta.model_name
            model_name = instance._meta.object_name

            import_path = '{app_name}.models.{model_name}{field_name}'

            relation_path = import_path.format(app_name=app_name,
                                               model_name=model_name,
                                               field_name=field_name)

            relation_model = import_class(relation_path)

            source_required = getattr(relation_model, 'source_required', False)

            try:
                confidence = self.get_confidence(data[confidence_position])
            except (KeyError, IndexError, TypeError):
                confidence = 1
                if confidence_required:
                    self.log_error('No confidence for {}'.format(field_name))
                    return None

            if not source_position:

                if source_required:
                    self.log_error('No source for {}'.format(field_name))
                    return None
                else:
                    sources = []
            else:

                try:
                    sources = self.get_sources(data[source_position])
                except IndexError:
                    if source_required:
                        self.log_error('No source for {}'.format(field_name))
                        return None
                    else:
                        sources = []

            if (sources or not source_required) and (confidence or not confidence_required):

                if isinstance(relation_model._meta.get_field('value'), models.ForeignKey):
                    value_rel_path_fmt = '{app_name}.models.{field_name}'
                    value_rel_path = value_rel_path_fmt.format(app_name=app_name,
                                                               field_name=field_name)

                    try:
                        value_model = import_class(value_rel_path)
                    except AttributeError:
                        value_rel_path = value_rel_path_fmt.format(app_name=app_name,
                                                                   field_name='Context')
                        value_model = import_class(value_rel_path)

                    # Split on semicolons if multiple values are supported
                    values = [value] if not multiple else [val.strip() for val in value.split(';') if val.strip()]
                    for value_text in values:

                        value_obj, created = value_model.objects.get_or_create(value=value_text)

                        relation_instance, created = relation_model.objects.get_or_create(value=value_obj,
                                                                                          object_ref=instance,
                                                                                          lang='en')
                        if created:

                            for source in sources:
                                relation_instance.accesspoints.add(source)
                                relation_instance.sources.add(source.source)

                            with reversion.create_revision():
                                relation_instance.confidence = confidence
                                relation_instance.save()
                                reversion.set_user(self.user)

                elif isinstance(relation_model._meta.get_field('value'), ApproximateDateField):
                    parsed_value = self.parse_date(value)

                    if parsed_value:
                        relation_instance, created = relation_model.objects.get_or_create(value=parsed_value,
                                                                                          object_ref=instance,
                                                                                          lang='en')
                        if created:

                            for source in sources:
                                relation_instance.accesspoints.add(source)
                                relation_instance.sources.add(source.source)

                            with reversion.create_revision():
                                relation_instance.confidence = confidence
                                relation_instance.save()
                                reversion.set_user(self.user)

                    else:
                        self.log_error('Expected a date for {app_name}.models.{field_name} but got {value}'.format(app_name=app_name,
                                                                                                                   field_name=field_name,
                                                                                                                   value=value))
                        return None

                else:

                    # Split on semicolons if multiple values are supported.
                    values = [value] if not multiple else [val.strip() for val in value.split(';') if val.strip()]
                    for val in values:
                        relation_instance, created = relation_model.objects.get_or_create(value=val.strip(),
                                                                                          object_ref=instance,
                                                                                          lang='en')
                        if created:

                            for source in sources:
                                relation_instance.accesspoints.add(source)
                                relation_instance.sources.add(source.source)

                            with reversion.create_revision():
                                relation_instance.confidence = confidence
                                relation_instance.save()
                                reversion.set_user(self.user)

            else:
                missing = []
                if not confidence and instance.confidence_required:
                    missing.append('confidence')
                if not sources:
                    missing.append('sources')

                message = '{field_name} from {app_name}.{model_name} does not have {missing}'.format(field_name=field_name,
                                                                                                     app_name=app_name,
                                                                                                     model_name=model_name,
                                                                                                     missing=', '.join(missing))
                self.log_error(message)

            return None

    def make_area(self, osm_id, org_data, organization):

        positions = {
            'OSMName': {
                'value': 'unit:area_ops_name',
                'confidence': 'unit:area_ops_name:confidence',
                'source': 'unit:area_ops_name:source',
            },
        }

        relation_positions = {
            'StartDate': {
                'value': 'unit:area_ops_first_cited_date',
                'day': 'unit:area_ops_first_cited_date_day',
                'month': 'unit:area_ops_first_cited_date_month',
                'year': 'unit:area_ops_first_cited_date_year',
                'confidence': 'unit:area_ops_first_cited_date:confidence',
                'source': 'unit:area_ops_first_cited_date:source',
            },
            'RealStart': {
                'value': 'unit:area_ops_first_cited_date_start',
                'confidence': 'unit:area_ops_first_cited_date:confidence',
                'source': None,
            },
            'EndDate': {
                'value': 'unit:area_ops_last_cited_date',
                'day': 'unit:area_ops_last_cited_date_day',
                'month': 'unit:area_ops_last_cited_date_month',
                'year': 'unit:area_ops_last_cited_date_year',
                'confidence': 'unit:area_ops_last_cited_date:confidence',
                'source': 'unit:area_ops_last_cited_date:source',
            },
            'OpenEnded': {
                'value': 'unit:area_ops_open',
                'confidence': 'unit:area_ops_last_cited_date:confidence',
                'source': None,
            },
        }

        try:
            geo = get_osm_by_id(osm_id)
        except DataError:
            self.log_error('OSM ID for Area does not seem valid: {}'.format(osm_id))
            geo = None


        if geo:
            country_code = geo.country_code.lower()

            division_id = 'ocd-division/country:{}'.format(country_code)

            area, created = Location.objects.get_or_create(id=geo.id)

            if created:
                area.name = geo.name
                area.geometry = geo.geometry
                area.division_id = division_id

                if area.feature_type == 'point':
                    area.feature_type = 'node'
                else:
                    area.feature_type = 'relation'

                area.save()

            try:
                area_confidence = self.get_confidence(org_data[positions['OSMName']['confidence']])
            except (IndexError, KeyError):
                self.log_error('OSMName for Area for {} does not have confidence'.format(organization.name))
                return None

            try:
                area_sources = self.get_sources(org_data[positions['OSMName']['source']])
            except IndexError:
                self.log_error('OSMName for Area for {} does not have source'.format(organization.name))
                return None

            area_info = {
                'Association_AssociationOrganization': {
                    'value': organization,
                    'confidence': area_confidence,
                    'sources': area_sources
                },
                'Association_AssociationArea': {
                    'value': area,
                    'confidence': area_confidence,
                    'sources': area_sources
                },
            }

            try:
                assoc = Association.objects.get(associationorganization__value=organization,
                                                associationarea__value=area)
                assoc.update(area_info)
            except Association.DoesNotExist:
                assoc = Association.create(area_info)

            for field_name, positions in relation_positions.items():

                if field_name == 'StartDate':
                    self.make_relation(field_name,
                                       positions,
                                       org_data,
                                       assoc,
                                       date=True)

                elif field_name == 'EndDate':
                    self.make_relation(field_name,
                                       positions,
                                       org_data,
                                       assoc,
                                       date=True)

                elif field_name == 'RealStart':
                    self.make_real_date(data=org_data,
                                        position=positions['value'],
                                        model=AssociationRealStart,
                                        attribute='realstart',
                                        object_ref=assoc)

                else:
                    self.make_relation(field_name,
                                       positions,
                                       org_data,
                                       assoc)

    def make_emplacement(self,
                         osm_id,
                         org_data,
                         organization):

        positions = {
            'AdminLevel1': {
                'value': 'unit:site_first_admin_area_name',
                'osmid': 'unit:site_first_admin_area_id',
                'confidence': 'unit:site_first_admin_area_name:confidence',
                'source': 'unit:site_first_admin_area_name:source',
            },
            # This doesn't correspond directly to a model attribute
            # but we'll use it to unpack data about the highest
            # level of resolution available to us
            'ExactLocation': {
                'lng_or_name': 'unit:site_exact_location_name_longitude',
                'lat_or_id': 'unit:site_exact_location_id_latitude',
                'confidence': 'unit:site_exact_location:confidence',
                'source': 'unit:site_exact_location:source',
            },
            'Headquarters': {
                'value': 'unit:base_name',
                'confidence': 'unit:base_name:confidence',
                'source': 'unit:base_name:source',
            },
            'AdminName': {
                'value': 'unit:site_nearest_settlement_name',
                'confidence': 'unit:site_nearest_settlement_name:confidence',
                'source': 'unit:site_nearest_settlement_name:source',
            },
            'AdminId': {
                'value': 'unit:site_nearest_settlement_id',
                'confidence': 'unit:site_nearest_settlement_name:confidence',
                'source': 'unit:site_nearest_settlement_name:source',
            }
        }

        relation_positions = {
            'StartDate': {
                'value': 'unit:site_first_cited_date',
                'day': 'unit:site_first_cited_date_day',
                'month': 'unit:site_first_cited_date_month',
                'year': 'unit:site_first_cited_date_year',
                'confidence': 'unit:site_first_cited_date:confidence',
                'source': 'unit:site_first_cited_date:source',
            },
            'RealStart': {
                'value': 'unit:site_first_cited_date_founding',
                'confidence': 'unit:site_first_cited_date:confidence',
                'source': None
            },
            'EndDate': {
                'value': 'unit:site_last_cited_date',
                'day': 'unit:site_last_cited_date_day',
                'month': 'unit:site_last_cited_date_month',
                'year': 'unit:site_last_cited_date_year',
                'confidence': 'unit:site_last_cited_date:confidence',
                'source': 'unit:site_last_cited_date:source',
            },
            'OpenEnded': {
                'value': 'unit:site_open',
                'confidence': 'unit:site_last_cited_date:confidence',
                'source': None
            }
        }

        exact_location = self.get_exact_location(positions, org_data)

        if exact_location.get('id') and exact_location.get('name'):
            osm_id = exact_location['id']
            site_name = exact_location['name']
        else:
            osm_id = org_data[positions['AdminId']['value']]
            site_name = org_data[positions['AdminName']['value']]

        try:
            osm_geo = get_osm_by_id(osm_id)
        except DataError:
            osm_geo = None
            self.log_error('OSM ID for Site {1} does not seem valid: {2}'.format(site_name, osm_id))

        if osm_geo:

            site = self.get_or_create_site(osm_geo, exact_location, org_data, positions)
            confidence = self.get_confidence(org_data[positions['AdminName']['confidence']])
            sources = self.get_sources(org_data[positions['AdminName']['source']])

            if sources and confidence:

                emp_data = {
                    'Emplacement_EmplacementOrganization': {
                        'value': organization,
                        'confidence': confidence,
                        'sources': sources.copy()
                    },
                    'Emplacement_EmplacementSite': {
                        'value': site,
                        'confidence': confidence,
                        'sources': sources.copy()
                    }
                }

                try:
                    emplacement = Emplacement.objects.get(emplacementorganization__value=organization,
                                                        emplacementsite__value=site)
                except Emplacement.DoesNotExist:
                    emplacement = Emplacement.create(emp_data)

                for field_name, positions in relation_positions.items():

                    if field_name == 'StartDate':
                        self.make_relation(field_name,
                                           positions,
                                           org_data,
                                           emplacement,
                                           date=True)

                    elif field_name == 'EndDate':
                        self.make_relation(field_name,
                                           positions,
                                           org_data,
                                           emplacement,
                                           date=True)

                    elif field_name == 'RealStart':
                        self.make_real_date(data=org_data,
                                            position=positions['value'],
                                            model=EmplacementRealStart,
                                            attribute='realstart',
                                            object_ref=emplacement)

                    else:
                        self.make_relation(field_name,
                                           positions,
                                           org_data,
                                           emplacement)

                return emplacement

            else:
                missing = []
                if not confidence:
                    missing.append('confidence')
                if not sources:
                    missing.append('sources')

                self.log_error('Emplacement for org {0} did not have {1}'.format(organization.name.get_value().value,
                                                                                 ', '.join(missing)))
                return None

        else:
            self.log_error('Could not find OSM ID {}'.format(osm_id))
            return None

    def get_or_create_site(self, osm, exact_location, data, positions):
        '''
        Helper method to get or create a Location based on spreadsheet data.

        Params:
            * osm: OSMFeature
            * exact_location: dictionary returned from get_exact_location()
            * data: the spreadsheet data, as an array
            * positions: nested dictionaries documenting the index, confidence,
              and source values for each model represented in the sheet.

        Returns:
            * Location object.
        '''

        names = [
            exact_location.get('name'),
            data[positions['AdminName']['value']],
            data[positions['AdminLevel1']['value']],
        ]

        name = ', '.join([n for n in names if n])

        if exact_location.get('id'):
            osm_id = exact_location['id']
            division_id = None
            coords = exact_location['coords']
            tags = exact_location['tags']
            feature_type = 'node'
        else:
            osm_id = data[positions['AdminId']['value']]
            osm = get_osm_by_id(osm_id)
            osm_id = osm.id

            division_id = 'ocd-division/country:{}'.format(osm.country_code)

            coords = osm.geometry
            tags = osm.tags

            if osm.feature_type == 'point':
                feature_type = 'node'
            else:
                feature_type = 'relation'

        site, created = Location.objects.get_or_create(id=osm_id)

        if created:

            site.name = name
            site.division_id = division_id
            site.tags = tags
            site.geometry = coords
            site.feature_type = feature_type

            site.save()

        return site

    def get_exact_location(self, positions, data):
        '''
        Helper method for figuring out the data type of an "Exact Location" and
        returning relevant info. SFM staff sometimes record Exact Locations as
        OSM ID/Name pairs, and sometimes as coordinates, so we have to do some
        parsing to get the right attributes.

        Params:
            * data: the spreadsheet data, as an array
            * positions: nested dictionaries documenting the index, confidence,
              and source values for each model represented in the sheet.
        Returns:
            * dictionary with the following values:
                - id: OSM ID or None
                - name: OSM Name or None
                - coords: Coordinate pair
        '''
        exact_location = {}

        lng_or_name = data[positions['ExactLocation']['lng_or_name']]
        lat_or_id = data[positions['ExactLocation']['lat_or_id']]

        try:
            assert (lng_or_name and lat_or_id)
        except AssertionError:
            # The field is empty, so return an empty dict
            return exact_location

        # Figure out if it's OSM Name/ID pair, or coordinate pair
        try:

            # If this succeeds, it's a coordinate pair
            int(lng_or_name)
            int(lat_or_id)

            lng, lat = lng_or_name, lat_or_id

        except ValueError:

            # This is a name/ID pair
            exact_location['name'], exact_location['id'] = lng_or_name, lat_or_id

            try:

                geo = get_osm_by_id(exact_location['id'])
                lng, lat = geo.st_x, geo.st_y

            except (DataError, AttributeError):
                self.log_error('OSM ID for exact location {0} does not seem valid: {1}'.format(exact_location['name'],
                                                                                               exact_location['id']))
                return exact_location

        point_string = 'POINT({lng} {lat})'.format(lng=lng, lat=lat)
        exact_location['coords'] = GEOSGeometry(point_string, srid=4326)
        exact_location['tags'] = geo.tags

        return exact_location

    def make_real_date(self, *, data, position, model, attribute, object_ref):
        '''
        Record a value from the sheet (`data`) corresponding to a real start/end
        date for a particular model instance.
        Params:
            - `data`: the sheet in question
            - `position`: index from which to retrieve the value
            - `model`: the model to create (e.g. OrganizationRealStart)
            - `attribute`: attribute of the model in question (e.g. 'realstart')
            - `object_ref`: the object instance that this date is tied to
        '''
        # We have to convert the 'Y'/'N' in the RealStart/End field to bool
        try:
            real_date = data[position]
        except IndexError:
            real_date = None

        if not real_date:
            return None

        if real_date == 'Y':
            real_date = True
        elif real_date == 'N':
            real_date = False
        else:
            real_date = None

        instance, created = model.objects.get_or_create(value=real_date,
                                                        object_ref=object_ref)

        if created:

            with reversion.create_revision():
                reversion.set_user(self.user)

        instance.save()

    def create_sources(self, source_sheet):

        self.current_sheet = 'sources'

        for source in source_sheet['values']:
            if source['source:restricted:admin'] == '1':
                # Skip restricted sources
                continue

            access_point_uuid = source['source:access_point_id:admin']

            try:
                AccessPoint.objects.get(uuid=access_point_uuid)

            except AccessPoint.DoesNotExist:
                new_source, created = Source.objects.get_or_create(
                    title=source['source:title'],
                    type=source['source:type'],
                    author=source['source:author'],
                    publication=source['source:publication_name'],
                    publication_country=source['source:publication_country'],
                    published_on=self.parse_date(source['source:published_timestamp']),
                    created_on=self.parse_date(source['source:created_timestamp']),
                    uploaded_on=self.parse_date(source['source:uploaded_timestamp']),
                    source_url=source['source:url'],
                    user=self.user
                )

                AccessPoint.objects.create(
                    uuid=access_point_uuid,
                    type=source['source:access_point_type'],
                    trigger=source['source:access_point_trigger'],
                    accessed_on=self.parse_date(source['source:accessed_timestamp']),
                    archive_url=source['source:archive_url'],
                    source=new_source,
                    user=self.user
                )

            except ValueError:
                self.log_error("Invalid access point at: " + access_point_uuid)

    def get_sources(self, source_id_string):

        sources = []
        source_ids = [s.strip() for s in source_id_string.split(';') if s]

        for source_id in source_ids:
            try:
                source = AccessPoint.objects.get(uuid=source_id)
                sources.append(source)

            except (ValueError, ValidationError):
                self.log_error("Invalid source: " + source_id)


        return sources

    def create_person(self, person_data):
        person = None

        person_positions = {
            'Name': {
                'value': 'person:name',
                'confidence': 'person:name:confidence',
                'source': 'person:name:source',
            },
            'Alias': {
                'value': 'person:other_names',
                'confidence': 'person:other_names:confidence',
                'source': 'person:other_names:source',
            },
            'DivisionId': {
                'value': 'person:country',
                'confidence': 'person:country:confidence',
                'source': 'person:country:source',
            },
        }
        membership_positions = {
            'Organization': {
                'value': 'person:posting',
                'confidence': 'person:posting:confidence',
                'source': 'person:posting:source',
            },
            'Role': {
                'value': 'person:posting_role',
                'confidence': 'person:posting_role:confidence',
                'source': 'person:posting_role:source',
            },
            'Title': {
                'value': 'person:posting_title',
                'confidence': 'person:posting_title:confidence',
                'source': 'person:posting_title:source',
            },
            'Rank': {
                'value': 'person:posting_rank',
                'confidence': 'person:posting_rank:confidence',
                'source': 'person:posting_rank:source',
            },
            'FirstCitedDate': {
                'value': 'person:posting_first_cited_date',
                'day': 'person:posting_first_cited_date_day',
                'month': 'person:posting_first_cited_date_month',
                'year': 'person:posting_first_cited_date_year',
                'confidence': 'person:posting_first_cited_date:confidence',
                'source': 'person:posting_first_cited_date:source',
            },
            'RealStart': {
                'value': 'person:posting_first_cited_date_start',
                'confidence': 'person:posting_first_cited_date:confidence',
                'source': None,
            },
            'StartContext': {
                'value': 'person:posting_first_cited_date_start_context',
                'confidence': 'person:posting_first_cited_date_start_context:confidence',
                'source': 'person:posting_first_cited_date_start_context:source',
            },
            'LastCitedDate': {
                'value': 'person:posting_last_cited_date',
                'day': 'person:posting_last_cited_date_day',
                'month': 'person:posting_last_cited_date_month',
                'year': 'person:posting_last_cited_date_year',
                'confidence': 'person:posting_last_cited_date:confidence',
                'source': 'person:posting_last_cited_date:source',
            },
            'RealEnd': {
                'value': 'person:posting_last_cited_date_end',
                'confidence': 'person:posting_last_cited_date:confidence',
                'source': None,
            },
            'EndContext': {
                'value': 'person:posting_last_cited_date_end_context',
                'confidence': 'person:posting_last_cited_date_end_context:confidence',
                'source': 'person:posting_last_cited_date_end_context:source',
            },
        }

        try:
            name_value = person_data[person_positions['Name']['value']]
            confidence = person_data[person_positions['Name']['confidence']]
            source = person_data[person_positions['Name']['source']]
        except IndexError:
            self.log_error('Row seems to be empty')
            return None

        try:
            country_code = person_data[person_positions['DivisionId']['value']]
        except IndexError:
            self.log_error('Country code missing')
            return None

        if confidence and source:

            try:
                confidence = self.get_confidence(confidence)
            except KeyError:
                confidence = None

            sources = self.get_sources(source)
            self.stdout.write(self.style.SUCCESS('Working on {}'.format(name_value)))

            if confidence and sources:

                division_id = 'ocd-division/country:{}'.format(country_code)
                division_confidence = self.get_confidence(
                    person_data[person_positions['DivisionId']['confidence']]
                )
                division_sources = self.get_sources(
                    person_data[person_positions['DivisionId']['source']]
                )

                person_info = {
                    'Person_PersonName': {
                        'value': name_value,
                        'confidence': confidence,
                        'sources': sources.copy()
                    },
                    'Person_PersonDivisionId': {
                        'value': division_id,
                        'confidence': division_confidence,
                        'sources': division_sources,
                    }
                }

                try:
                    uuid = self.person_entity_map[name_value]
                except KeyError:
                    self.log_error('Could not find "{}" in list of person names'.format(name_value))
                    return None

                try:
                    person = Person.objects.get(uuid=uuid)
                    sources = self.sourcesList(person, 'name')
                    person_info["Person_PersonName"]['sources'] += sources
                    person.update(person_info)

                except Person.DoesNotExist:
                    person = Person.objects.create(uuid=uuid, published=True)
                    person.update(person_info)

                self.make_relation('Alias',
                                   person_positions['Alias'],
                                   person_data,
                                   person)

                # Make membership objects
                try:
                    organization_name = person_data[membership_positions['Organization']['value']]
                except IndexError:
                    self.log_error('Row seems to be empty')
                    return None

                try:
                    confidence = self.get_confidence(person_data[membership_positions['Organization']['confidence']])
                except (KeyError, IndexError):
                    self.log_error('Person {0} as a member of {1} has no confidence'.format(name_value, organization_name))
                    return None

                try:
                    sources = self.get_sources(person_data[membership_positions['Organization']['source']])
                except (KeyError, IndexError):
                    self.log_error('Person {0} as a member of {1} has no sources'.format(name_value, organization_name))
                    return None

                org_info = {
                    'Organization_OrganizationName': {
                        'value': organization_name,
                        'confidence': confidence,
                        'sources': sources.copy(),
                    },
                    'Organization_OrganizationDivisionId': {
                        'value': division_id,
                        'confidence': division_confidence,
                        'sources': division_sources,
                    }
                }

                try:
                    uuid = self.organization_entity_map[organization_name]
                except KeyError:
                    self.log_error('Could not find "{}" in list of organization names'.format(organization_name))
                    return None

                try:
                    organization = Organization.objects.get(uuid=uuid)

                except Organization.DoesNotExist:
                    organization = Organization.objects.create(uuid=uuid,
                                                               published=True)
                    organization.update(org_info)

                else:
                    name_sources = self.sourcesList(organization, 'name')
                    div_sources = self.sourcesList(organization, 'division_id')

                    org_info["Organization_OrganizationName"]['sources'] += name_sources
                    org_info["Organization_OrganizationDivisionId"]['sources'] += div_sources

                    if organization.name.get_value():
                        name_confidence = organization.name.get_value().confidence

                        if name_confidence:
                            name_confidence = int(name_confidence)
                            org_info["Organization_OrganizationName"]['confidence'] = name_confidence

                    if organization.division_id.get_value():
                        div_confidence = organization.division_id.get_value().confidence

                        if div_confidence:
                            div_confidence = int(div_confidence)
                            org_info["Organization_OrganizationDivisionId"]['confidence'] = div_confidence

                    organization.update(org_info)

                membership_data = {
                    'MembershipPerson_MembershipPersonMember': {
                        'value': person,
                        'confidence': confidence,
                        'sources': sources.copy(),
                    },
                    'MembershipPerson_MembershipPersonOrganization': {
                        'value': organization,
                        'confidence': confidence,
                        'sources': sources.copy(),
                    },
                }

                try:
                    date_parts = [
                        person_data[membership_positions['FirstCitedDate']['year']],
                        person_data[membership_positions['FirstCitedDate']['month']],
                        person_data[membership_positions['FirstCitedDate']['day']]
                    ]
                    fcd = self.parse_date('-'.join(filter(None, date_parts)))
                except IndexError:
                    fcd = None

                try:
                    date_parts = [
                        person_data[membership_positions['LastCitedDate']['year']],
                        person_data[membership_positions['LastCitedDate']['month']],
                        person_data[membership_positions['LastCitedDate']['day']]
                    ]
                    lcd = self.parse_date('-'.join(filter(None, date_parts)))
                except IndexError:
                    lcd = None

                try:
                    role_name = person_data[membership_positions['Role']['value']]
                    role, _ = Role.objects.get_or_create(value=role_name)
                    role = role.id
                except IndexError:
                    role = None

                try:
                    rank_name = person_data[membership_positions['Rank']['value']]
                    rank, _ = Rank.objects.get_or_create(value=rank_name)
                    rank = rank.id
                except IndexError:
                    rank = None

                try:
                    title = person_data[membership_positions['Title']['value']]
                except IndexError:
                    title = None

                try:
                    membership = MembershipPerson.objects.get(membershippersonmember__value=person,
                                                              membershippersonorganization__value=organization,
                                                              membershippersonfirstciteddate__value=fcd,
                                                              membershippersonlastciteddate__value=lcd,
                                                              membershippersonrole__value=role,
                                                              membershippersonrank__value=rank,
                                                              membershippersontitle__value=title)
                    sources = set(self.sourcesList(membership, 'member') + \
                                  self.sourcesList(membership, 'organization'))
                    membership_data['MembershipPerson_MembershipPersonMember']['sources'] += sources
                    membership.update(membership_data)

                except MembershipPerson.DoesNotExist:
                    membership = MembershipPerson.create(membership_data)

                self.make_relation('Role',
                                   membership_positions['Role'],
                                   person_data,
                                   membership)

                self.make_relation('Title',
                                   membership_positions['Title'],
                                   person_data,
                                   membership)

                self.make_relation('Rank',
                                   membership_positions['Rank'],
                                   person_data,
                                   membership)

                self.make_relation('FirstCitedDate',
                                   membership_positions['FirstCitedDate'],
                                   person_data,
                                   membership,
                                   date=True)

                self.make_real_date(data=person_data,
                                    position=membership_positions['RealStart']['value'],
                                    model=MembershipPersonRealStart,
                                    attribute='realstart',
                                    object_ref=membership)

                self.make_relation('StartContext',
                                   membership_positions['StartContext'],
                                   person_data,
                                   membership)

                self.make_relation('LastCitedDate',
                                   membership_positions['LastCitedDate'],
                                   person_data,
                                   membership,
                                   date=True)

                self.make_real_date(data=person_data,
                                    position=membership_positions['RealEnd']['value'],
                                    model=MembershipPersonRealEnd,
                                    attribute='realstart',
                                    object_ref=membership)

                self.make_relation('EndContext',
                                   membership_positions['EndContext'],
                                   person_data,
                                   membership)

                self.stdout.write(self.style.SUCCESS('Created {}'.format(person.get_value())))

            else:
                self.log_error('{} did not have a confidence or source'.format(name_value))

    def create_person_extra(self, data):
        """
        Create a PersonExtra objects from a row in the persons_extra sheet.
        """
        positions = {
            'Name': {
                'value': 'person_extra:name',
            },
            'Id': {
                'value': 'person_extra:id:admin',
            },
            'Gender': {
                'key': 'Person_PersonExtraGender',
                'value': 'person_extra:gender',
                'confidence': 'person_extra:gender:confidence',
                'source': 'person_extra:gender:source',
            },
            'DateOfBirth': {
                'key': 'Person_PersonExtraDateOfBirth',
                'value': 'person_extra:date_of_birth',
                'confidence': 'person_extra:date_of_birth:confidence',
                'source': 'person_extra:date_of_birth:source',
            },
            'Deceased': {
                'key': 'Person_PersonExtraDeceased',
                'value': 'person_extra:deceased',
                'confidence': 'person_extra:deceased:confidence',
                'source': 'person_extra:deceased:source',
            },
            'DateOfDeath': {
                'key': 'Person_PersonExtraDateOfDeath',
                'value': 'person_extra:deceased_date',
                'confidence': 'person_extra:deceased_date:confidence',
                'source': 'person_extra:deceased_date:source',
            },
            'AccountType': {
                'key': 'Person_PersonExtraAccountType',
                'value': 'person_extra:account_type',
                'confidence': 'person_extra:account:confidence',
                'source': 'person_extra:account:source',
            },
            'AccountId': {
                'key': 'Person_PersonExtraAccount',
                'value': 'person_extra:account_id',
                'confidence': 'person_extra:account:confidence',
                'source': 'person_extra:account:source',
            },
            'ExternalLinkDescription': {
                'key': 'Person_PersonExtraExternalLinkDescription',
                'value': 'person_extra:external_link_description',
                'confidence': 'person_extra:external_link:confidence',
                'source': 'person_extra:external_link:source',
            },
            'MediaDescription': {
                'key': 'Person_PersonExtraMediaDescription',
                'value': 'person_extra:media_desc',
                'confidence': 'person_extra:media:confidence',
                'source': 'person_extra:media:source',
            },
            'Notes': {
                'key': 'Person_PersonExtraNotes',
                'value': 'person_extra:notes:admin',
            },
        }

        try:
            person_name_value = data[positions['Name']['value']]
        except IndexError:
            self.log_error('Row appears to be missing a Person name')
            return None

        try:
            person_id_value = data[positions['Id']['value']]
        except IndexError:
            self.log_error('Row appears to be missing a Person ID')
            return None

        try:
            person = Person.objects.get(uuid=person_id_value)
        except Person.DoesNotExist:
            self.log_error('No person with the ID {} was found')
            return None

        try:
            assert person.name.get_value() == person_name_value
        except AssertionError:
            self.log_error(
                'Stored person name "{}" does not match spreadsheet value "{}"'.format(
                    person.name.get_value(), person_name_value
                ))
            return None

        self.stdout.write(
            self.style.SUCCESS(
                'Working on {}'.format(person_name_value)
            )
        )

        person_extra_info = {
            'Person_PersonExtraPerson': {
                'value': person,
            },
        }

        for metadata in positions.values():
            if metadata.get('key'):
                person_extra_info[metadata['key']] = {
                    'value': metadata['value']
                }
                if metadata.get('confidence'):
                    person_extra_info[metadata['key']]['confidence'] = self.get_confidence(
                        metadata['confidence']
                    )
                if metadata.get('sources'):
                    person_extra_info[metadata['key']]['sources'] = self.get_sources(
                        metadata['sources']
                    )

        try:
            person_extra = PersonExtra.objects.get(person=person)
        except PersonExtra.DoesNotExist:
            person_extra = PersonExtra.objects.create(person=person)

        person_extra.update(person_extra_info)

        self.stdout.write(
            self.style.SUCCESS(
                'Created extra information for {}'.format(person_name_value)
            )
        )

    def get_or_create_location(self, geo):
        location, created = Location.objects.get_or_create(id=geo.id)

        if created:
            location.name = geo.name
            location.geometry = geo.geometry

            country_code = geo.country_code.lower()
            location.division_id = 'ocd-division/country:{}'.format(country_code)

            if location.feature_type == 'point':
                location.feature_type = 'node'
            else:
                location.feature_type = 'relation'

            location.save()

        return location

    def create_event(self, event_data):

        positions = {
            'StartDate': {
                'value': 'incident:start_date',
                'source': 'incident:all:source',
                'model_field': 'violationstartdate',
            },
            'EndDate': {
                'value': 'incident:end_date',
                'source': 'incident:all:source',
                'model_field': 'violationenddate',
            },
            # AKA "date of publication"
            'FirstAllegation': {
                'value': 'incident:pub_date',
                'source': 'incident:all:source',
                'model_field': 'violationfirstallegation',
            },
            'LastUpdate': {
                'value': 'incident:update_date',
                'source': 'incident:all:source',
                'model_field': 'violationlastupdate',
            },
            'Status': {
                'value': 'incident:update_status',
                'source': 'incident:all:source',
                'model_field': 'violationstatus',
            },
            'LocationDescription': {
                'value': 'incident:location_description',
                'source': 'incident:all:source',
                'model_field': 'violationlocationdescription',
            },
            'ExactLocation': {
                'lng_or_name': 'incident:site_exact_location_name_longitude',
                'lat_or_id': 'incident:site_exact_location_id_latitude',
                'source': 'incident:all:source',
                'model_field': 'violationexactlocation',
            },
            'DivisionId': {
                'value': 'incident:site_country',
                'source': 'incident:all:source',
            },
            'Type': {
                'value': 'incident:violation_type',
                'source': 'incident:all:source',
                'model_field': 'violationtype',
            },
            'Description': {
                'value': 'incident:violation_description',
                'source': 'incident:all:source',
                'model_field': 'violationdescription',
            },
            'AdminName': {
                'value': 'incident:site_settlement_name',
                'source': 'incident:all:source',
            },
            'AdminId': {
                'value': 'incident:site_settlement_id',
                'source': 'incident:all:source',
            },
            'AdminLevel2': {
                'osmid': 'incident:site_first_admin_area_id',
                'value': 'incident:site_first_admin_area_name',
                'source': 'incident:all:source',
            },
            'Perpetrator': {
                'value': 'incident:perpetrator_name',
                'source': 'incident:all:source'
            },
            'PerpetratorOrganization': {
                'value': 'incident:perpetrator_unit',
                'source': 'incident:all:source'
            },
            'PerpetratorClassification': {
                'value': 'incident:perpetrator_classification',
                'source': 'incident:all:source'
            }
        }

        uuid = event_data[self.col('AG')]

        with reversion.create_revision():
            violation, created = Violation.objects.get_or_create(uuid=uuid,
                                                                 published=True)
            reversion.set_user(self.user)

        # Simple attributes that support multiple values
        simple_multi_attrs = ('LocationDescription', 'Type', 'Status')

        for attr in simple_multi_attrs:
            self.make_relation(attr,
                               positions[attr],
                               event_data,
                               violation,
                               require_confidence=False)

        # Simple attributes that only support single values
        simple_single_attrs = ('Description',)

        for attr in simple_single_attrs:
            self.make_relation(attr,
                               positions[attr],
                               event_data,
                               violation,
                               require_confidence=False,
                               multiple=False)

        date_attrs = ('StartDate', 'EndDate', 'FirstAllegation', 'LastUpdate')

        for attr in date_attrs:

            self.make_relation(attr,
                               positions[attr],
                               event_data,
                               violation,
                               require_confidence=False,
                               date=True)

        try:
            # All data in this sheet use the same source
            sources = self.get_sources(event_data[positions['Type']['source']])
        except IndexError:
            self.log_error('Row does not have required source column')
            return None

        # Make OSM stuff
        admin_id = event_data[positions['AdminId']['value']]
        admin_name = event_data[positions['AdminName']['value']]

        adminlevel2_id = event_data[positions['AdminLevel2']['osmid']]
        adminlevel2_name = event_data[positions['AdminLevel2']['value']]

        exact_location = self.get_exact_location(positions, event_data)

        coords = exact_location.get('coords')
        exactloc_id = exact_location.get('id')
        exactloc_name = exact_location.get('name')

        event_info = {}
        osm_id = None

        if exactloc_name and exactloc_id:
            event_info.update({
                'Violation_ViolationLocationName': {
                    'value': exactloc_name,
                    'sources': sources.copy(),
                    'confidence': 1
                },
                'Violation_ViolationLocationId': {
                    'value': exactloc_id,
                    'sources': sources.copy(),
                    'confidence': 1
                },
            })

            osm_id = exactloc_id

        geo, admin1, admin2 = None, None, None

        # Get adminlevel2
        if adminlevel2_id:
            try:
                admin2 = get_osm_by_id(adminlevel2_id)
            except DataError:
                self.log_error(
                    'AdminLevel2 ID for ViolationLocation {} does not seem valid: {}'.format(
                        adminlevel2_name, adminlevel2_id
                    ))
        else:
            self.log_error('Missing OSM ID for AdminLevel2')

        # Infer locations
        if admin_id:
            try:
                geo = get_osm_by_id(admin_id)
            except DataError:
                self.log_error('OSM ID for Site {0} does not seem valid: {1}'.format(site_name, admin_id))
        else:
            self.log_error('Missing OSM ID')

        if geo:

            if not coords:

                point_string = 'POINT({lng} {lat})'

                point = (str(geo.st_x), str(geo.st_y))

                coords = GEOSGeometry(point_string.format(lng=point[0], lat=point[1]),
                                      srid=4326)

            hierarchy = get_hierarchy_by_id(admin_id)

            if hierarchy:
                for member in hierarchy:
                    if int(member.admin_level) == 6 and not admin1:
                        admin1 = self.get_or_create_location(member)

            if admin1:
                event_info.update({
                    'Violation_ViolationAdminLevel1': {
                        'value': admin1,
                        'sources': sources.copy(),
                        'confidence': 1
                    },
                })
            if admin2:
                event_info.update({
                    'Violation_ViolationAdminLevel2': {
                        'value': self.get_or_create_location(admin2),
                        'sources': sources.copy(),
                        'confidence': 1
                    },
                })
            if geo:
                event_info.update({
                    'Violation_ViolationOSMName': {
                        'value': geo.name,
                        'sources': sources.copy(),
                        'confidence': 1
                    },
                    'Violation_ViolationOSMId': {
                        'value': geo.id,
                        'sources': sources.copy(),
                        'confidence': 1
                    },
                })

            osm_id = geo.id

        if osm_id:

            event_info.update({
                'Violation_ViolationLocation': {
                    'value': self.get_or_create_location(geo),
                    'sources': sources.copy(),
                    'confidence': 1
                },
            })

        try:
            country_code = event_data[positions['DivisionId']['value']]
        except IndexError:
            self.log_error('Country code missing')
            return None

        division_id = 'ocd-division/country:{}'.format(country_code)

        event_info.update({
            'Violation_ViolationDivisionId': {
                'value': division_id,
                'sources': sources.copy(),
                'confidence': 1,
            }
        })

        violation.update(event_info)

        # Record perpetrators

        try:
            perpetrator = event_data[positions['Perpetrator']['value']]
        except IndexError:
            perpetrator = None

        if perpetrator:

            perps = [perp.strip() for perp in perpetrator.split(';') if perp.strip()]

            for perp in perps:

                try:
                    uuid = self.person_entity_map[perp]
                except KeyError:
                    self.log_error('Could not find "{}" in list of person names'.format(perp))
                    continue

                try:
                    person = Person.objects.get(uuid=uuid)
                except Person.DoesNotExist:
                    person_info = {
                        'Person_PersonName': {
                            'value': perp,
                            'confidence': 1,
                            'sources': sources.copy(),
                        },
                        'Person_PersonDivisionId' : {
                            'value': division_id,
                            'confidence': 1,
                            'sources': sources.copy()
                        }
                    }
                    person = Person.objects.create(uuid=uuid, published=True)
                    person.update(person_info)

                vp, created = ViolationPerpetrator.objects.get_or_create(value=person,
                                                                         object_ref=violation)
                if created:

                    with reversion.create_revision():
                        for source in sources:
                            vp.accesspoints.add(source)
                            vp.sources.add(source.source)
                        vp.save()
                        reversion.set_user(self.user)

        try:
            perp_org = event_data[positions['PerpetratorOrganization']['value']]
        except IndexError:
            perp_org = None

        if perp_org:

            orgs = [perp.strip() for perp in perp_org.split(';') if perp.strip()]

            for org in orgs:

                try:
                    uuid = self.organization_entity_map[org]
                except KeyError:
                    self.log_error('Could not find "{}" in list of organization names'.format(org))
                    return None

                try:
                    organization = Organization.objects.get(uuid=uuid)
                except (Organization.DoesNotExist, ValueError):

                    info = {
                        'Organization_OrganizationName': {
                            'value': org,
                            'confidence': 1,
                            'sources': sources.copy(),
                        },
                        'Organization_OrganizationDivisionId': {
                            'value': division_id,
                            'confidence': 1,
                            'sources': sources.copy(),
                        }
                    }
                    organization = Organization.objects.create(uuid=uuid,
                                                               published=True)
                    organization.update(info)

                vpo_obj, created = ViolationPerpetratorOrganization.objects.get_or_create(value=organization,
                                                                                          object_ref=violation)

                if created:

                    with reversion.create_revision():
                        for source in sources:
                            vpo_obj.accesspoints.add(source)
                            vpo_obj.sources.add(source.source)
                        vpo_obj.save()
                        reversion.set_user(self.user)

        self.make_relation('PerpetratorClassification',
                           positions['PerpetratorClassification'],
                           event_data,
                           violation,
                           require_confidence=False)

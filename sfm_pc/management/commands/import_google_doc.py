import os
import json
from collections import OrderedDict
import re
from uuid import uuid4
from datetime import datetime
import csv

import httplib2

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

import datefinder

from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist

from cities.models import Country

from source.models import Source, Publication
from organization.models import Organization, OrganizationAlias, \
    OrganizationClassification, OrganizationName
from sfm_pc.utils import import_class, get_geoname_by_id
from sfm_pc.base_views import UtilityMixin
from geosite.models import Geosite
from emplacement.models import Emplacement

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

CONFIDENCE_MAP = {
    'low': 1,
    'medium': 2,
    'high': 3,
}

class Command(UtilityMixin, BaseCommand):
    help = 'Import data from Google Drive Spreadsheet'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--doc_id',
            dest='doc_id',
            default='16cRBkrnXE5iGm8JXD7LSqbeFOg_anhVp2YAzYTRYDgU',
            help='Import data from specified Google Drive Document'
        )
        parser.add_argument(
            '--entity_types',
            dest='entity_types',
            default='organization,person,event',
            help='Comma separated list of entity types to import'
        )
    
    def get_credentials(self):
        
        this_dir = os.path.dirname(__file__)
        secrets_path = os.path.join(this_dir, 'credentials.json')
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(secrets_path, 
                                                                       SCOPES)
        return credentials
    
    # @transaction.atomic
    def handle(self, *args, **options):
        
        credentials = self.get_credentials()
        
        http = credentials.authorize(httplib2.Http())

        service = build('sheets', 'v4', http=http)
        
        result = service.spreadsheets().get(
            spreadsheetId=options['doc_id'], includeGridData=False).execute()
        
        sheets = result['sheets']
        
        sheet_mapping = {}

        for sheet in sheets:
            title = sheet['properties']['title']

            sheet_data = service.spreadsheets().values().get(
                spreadsheetId=options['doc_id'], range=title).execute()

            sheet_mapping[title] = sheet_data['values']

        org_sheets = {title: data for title, data in sheet_mapping.items() \
                          if 'organization' in title.lower() or 'mopol' in title.lower()}
        
        person_sheets = {title: data for title, data in sheet_mapping.items() \
                            if 'person' in title.lower()}
        
        event_sheets = {title: data for title, data in sheet_mapping.items() \
                            if 'event' in title.lower()}
        
        all_sheets = {
            'organization': org_sheets,
            'person': person_sheets,
            'event': event_sheets,
        }
        
        for entity_type in options['entity_types'].split(','):
            
            sheets = all_sheets[entity_type]
            
            for title, sheet in sheets.items():
            
                self.stdout.write(self.style.SUCCESS('Creating {0}s from {1} ... '.format(entity_type, title)))
                
                self.current_sheet = title

                # Skip header row
                for index, row in enumerate(sheet[1:]):
                    if row:
                        self.current_row = index
                        getattr(self, 'create_{}'.format(entity_type))(row)
        
        self.stdout.write(self.style.SUCCESS('Successfully imported data from {}'.format(options['doc_id'])))
    
    def log_error(self, message):
        log_message = message + ' (context: Sheet {0}, Row {1})'.format(self.current_sheet, self.current_row)
        self.stdout.write(self.style.ERROR(log_message))
        
        if not os.path.isfile('errors.csv'):
            with open('errors.csv', 'w') as f:
                header = ['timestamp', 'sheet', 'row', 'message']
                writer = csv.writer(f)
                writer.writerow(header)

        with open('errors.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().isoformat(), 
                             self.current_sheet, 
                             self.current_row, 
                             message])

    def create_organization(self, org_data):
        organization = None
        
        org_positions = {
            'Name': {
                'value': 14,
                'confidence': 16,
                'source': 15
            },
            'Alias': {
                'value': 17,
                'confidence': 19,
                'source': 18,
            },
            'Classification': {
                'value': 21,
                'confidence': 23,
                'source': 22,
            },
        }
        
        composition_positions = {
            'Parent': {
                'value': 1,
                'confidence': 3,
                'source': 2,
            },
            'StartDate': {
                'value': 7,
                'confidence': 9,
                'source': 8,
            },
            'EndDate': {
                'value': 10,
                'confidence': 12,
                'source': 11,
            },
            'Classification': {
                'value': 4,
                'confidence': 6,
                'source': 5,
            },
        }
        
        area_positions = {
            'Geoname': {
                'value': 45,
                'confidence': 48,
                'source': 47,
            },
            'GeonameId': {
                'value': 46,
                'confidence': 48,
                'source': 47,
            },
        }
        
        site_positions = {
            'Geoname': {
                'value': 27,
                'confidence': 30,
                'source': 29,
            },
            'GeonameId': {
                'value': 28,
                'confidence': 30,
                'source': 29,
            },
        }
        
        association_positions = {
            'StartDate': {
                'value': 49,
                'confidence': 51,
                'source': 50
            },
            'EndDate': {
                'value': 52,
                'confidence': 54,
                'source': 53,
            }
        }

        # Need to get or create name first

        try:
            name_value = org_data[org_positions['Name']['value']]
            confidence = org_data[org_positions['Name']['confidence']].strip().lower()
            source = org_data[org_positions['Name']['source']]
        except IndexError:
            self.log_error('Row seems to be empty')
            return None
        
        if confidence and source:
            
            try:
                confidence = CONFIDENCE_MAP[confidence]
            except KeyError:
                confidence = None
            
            sources = self.create_sources(source)
            self.stdout.write(self.style.SUCCESS('Working on {}'.format(name_value)))
            
            if confidence and sources:
                
                org_info = {
                    'Organization_OrganizationName': {
                        'value': name_value,
                        'confidence': confidence,
                        'sources': sources
                    }
                }
                
                try:
                    organization = Organization.objects.get(organizationname__value=name_value)
                    sources = self.sourcesList(organization, 'name')
                    org_info["Organization_OrganizationName"]['sources'] = sources
                    
                except Organization.DoesNotExist:
                    organization = Organization.create(org_info)

                aliases = self.make_relation('Alias', 
                                             org_positions['Alias'], 
                                             org_data, 
                                             organization)
                
                classification = self.make_relation('Classification',
                                                    org_positions['Classification'],
                                                    org_data,
                                                    organization)
                
                # Create Geographies
                site_geoname_id = org_data[site_positions['GeonameId']['value']]

                if site_geoname_id:
                    
                    emplacement = self.make_emplacement(site_geoname_id, 
                                                        org_data, 
                                                        organization)
                

                self.stdout.write(self.style.SUCCESS('Created {}'.format(organization.get_value())))

            else:
                self.log_error('{} did not have a confidence or source'.format(name_value))
        
        else:
            self.log_error('{} did not have a confidence or source'.format(name_value))
        
        return organization
    
    def make_relation(self, 
                      field_name, 
                      positions, 
                      data,
                      instance):

        value_position = positions['value']
        confidence_position = positions['confidence']
        source_position = positions['source']
        
        try:
            value = data[value_position]
            confidence = CONFIDENCE_MAP.get(data[confidence_position])
            source = self.create_sources(data[source_position])
        except IndexError:
            self.log_error('Row seems to be empty')
        
        app_name = instance._meta.model_name
        model_name = instance._meta.object_name

        if source and confidence:
            import_path = '{app_name}.models.{model_name}{field_name}'

            relation_path = import_path.format(app_name=app_name,
                                               model_name=model_name,
                                               field_name=field_name)

            relation_model = import_class(relation_path)
            
            if isinstance(relation_model._meta.get_field('value'), models.ForeignKey):
                value_rel_path = '{app_name}.models.{field_name}'.format(app_name=app_name,
                                                                         field_name=field_name)
                value_model = import_class(value_rel_path)
               
                value_objects = []
                for value_text in value.split(';'):
                    value_obj, created = value_model.objects.get_or_create(value=value_text)
                    
                    relation_instance, created = relation_model.objects.get_or_create(value=value_obj,
                                                                                      object_ref=instance,
                                                                                      lang='en')
            else:
                relation_instance, created = relation_model.objects.get_or_create(value=value, 
                                                                                  object_ref=instance,
                                                                                  lang='en')

            relation_instance.sources.add(source)
            relation_instance.save()

            return relation_instance
        
        else:
            message = '{field_name} from {app_name}.{model_name} did not have a confidence or source'.format(field_name=field_name,
                                                                                                             app_name=app_name,
                                                                                                             model_name=model_name)
            self.log_error(message)
        
        return None
        
    def make_emplacement(self, 
                         geoname_id, 
                         org_data, 
                         organization):
        
        positions = {
            'Geoname': {
                'confidence': 30,
                'source': 29,
            },
            'AdminLevel1': {
                'confidence': 34,
                'source': 33,
            }
        }

        relation_positions = {
            'StartDate': {
                'value': 36,
                'confidence': 38,
                'source': 37,
            },
            'EndDate': {
                'value': 40,
                'confidence': 42,
                'source': 41,
            }
        }
        
        geo = get_geoname_by_id(geoname_id)
        
        if geo:
            parent = geo.parent
            admin1 = parent.name
            coords = getattr(geo, 'location', None)

            site, created = Geosite.objects.get_or_create(geositegeonameid__value=geo.id)

            site_data = {}

            geoname_confidence = CONFIDENCE_MAP[org_data[positions['Geoname']['confidence']].lower()]
            geoname_sources = self.create_sources(org_data[positions['Geoname']['source']])
            
            if geoname_confidence and geoname_sources:

                site_data['Geosite_GeositeName'] = {
                    'value': geo.name,
                    'confidence': geoname_confidence,
                    'sources': geoname_sources,
                }
                site_data['Geosite_GeositeGeoname'] = {
                    'value': geo.name,
                    'confidence': geoname_confidence,
                    'sources': geoname_sources,
                }
                site_data['Geosite_GeositeGeonameId'] = {
                    'value': geo.id,
                    'confidence': geoname_confidence,
                    'sources': geoname_sources,
                }
                site_data['Geosite_GeositeCoordinates'] = {
                    'value': coords,
                    'confidence': geoname_confidence,
                    'sources': geoname_sources,
                }
            
            else:
                self.log_error('Geoname {} did not have source or confidence'.format(geo.name))

            admin1_confidence = CONFIDENCE_MAP[org_data[positions['AdminLevel1']['confidence']].lower()]
            admin1_sources = self.create_sources(org_data[positions['AdminLevel1']['source']])
            
            if admin1_confidence and admin1_sources:

                site_data['Geosite_GeositeAdminLevel1'] = {
                    'value': admin1,
                    'confidence': admin1_confidence,
                    'sources': admin1_sources,
                }
            
            else:
                self.log_error('AdminLevel1 {} did not have source or confidence'.format(admin1))
            
            site.update(site_data)
            
            emplacement, created = Emplacement.objects.get_or_create(emplacementorganization__value=organization.id,
                                                                     emplacementsite__value=site.id)
            
            for field_name, positions in relation_positions.items():
                
                self.make_relation(field_name, 
                                   positions, 
                                   org_data, 
                                   emplacement)
            emp_data = {
                'Emplacement_EmplacementOrganization': {
                    'value': organization,
                    'confidence': geoname_confidence,
                    'sources': geoname_sources,
                },
                'Emplacement_EmplacementSite': {
                    'value': site,
                    'confidence': geoname_confidence,
                    'sources': geoname_sources,
                },
            }
            
            emplacement.update(emp_data)
        
        else:
            self.log_error('Could not find GeonameID {}'.format(geoname_id))

    def create_sources(self, sources_string):
        
        sources = []
        
        for source in sources_string.split(';'):
            
            try:
                dates = next(datefinder.find_dates(source, index=True))
            except StopIteration:
                self.log_error('Unable to parse published on date from source string: {}'.format(source))
                continue
            
            dates, indices = dates
            
            before_date, after_date = source[:indices[0]], source[indices[1]:]
            
            # Source title, publication title and publication country should be
            # before the date. If not, skip it

            try:
                source_title, pub_title = before_date.split('.', 1)
            except ValueError:
                self.log_error('Unable to parse source title and publication title from source string: {}'.format(source))
                continue
            
            pub_country = None
            first_paren = pub_title.find('(')
            
            if first_paren > 0:
                last_paren = pub_title.find(')')
                pub_country = pub_title[first_paren + 1:last_paren]
                pub_title = pub_title[:first_paren]
            
            try:
                country = Country.objects.get(name=pub_country)
            except Country.DoesNotExist:
                self.log_error('Unable to parse publication country from source string: {}'.format(source))
                continue

            # Source URL and archive URL (if they exist) should be after the date.
            
            source_url = None
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', after_date)

            if urls:
                source_url = urls[0]
            
            try:
                publication = Publication.objects.get(title=pub_title.strip(),
                                                      country=pub_country.strip())
            except Publication.DoesNotExist:
                publication_id = str(uuid4())
                publication = Publication.objects.create(title=pub_title.strip(),
                                                         id=publication_id,
                                                         country=pub_country.strip())
            
            source, created = Source.objects.get_or_create(title=source_title.strip(),
                                                           source_url=source_url,
                                                           publication=publication,
                                                           published_on=dates)
            
            sources.append(source)

        return sources


    def create_person(self, person_dict):
        person = None

        person_field_positions = {
            'Name': {
                'value': 1,
                'confidence': 3,
                'source': 2,
            },
            'Alias': {
                'value': 4,
                'confidence': 6,
                'source': 5,
            },
        }
        membership_field_positions = {
            'Organization': {
                'value': 7,
                'confidence': 9,
                'source': 8,
            },
            'Role': {
                'value': 10,
                'confidence': 12,
                'source': 11,
            },
            'Title': {
                'value': 13,
                'confidence': 15,
                'source': 14,
            },
            'Rank': {
                'value': 16,
                'confidence': 18,
                'source': 17,
            },
            'FirstCitedDate': {
                'value': 19,
                'confidence': 21,
                'source': 20,
            },
            'StartContext': {
                'value': 23,
                'confidence': 25,
                'source': 24,
            },
            'LastCitedDate': {
                'value': 26,
                'confidence': 28,
                'source': 27,
            },
            'EndContext': {
                'value': 30,
                'confidence': 32,
                'source': 31,
            },
        }

    def create_event(self, event_dict):
        pass

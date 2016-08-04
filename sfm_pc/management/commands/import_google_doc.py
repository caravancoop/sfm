import os
import json
from collections import OrderedDict
import re
from uuid import uuid4

import httplib2

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

import datefinder

from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction

from cities.models import Country

from source.models import Source, Publication
from organization.models import Organization, OrganizationAlias, \
    OrganizationClassification, OrganizationName
from sfm_pc.utils import import_class
from sfm_pc.base_views import UtilityMixin

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
                          if 'organization' in title.lower()}
        
        person_sheets = {title: data for title, data in sheet_mapping.items() \
                            if 'person' in title.lower()}
        
        event_sheets = {title: data for title, data in sheet_mapping.items() \
                            if 'event' in title.lower()}
        
        
        for title, sheet in org_sheets.items():
        
            self.stdout.write(self.style.SUCCESS('Creating organizations from {} ... '.format(title)))
            
            # Skip header row
            for row in sheet[1:]:
                if row:
                    self.create_organization(row)
        raise
        # self.stdout.write(self.style.SUCCESS('Successfully imported data from {}'.format(options['doc_id'])))
    
    def make_relation(self, 
                      field_name, 
                      positions, 
                      data,
                      instance):

        value_position = positions['value']
        confidence_position = positions['confidence']
        source_position = positions['source']

        value = data[value_position]
        confidence = CONFIDENCE_MAP.get(data[confidence_position])
        source = self.create_sources(data[source_position])
        
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
        
        # else:
            # TODO dump out errors
        
        return None
        

    def create_sources(self, sources_string):
        
        sources = []
        
        for source in sources_string.split(';'):
            
            try:
                dates = next(datefinder.find_dates(source, index=True))
            except StopIteration:
                continue
            
            dates, indices = dates
            
            before_date, after_date = source[:indices[0]], source[indices[1]:]
            
            # Source title, publication title and publication country should be
            # before the date. If not, skip it

            try:
                source_title, pub_title = before_date.split('.', 1)
            except ValueError:
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

    def create_organization(self, org_data):
        # Name, Aliases, Classification
        organization = None

        field_positions = {
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
        
        # Need to get or create name first
        name_value = org_data[field_positions['Name']['value']]
        confidence = org_data[field_positions['Name']['confidence']].strip().lower()
        source = org_data[field_positions['Name']['source']]
        
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
                                             field_positions['Alias'], 
                                             org_data, 
                                             organization)
                
                classification = self.make_relation('Classification',
                                                    field_positions['Classification'],
                                                    org_data,
                                                    organization)
            
                self.stdout.write(self.style.SUCCESS('Created {}'.format(organization.get_value())))

            else:
                self.stdout.write(self.style.ERROR('Skipping {}'.format(name_value)))
        
        else:
            self.stdout.write(self.style.ERROR('Skipping {}'.format(name_value)))
        
        return organization

    def create_person(self, person_dict):
        pass

    def create_event(self, event_dict):
        pass

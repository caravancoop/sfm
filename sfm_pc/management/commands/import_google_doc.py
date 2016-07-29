import os
import json
from collections import OrderedDict

import httplib2

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from django.core.management.base import BaseCommand, CommandError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

class Command(BaseCommand):
    help = 'Import data from Google Drive Spreadsheet'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--doc_id',
            dest='doc_id',
            default='1Jom4qjn3RnEGGxpBNqMIeEBZC7M8JiOl2g1sPTCiBas',
            help='Import data from specified Google Drive Document'
        )
    
    def get_credentials(self):
        
        this_dir = os.path.dirname(__file__)
        secrets_path = os.path.join(this_dir, 'credentials.json')
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(secrets_path, 
                                                                       SCOPES)
        return credentials
    
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
        
        self.stdout.write(self.style.SUCCESS('Creating organizations ... '))
        
        for sheet in org_sheets.values():

            header = sheet[0]
            
            for row in sheet[1:]:
                if row:
                    org_data = OrderedDict(zip(header, row))
                    self.create_organization(org_data)

        self.stdout.write(self.style.SUCCESS('Successfully imported data from {}'.format(options['doc_id'])))

    def create_organization(self, org_dict):
        name = org_dict['Name']

    def create_person(self, person_dict):
        pass

    def create_event(self, event_dict):
        pass

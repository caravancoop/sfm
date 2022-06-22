import os
import csv
import io

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import httplib2

from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Download entity, source, and location data from Google'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sources_doc_id',
            dest='sources_doc_id',
            default='1o-K13Od1pGc7FOQ-JS8LJW9Angk3_UPZHTmOU7hD3wU',
            help='Import data from specified Google Sheets Document'
        )
        
        parser.add_argument(
            '--location_doc_id',
            dest='location_doc_id',
            help='Import location data from specified Google Drive file'
        )

        parser.add_argument(
            '--entity_doc_id',
            dest='entity_doc_id',
            default='1o-K13Od1pGc7FOQ-JS8LJW9Angk3_UPZHTmOU7hD3wU',
            help='Import data from specified Google Sheets Document'
        )
        
        parser.add_argument(
            '--country_code',
            dest='country_code',
            help='Country code for the import'
        )

    def handle(self, *args, **kwargs):
        entity_doc_id = kwargs['entity_doc_id']
        location_doc_id = kwargs['location_doc_id']
        sources_doc_id = kwargs['sources_doc_id']
        country_code = kwargs['country_code'].rstrip()
        
        parent_directory = f'data'
        country_directory = f'{parent_directory}/countries/{country_code}'

        self._create_csv_files(
            entity_doc_id=entity_doc_id,
            sources_doc_id=sources_doc_id,
            country_directory=country_directory,
            sources_directory=parent_directory
        )

        self._create_location_file(location_doc_id, country_directory)
    
    def _create_location_file(self, location_doc_id, output_directory):
        downloader, buffer = self._build_location_downloader(location_doc_id)
        
        self.stdout.write('Downloading locations file...')
        
        done = False

        with tqdm(total=100) as progress_bar:
            while not done:
                status, done = downloader.next_chunk()
                progress_bar.update(int(status.progress() * 100) - progress_bar.n)

        buffer.seek(0)
        
        target = f'{output_directory}/locations.geojson'

        with open(target, 'wb') as f:
            f.write(buffer.getbuffer())

        self.stdout.write(
            self.style.SUCCESS('Downloaded locations file to {}'.format(target))
        )
    
    def _build_location_downloader(self, location_doc_id):
        drive_service = self._build_google_service(
            scopes=['https://www.googleapis.com/auth/drive.readonly'],
            service='drive',
            version='v3'
        )

        request = drive_service.files().get_media(fileId=location_doc_id)
        
        location_buffer = io.BytesIO()
        return MediaIoBaseDownload(location_buffer, request), location_buffer
    
    def _create_csv_files(
            self,
            entity_doc_id,
            sources_doc_id,
            country_directory,
            sources_directory
        ):
        
        sheets_service = self._build_google_service(
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'],
            service='sheets',
            version='v4'
        )
        
        self._create_sources_file(
            sheets_service=sheets_service,
            document_id=sources_doc_id,
            output_directory=sources_directory
        )
        
        self._create_entity_files(
            sheets_service=sheets_service,
            document_id=entity_doc_id,
            output_directory=country_directory
        )

    def _create_sources_file(self, sheets_service, document_id, output_directory):
        target = f'{output_directory}/sources.csv'
        
        # No need to keep downloading the same data
        if os.path.exists(target):
            return
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
    
        workbook_metadata = self._get_workbook_metadata(
            sheets_service,
            document_id
        )
        
        local_workbook = self._download_workbook(
            sheets_service,
            workbook_metadata,
            document_id
        )
        
        for key, sheet in local_workbook.items():
            if key == 'sources':
                with open(target, 'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(sheet)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Saved sheets file to {target}')
                    )

    def _create_entity_files(self, sheets_service, document_id, output_directory):
        workbook_metadata = self._get_workbook_metadata(
            sheets_service,
            document_id
        )
        
        local_workbook = self._download_workbook(
            sheets_service,
            workbook_metadata,
            document_id
        )

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        for key, sheet in local_workbook.items():
            target = f'{output_directory}/{key}.csv'

            with open(target, 'w') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(sheet)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Saved sheets file to {target}')
                )

    def _download_workbook(self, sheets_service, workbook_metadata, document_id):
        self.stdout.write(f'Downloading {document_id} sheets workbook...')

        workbook_title = workbook_metadata['properties']['title']
        local_workbook = {}
        
        for sheet in workbook_metadata['sheets']:
            title = sheet['properties']['title']
            sheet_data = sheets_service.spreadsheets().values().get(
                spreadsheetId=document_id,
                range=title
            ).execute()

            local_workbook.update({
                title: sheet_data['values']
            })
        
        return local_workbook
    
    def _get_workbook_metadata(self, sheets_service, document_id):
        response = sheets_service.spreadsheets().get(
            spreadsheetId=document_id,
            includeGridData=False
        ).execute()
        
        return response
    
    def _build_google_service(self, scopes, service, version):
        credentials = self.get_credentials(scopes=scopes)
        http = credentials.authorize(httplib2.Http())
        return build(service, version, http=http)
    
    def get_credentials(self, *, scopes, credentials_file='credentials.json'):
        this_dir = os.path.dirname(__file__)
        secrets_path = os.path.join(this_dir, credentials_file)

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            secrets_path,
            scopes
        )

        return credentials

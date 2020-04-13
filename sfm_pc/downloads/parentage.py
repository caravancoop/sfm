from .base import BaseDownload
from composition.models import Composition
from organization.models import Organization


class ParentageDownload(BaseDownload):
    download_type = 'parentage'
    selected_fields = [
        {
            'name': 'child.uuid',
            'label': 'unit:id:admin'
        },
        {
            'name': 'child.name',
            'label': Organization.get_spreadsheet_field_name('name')
        },
        {
            'name': 'child.name_sources',
            'label': Organization.get_spreadsheet_source_field_name('name'),
            'source': True
        },
        {
            'name': 'child.name_confidence',
            'label': Organization.get_spreadsheet_confidence_field_name('name'),
            'confidence': True
        },
        {
            'name': 'child.division_id',
            'label': Organization.get_spreadsheet_field_name('division_id')
        },
        {
            'name': 'child.division_id_sources',
            'label': Organization.get_spreadsheet_source_field_name('division_id'),
            'source': True
        },
        {
            'name': 'child.division_id_confidence',
            'label': Organization.get_spreadsheet_confidence_field_name('division_id'),
            'confidence': True
        },
        {
            'name': 'child.classifications',
            'label': Organization.get_spreadsheet_field_name('classification')
        },
        {
            'name': 'child.classifications_sources',
            'label': Organization.get_spreadsheet_source_field_name('classification'),
            'source': True
        },
        {
            'name': 'child.classifications_confidence',
            'label': Organization.get_spreadsheet_confidence_field_name('classification'),
            'confidence': True
        },
        {
            'name': 'child.aliases',
            'label': Organization.get_spreadsheet_field_name('aliases')
        },
        {
            'name': 'child.aliases_sources',
            'label': Organization.get_spreadsheet_source_field_name('aliases'),
            'source': True
        },
        {
            'name': 'child.aliases_confidence',
            'label': Organization.get_spreadsheet_confidence_field_name('aliases'),
            'confidence': True
        },
        {
            'name': 'child.first_cited_date',
            'label': Organization.get_spreadsheet_field_name('firstciteddate')
        },
        {
            'name': 'child.first_cited_date_sources',
            'label': Organization.get_spreadsheet_source_field_name('firstciteddate'),
            'source': True
        },
        {
            'name': 'child.first_cited_date_confidence',
            'label': Organization.get_spreadsheet_confidence_field_name('firstciteddate'),
            'confidence': True
        },
        {
            'name': 'child.real_start',
            'label': Organization.get_spreadsheet_field_name('realstart')
        },
        {
            'name': 'child.real_start_sources',
            'label': Organization.get_spreadsheet_source_field_name('realstart'),
            'source': True
        },
        {
            'name': 'child.real_start_confidence',
            'label': Organization.get_spreadsheet_confidence_field_name('realstart'),
            'confidence': True
        },
        {
            'name': 'child.last_cited_date',
            'label': Organization.get_spreadsheet_field_name('lastciteddate')
        },
        {
            'name': 'child.last_cited_date_sources',
            'label': Organization.get_spreadsheet_source_field_name('lastciteddate'),
            'source': True
        },
        {
            'name': 'child.last_cited_date_confidence',
            'label': Organization.get_spreadsheet_confidence_field_name('lastciteddate'),
            'confidence': True
        },
        {
            'name': 'child.open_ended',
            'label': Organization.get_spreadsheet_field_name('open_ended')
        },
        {
            'name': 'child.open_ended_sources',
            'label': Organization.get_spreadsheet_source_field_name('open_ended'),
            'source': True
        },
        {
            'name': 'child.open_ended_confidence',
            'label': Organization.get_spreadsheet_confidence_field_name('open_ended'),
            'confidence': True
        },
        {
            'name': 'parent.uuid',
            'label': Composition.get_spreadsheet_field_name('parent')
        },
        {
            'name': 'parent.name',
            'label': Composition.get_spreadsheet_field_name('parent') + ':name'
        },
        {
            'name': 'parent.name_sources',
            'label': Composition.get_spreadsheet_field_name('parent') + ':name:source',
            'source': True
        },
        {
            'name': 'parent.name_confidence',
            'label': Composition.get_spreadsheet_field_name('parent') + ':name:confidence',
            'confidence': True
        },
        {
            'name': 'parent.division_id',
            'label': Composition.get_spreadsheet_field_name('parent') + ':country'
        },
        {
            'name': 'parent.division_id_sources',
            'label': Composition.get_spreadsheet_field_name('parent') + ':country:source',
            'source': True
        },
        {
            'name': 'parent.division_id_confidence',
            'label': Composition.get_spreadsheet_field_name('parent') + ':country:confidence',
            'confidence': True
        },
        {
            'name': 'composition.classifications',
            'label': Composition.get_spreadsheet_field_name('classification')
        },
        {
            'name': 'composition.classifications_sources',
            'label': Composition.get_spreadsheet_source_field_name('classification'),
            'source': True
        },
        {
            'name': 'composition.classifications_confidence',
            'label': Composition.get_spreadsheet_confidence_field_name('classification'),
            'confidence': True
        },
        {
            'name': 'composition.first_cited_date',
            'label': Composition.get_spreadsheet_field_name('startdate')
        },
        {
            'name': 'composition.first_cited_date_sources',
            'label': Composition.get_spreadsheet_source_field_name('startdate'),
            'source': True
        },
        {
            'name': 'composition.first_cited_date_confidence',
            'label': Composition.get_spreadsheet_confidence_field_name('startdate'),
            'confidence': True
        },
        {
            'name': 'composition.real_start',
            'label': Composition.get_spreadsheet_field_name('realstart')
        },
        {
            'name': 'composition.real_start_sources',
            'label': Composition.get_spreadsheet_source_field_name('realstart'),
            'source': True
        },
        {
            'name': 'composition.real_start_confidence',
            'label': Composition.get_spreadsheet_confidence_field_name('realstart'),
            'confidence': True
        },
        {
            'name': 'composition.last_cited_date',
            'label': Composition.get_spreadsheet_field_name('enddate')
        },
        {
            'name': 'composition.last_cited_date_sources',
            'label': Composition.get_spreadsheet_source_field_name('enddate'),
            'source': True
        },
        {
            'name': 'composition.last_cited_date_confidence',
            'label': Composition.get_spreadsheet_confidence_field_name('enddate'),
            'confidence': True
        },
        {
            'name': 'composition.open_ended',
            'label': Composition.get_spreadsheet_field_name('open_ended')
        },
        {
            'name': 'composition.open_ended_sources',
            'label': Composition.get_spreadsheet_source_field_name('open_ended'),
            'source': True
        },
        {
            'name': 'composition.open_ended_confidence',
            'label': Composition.get_spreadsheet_confidence_field_name('open_ended'),
            'confidence': True
        },
    ]

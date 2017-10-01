import uuid
from collections import namedtuple
import csv
from io import BytesIO
import zipfile

from django.db import models, connection
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext as _
from django.db.models import Max

from django_date_extensions.fields import ApproximateDateField

from complex_fields.model_decorators import versioned, translated, sourced
from complex_fields.models import ComplexField, ComplexFieldContainer, \
    ComplexFieldListContainer
from complex_fields.base_models import BaseModel


class Person(models.Model, BaseModel):
    
    uuid = models.UUIDField(default=uuid.uuid4, 
                            editable=False, 
                            db_index=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ComplexFieldContainer(self, PersonName)
        self.aliases = ComplexFieldListContainer(self, PersonAlias)
        self.division_id = ComplexFieldContainer(self, PersonDivisionId)
        
        self.complex_fields = [self.name, self.division_id]

        self.required_fields = [
            "Person_PersonName",
        ]

    def get_value(self):
        return self.name.get_value()

    def __str__(self):
        return str(self.name)

    @classmethod
    def download(self, person_ids):
        table_attrs = ['name', 'alias', 'firstciteddate', 'lastciteddate',
                       'membership', 'rank', 'role', 'title']

        table_fmt = 'person_{0}_export'
        tables = (table_fmt.format(attr) for attr in table_attrs)

        query_fmt = '''
            SELECT * FROM {table}
            WHERE person_id = %s
        '''

        col_query_fmt = '''
            SELECT * FROM {table}
            LIMIT 0
        '''

        for table in tables:

            col_query = col_query_fmt.format(table)
            col_cursor = connection.cursor()
            cursor.execute(col_query)

            columns = [c[0] for c in cursor.description]

            csvfile = BytesIO()
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()

            row_fmt = {colname: '' for colname in cols}

            for person_id in person_ids:

                query = query_fmt.format(table=table)
                q_args = [person_id]

                cursor = connection.cursor()
                cursor.execute(query, q_args)

                results_tuple = namedtuple(table, columns)

                results = [results_tuple(*r) for r in cursor]

                for res in results:
                    row = {}

                    for colname in columns:
                        row[colname] = getattr(results, colname, '')

                    writer.writerow(row)

        return




@translated
@versioned
@sourced
class PersonName(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)
    field_name = _("Name")


@translated
@versioned
@sourced
class PersonAlias(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.ForeignKey('Alias', default=None, blank=True, null=True)
    field_name = _("Alias")

class Alias(models.Model):
    value = models.TextField()
    
    def __str__(self):
        return self.value

@versioned
@sourced
class PersonDivisionId(ComplexField):
    object_ref = models.ForeignKey('Person')
    value = models.TextField(default=None, blank=True, null=True)

    field_name = _('Division ID')

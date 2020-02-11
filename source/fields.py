from django.db import models
import django_date_extensions.fields


class SpreadsheetFieldNameMixin:
    """
    Mixin for Django Field classes providing the ability to specify a
    spreadsheet_field_name attribute for a field.
    """
    def __init__(self, *args, **kwargs):
        if kwargs.get('spreadsheet_field_name'):
            self.spreadsheet_field_name = kwargs.pop('spreadsheet_field_name')
        super().__init__(*args, **kwargs)


class TextField(SpreadsheetFieldNameMixin, models.TextField):
    pass


class CharField(SpreadsheetFieldNameMixin, models.CharField):
    pass


class DateField(SpreadsheetFieldNameMixin, models.DateField):
    pass


class ApproximateDateField(SpreadsheetFieldNameMixin, django_date_extensions.fields.ApproximateDateField):
    pass


class URLField(SpreadsheetFieldNameMixin, models.URLField):
    pass

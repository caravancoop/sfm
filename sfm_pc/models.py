from complex_fields.models import ComplexFieldContainer


class GetComplexSpreadsheetFieldNameMixin:
    """
    Mixin to allow models with ComplexFields to retrieve the
    spreadsheet field names for a given ComplexField.
    """
    @classmethod
    def get_spreadsheet_field_name(cls, field_name):
        """
        Get the spreadsheet field name for a given field_name. For instance,
        the spreadsheet field name for Person.name would be 'person:name'.
        """
        # Get the 0th ID instance, to indicate that we don't want a specific instance
        # (for more information on these methods, see the source code in the
        # complex_fields app)
        container = ComplexFieldContainer.field_from_str_and_id(
            cls.__name__.lower(), '0', field_name
        )
        field_model = container.field_model()
        return field_model.spreadsheet_field_name

    @classmethod
    def get_spreadsheet_confidence_field_name(cls, field_name):
        """
        Get the spreadsheet confidence field name for a given field_name. For
        instance, the spreadsheet confidence field name for Person.name would
        be 'person:name:confidence'.
        """
        return cls.get_spreadsheet_field_name(field_name) + ':confidence'

    @classmethod
    def get_spreadsheet_source_field_name(cls, field_name):
        """
        Get the spreadsheet source field name for a given field_name. For
        instance, the spreadsheet source field name for Person.name would
        be 'person:name:source'.
        """
        return cls.get_spreadsheet_field_name(field_name) + ':source'

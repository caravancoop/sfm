from django.utils.translation import get_language_bidi

from django_date_extensions.fields import ApproximateDateField


class I10nApproximateDateField(ApproximateDateField):

    def from_db_value(self, value, expression=None, connection=None, context=None):
        value = super().from_db_value(value, expression, connection, context)

        if value and get_language_bidi():
            date_parts = str(value).split(' ')
            date_parts.reverse()
            return ' '.join(date_parts)

        return value

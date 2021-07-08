from django.utils.translation import get_language_bidi

from django_date_extensions.fields import ApproximateDateField


class I10nApproximateDateField(ApproximateDateField):

    def from_db_value(self, value, expression=None, connection=None, context=None):
        '''
        The django_date_extensions module defines a custom ApproximateDate class
        that is not a datetime, i.e., cannot be localized using the usual Django
        localization mechanisms.

        Extend this method to reverse available date parts, in the event that
        the active language should be read right to left rather than left to
        right, the direction of the default language (English) and therefore the
        direction in which the date format is specified in settings.py.
        '''
        value = super().from_db_value(value, expression, connection, context)

        if value and get_language_bidi():
            date_parts = str(value).split(' ')
            date_parts.reverse()
            return ' '.join(date_parts)

        return value

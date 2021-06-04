import itertools

from complex_fields.models import ComplexFieldContainer, ComplexFieldListContainer
from django.db.models import QuerySet

from source.models import Source


class SourcesMixin:
    @property
    def sources(self):
        access_points = set()

        for field in itertools.chain(self.complex_fields, self.complex_lists):
            if isinstance(field, ComplexFieldListContainer):
                field = field.get_complex_field(None)
                assert field

            field_sources = field.get_sources()

            if field_sources and isinstance(field_sources, QuerySet):  # Empty list if unsourced
                access_points.update(list(field_sources))

        return Source.objects.filter(accesspoint__in=access_points).distinct('source_url')

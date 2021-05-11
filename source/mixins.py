import itertools

from complex_fields.models import ComplexFieldContainer, ComplexFieldListContainer


class SourcesMixin:
    @property
    def sources(self):
        sources = []

        for field in itertools.chain(self.complex_fields, self.complex_lists):
            if isinstance(field, ComplexFieldListContainer):
                field = field.get_complex_field(None)
                assert field

            sources += [accesspoint.source for accesspoint in field.get_sources()]

        return set(sources)

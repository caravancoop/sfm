from django.utils.translation import ugettext as _
from django.db import models

CONFIDENCE_LEVELS = (
    ('1', _('Low')),
    ('2', _('Medium')),
    ('3', _('High')),
)

class Source(models.Model):
    source = models.TextField()
    confidence = models.CharField(max_length=1, choices=CONFIDENCE_LEVELS)

    @classmethod
    def create_sources(cls, sources):
        sources = []
        for source in sources:
            possible_source = Source.objects.filter(
                source=source['source'],
                confidence=source['confidence']
            )
            possible_source = list(possible_source[:1])
            if possible_source:
                sources.append(possible_source)
            else:
                new_source = cls(source['source'], source['confidence'])
                new_source.save()
                sources.append(new_source)

        return sources


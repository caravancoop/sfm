from django.utils.translation import ugettext as _
from django.utils.translation import activate, get_language
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
    def create_sources(cls, sources_dict):
        sources = []
        for src in sources_dict:
            possible_source = Source.objects.filter(
                source=src['source'],
                confidence=src['confidence']
            )
            possible_source = list(possible_source[:1])
            if possible_source:
                sources.append(possible_source[0])
            else:
                new_source = cls(source=src['source'], confidence=src['confidence'])
                new_source.save()
                sources.append(new_source)

        return sources

    @classmethod
    def get_sources(cls, source_ids):
        sources = cls.objects.filter(id__in = source_ids)
        return sources

    @classmethod
    def get_confidences(cls, lang=get_language()):
        activate(lang)
        confs = {}
        for conf in CONFIDENCE_LEVELS:
            confs[conf[0]]= conf[1]

        return confs

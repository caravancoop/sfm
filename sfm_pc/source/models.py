from django.db import models


class Source(models.Model):
    source = models.TextField()

    @classmethod
    def create_sources(cls, sources):
        srcs = []
        for src in sources:
            try:
                existing_source = Source.objects.get(source=src['source'])
                srcs.append(existing_source)
            except Source.DoesNotExist:
                new_source = cls(source=src['source'])
                new_source.save()
                srcs.append(new_source)

        return srcs

    @classmethod
    def get_sources(cls, source_ids):
        sources = cls.objects.filter(id__in = source_ids)
        return sources

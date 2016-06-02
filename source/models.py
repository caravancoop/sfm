from django.db import models

class Publication(models.Model):
    uuid = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    country_iso = models.CharField(max_length=2)
    country_name = models.CharField(max_length=255)
    
    def __str__(self):
        if self.title is None:
            return ""
        return self.title

class Source(models.Model):
    title = models.TextField()
    publication = models.ForeignKey(Publication, null=True)
    published_on = models.DateField()
    source_url = models.URLField()
    archive_url = models.URLField()

    def __str__(self):
        if self.title is None:
            return ""
        return self.title

    @classmethod
    def create_sources(cls, sources):
        # TODO: This does not seem to be used anywhere. Is it needed?
        srcs = []
        for src in sources:
            try:
                existing_source = Source.objects.get(source=src.title)
                srcs.append(existing_source)
            except Source.DoesNotExist:
                new_source = cls(source=src['source'])
                new_source.save()
                srcs.append(new_source)

        return srcs

    @classmethod
    def get_sources(cls, source_ids):
        sources = cls.objects.filter(id__in=source_ids)
        return sources

import threading

import requests

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Publication(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.TextField()
    country = models.CharField(max_length=255, null=True)
    
    def __str__(self):
        if self.title is None:
            return ""
        return self.title

class Source(models.Model):
    title = models.TextField()
    publication = models.ForeignKey(Publication, null=True)
    published_on = models.DateField()
    source_url = models.URLField(max_length=1000, null=True)
    archive_url = models.URLField(max_length=1000, null=True)

    def __str__(self):
        if self.title is None:
            return ""
        return self.title

    @classmethod
    def get_sources(cls, source_ids):
        sources = cls.objects.filter(id__in=source_ids)
        return sources

def archive_source_url(source):
    
    if source.source_url:
        wayback_host = 'http://web.archive.org'
        save_url = '{0}/save/{1}'.format(wayback_host, source.source_url)
        archived = requests.get(save_url)
        source.archive_url = '{0}{1}'.format(wayback_host, 
                                             archived.headers['Content-Location'])
        source.save()

#@receiver(post_save, sender=Source)
def get_archived_url(sender, **kwargs):
    
    source = kwargs['instance']
    
    thread = threading.Thread(target=archive_source_url, 
                              args=[source])
    thread.start()

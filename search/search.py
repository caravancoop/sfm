import pysolr

from django.conf import settings

class Searcher(pysolr.Solr):
    def __init__(self, *args, **kwargs):
        self.url = settings.SOLR_URL
        
        super().__init__(self.url, *args, **kwargs)

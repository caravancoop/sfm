from django.db import models
from django.contrib.gis.db.models.fields import GeometryField

class Location(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    country_code = models.TextField(blank=True, null=True)
    feature_type = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    geometry = GeometryField(blank=True, null=True)

    def __str__(self):
        if self.name is None:
            return self.id
        return self.name

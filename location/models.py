from django.db import models
from django.contrib.gis.db.models.fields import GeometryField
from django.contrib.postgres.fields import JSONField

class Location(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    division_id = models.TextField(blank=True, null=True)
    feature_type = models.TextField(blank=True, null=True)
    tags = JSONField(blank=True, null=True)
    geometry = GeometryField(blank=True, null=True)

    def __str__(self):
        if self.name is None:
            return self.id
        return self.name

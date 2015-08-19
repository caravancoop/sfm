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

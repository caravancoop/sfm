from django.db import models
from django.db.models.signals import class_prepared

from reversion import register


def translatable(orig_cls):
    orig_save = orig_cls.save


    # orig_cls.lang = models.CharField(max_length=5, null=False)
    # orig_cls._meta.unique_together = (('object', 'lang'), )

    def save(self, *args, **kwargs):
        print("Apply magic translation sauce")
        return orig_save(self, *args, **kwargs)

    orig_cls.save = save
    return orig_cls


def versioned(orig_cls):
    register(orig_cls)
    return orig_cls

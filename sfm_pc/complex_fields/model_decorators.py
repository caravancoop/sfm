from django.db import models
from django.db.models.signals import class_prepared

from reversion import register
from django.db import models
from source.models import Source


def translated(orig_cls):
    translated = True
    """
    orig_save = orig_cls.save

    # Find a way to set the lang field and the constraint here sometime
    # orig_cls.lang = models.CharField(max_length=5, null=False)
    # orig_cls._meta.unique_together = (('object', 'lang'), )

    def save(self, *args, **kwargs):
        print("Apply magic translation sauce")
        return orig_save(self, *args, **kwargs)

    @classmethod
    def from_object_ids(cls, id_):
        queryset = cls.objects.filter(id=id_)

    orig_cls.save = save
    orig_cls._save = orig_save
    """
    return orig_cls

def versioned(orig_cls):
    versioned = True
    register(orig_cls)
    return orig_cls


def sourced(orig_cls):
    sourced = True
    """
    orig_save = orig_cls.save

    def save(self, *args, **kwargs):
        print("Apply magic sourcing sauce")
        return orig_save(self, *args, **kwargs)

    orig_cls.save = save
    orig_cls._save = orig_save
    """
    return orig_cls

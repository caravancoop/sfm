import functools

from django.db import models
from django.db.models.signals import class_prepared

from reversion import register
from django.db import models
from source.models import Source


def translated(orig_cls):
    orig_cls.translated = True
    return orig_cls

def versioned(orig_cls):
    orig_cls.versioned = True
    register(orig_cls)
    return orig_cls

def sourced(orig_cls):
    orig_cls.sourced = True
    orig_cls.source_required = True
    return orig_cls

def sourced_optional(orig_cls):
    orig_cls.sourced = True
    return orig_cls

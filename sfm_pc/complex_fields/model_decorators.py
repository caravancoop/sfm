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
    return orig_cls

class combomethod(object):
    def __init__(self, method):
        self.method = method

    def __get__(self, obj=None, objtype=None):
        @functools.wraps(self.method)
        def _wrapper(*args, **kwargs):
            if obj is not None:
                return self.method(obj, *args, **kwargs)
            else:
                return self.method(objtype, *args, **kwargs)

        return _wrapper

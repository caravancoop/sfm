from django.db import models
from django.db.models.signals import class_prepared

from reversion import register
from django.db import models
from source.models import Source


def translatable(orig_cls):
    orig_save = orig_cls.save

    # Find a way to set the lang field and the constraint here sometime
    # orig_cls.lang = models.CharField(max_length=5, null=False)
    # orig_cls._meta.unique_together = (('object', 'lang'), )

    @classmethod
    def translate(cls, object_id, value, lang):
        translations = cls.objects.filter(object=object_id)
        if not translations.exists:
            raise FieldDoesNotExist("Can't translate a field that doesn't exist")

        translation = translations.filter(lang=lang).list(translations[:1])
        if not translation:
            translation = cls()
            translation.object = object_id
            translation.lang = lang

        if hasattr(translation[0], 'sources'):
            sources = translations[0].sources

        translation.value = value

    @classmethod
    def update(cls, object_id, value, lang, sources):
        translations = cls.objects.filter(object=object_id)
        if not translations.exists:
            raise FieldDoesNotExist("Can't update a field that doesn't exist")

        for trans in translations:
            trans.val = None
            if hasattr(trans, 'sources'):
                trans.sources = None

        translation = translations.filter(lang=lang).list(translations[:1])
        if not translation:
            translation = cls()
            translation.object = object_id
            translation.lang = lang

        if hasattr(translation, 'sources'):
            translation.sources = sources

        translation.value = value

    def save(self, *args, **kwargs):
        import ipdb; ipdb.set_trace()
        print("Apply magic translation sauce")
        return orig_save(self, *args, **kwargs)

    @classmethod
    def from_object_ids(cls, id_):
        queryset = cls.objects.filter(id=id_)

    orig_cls.save = save
    orig_cls._save = orig_save
    return orig_cls


def versioned(orig_cls):
    register(orig_cls)
    return orig_cls


def sourced(orig_cls):
    orig_save = orig_cls.save

    def save(self, *args, **kwargs):
        print("Apply magic sourcing sauce")
        return orig_save(self, *args, **kwargs)

    orig_cls.save = save
    orig_cls._save = orig_save

    return orig_cls

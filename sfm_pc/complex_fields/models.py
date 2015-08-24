from django.db import models
from source.models import Source

class ComplexField(models.Model):
    lang = models.CharField(max_length=5, null=False)
    sources = models.ManyToManyField(Source, related_name="%(app_label)s_%(class)s_related")

    class Meta:
        abstract = True
        unique_together = ('object', 'lang')

    @classmethod
    def translate(cls, object, value, lang):
        translations = cls.objects.filter(object=object)
        if not translations.exists:
            raise FieldDoesNotExist("Can't translate a field that doesn't exist")

        translation = translations.filter(lang=lang)
        translation = list(translation[:1])
        if not translation:
            translation = cls()
            translation.object = object
            translation.lang = lang

        if hasattr(translation[0], 'sourced'):
            sources = translations[0].sources

        translation.value = value

    @classmethod
    def update(cls, object, value, lang, sources):
        translations = cls.objects.filter(object=object)
        if not translations.exists:
            raise FieldDoesNotExist("Can't update a field that doesn't exist")

        for trans in translations:
            trans.val = None
            if hasattr(trans, 'sourced'):
                trans.sources = None

        translation = translations.filter(lang=lang)
        translation = list(translation[:1])
        if not translation:
            translation = cls()
            translation.object = object
            translation.lang = lang

        if hasattr(translation, 'sources'):
            translation.sources = sources

        translation.value = value

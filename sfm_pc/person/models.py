import reversion

from django.db import models

class Person(models.Model):
    def get_name(self, lang='en'):
        return self.get_attribute(PersonName, lang)

    def get_alias(self, lang='en'):
        return self.get_attribute(PersonAlias, lang)

    def get_notes(self, lang='en'):
        return self.get_attribute(PersonNotes, lang)

    def get_attribute(self, object_type, lang='en'):
        queryset = object_type.objects.filter(person=self, lang=lang)
        values = list(queryset[:1])
        if values:
            return values[0].value
        return None

class PersonName(models.Model):
    person = models.ForeignKey('Person')
    lang = models.CharField(max_length=5, null=False)
    value = models.TextField()

    class Meta:
        unique_together = ('person', 'lang')

reversion.register(PersonName)

class PersonAlias(models.Model):
    person = models.ForeignKey('Person')
    lang = models.CharField(max_length=5, null=False)
    value = models.TextField()

    class Meta:
        unique_together = ('person', 'lang')

reversion.register(PersonAlias)

class PersonNotes(models.Model):
    person = models.ForeignKey('Person')
    lang = models.CharField(max_length=5, null=False)
    value = models.TextField()

    class Meta:
        unique_together = ('person', 'lang')

reversion.register(PersonNotes)

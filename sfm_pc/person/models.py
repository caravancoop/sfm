from django.db import models
import reversion

class Person(models.Model):
    pass

class PersonName(models.Model):
    lang = models.CharField(max_length=5, null=False)
    person = models.ForeignKey(Person)
    value = models.TextField()

reversion.register(PersonName)

class PersonAlias(models.Model):
    lang = models.CharField(max_length=5, null=False)
    person = models.ForeignKey(Person)
    value = models.TextField()

reversion.register(PersonAlias)

class PersonNotes(models.Model):
    lang = models.CharField(max_length=5, null=False)
    person = models.ForeignKey(Person)
    value = models.TextField()

reversion.register(PersonNotes)

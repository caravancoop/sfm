import reversion
import json

from django.test import TestCase
from django.db import models
from django.core.exceptions import ValidationError, FieldDoesNotExist
from unittest.mock import MagicMock
from .models import ComplexField
from .model_decorators import translated, versioned, sourced
from source.models import Source
from person.models import Person, PersonName

class ComplexFieldTestCase(TestCase):


    def setUp(self):
        self.person = Person.objects.create()
        self.source = Source.objects.create(source="A source", confidence='1')
        self.person_name = PersonName(
            object=self.person,
            lang="FR",
            value="Aujourd'hui"
        )
        self.person_name.save()
        self.person_name.sources.add(self.source)
        with reversion.create_revision():
            self.person_name.save()

    def test_translate_new(self):
        PersonName.translate(self.person, 'Today', 'EN')

        translations = PersonName.objects.filter(object=self.person)
        self.assertEqual(len(translations), 2)

        languages = [
            ('FR', self.source, 1, "Aujourd'hui"),
            ('EN', self.source, 1, "Today")
        ]
        langs = [
            (trans.lang, trans.sources.first(), len(trans.sources.all()), trans.value)
            for trans in translations
        ]
        self.assertCountEqual(langs, languages)

    def test_translate_existing_fail(self):
        with self.assertRaises(ValidationError):
            PersonName.translate(self.person, 'Today', 'FR')

    def test_translate_inexisting_field_fail(self):
        other_person = Person.objects.create()
        with self.assertRaises(FieldDoesNotExist):
            PersonName.translate(other_person, 'Ayer', 'ES')


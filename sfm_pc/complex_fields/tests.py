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

    def test_update_alone_field(self):
        PersonName.update(self.person, 'Demain', 'FR', [self.source])

        translations = PersonName.objects.filter(object=self.person)
        self.assertEqual(len(translations), 1)

        language = translations[0].lang
        self.assertEqual('FR', language)

    def test_update_multiple_field(self):
        PersonName.translate(self.person, 'Tomorrow', 'EN')
        PersonName.translate(self.person, 'Mañana', 'ES')
        PersonName.update(self.person, 'Ayer', 'ES', [self.source])

        translations = PersonName.objects.filter(object=self.person)
        self.assertEqual(len(translations), 3)

        values = [
            (None, 0),
            (None, 0),
            ("Ayer", 1)
        ]
        vals = [
            (trans.value, len(trans.sources.all()))
            for trans in translations
        ]

        self.assertCountEqual(values, vals)
        language = translations[0].lang

    def test_update_new_lang(self):
        PersonName.translate(self.person, 'Tomorrow', 'EN')
        PersonName.update(self.person, 'Ayer', 'ES', [self.source])

        translations = PersonName.objects.filter(object=self.person)
        self.assertEqual(len(translations), 3)

        values = [
            (None, 0),
            (None, 0),
            ("Ayer", 1)
        ]
        vals = [
            (trans.value, len(trans.sources.all()))
            for trans in translations
        ]

        self.assertCountEqual(values, vals)
        language = translations[0].lang

    def test_history_get(self):
        with reversion.create_revision():
            PersonName.update(self.person, 'Now', 'EN', [self.source])
        with reversion.create_revision():
            PersonName.translate(self.person, 'Maintenant', 'FR')
        with reversion.create_revision():
            PersonName.translate(self.person, 'Ahora', 'ES')
        with reversion.create_revision():
            PersonName.update(self.person, 'Demain', 'FR', [self.source])
        with reversion.create_revision():
            PersonName.update(self.person, 'YYYY', 'IT', [self.source])
        with reversion.create_revision():
            PersonName.translate(self.person, 'Hier', 'FR')
        fr_trans = PersonName.objects.get(object=self.person, lang='FR')
        fr_version_list = reversion.get_for_object(fr_trans)
        results = [
            json.loads(fr_version.serialized_data)[0]['fields']
            for fr_version in fr_version_list
        ]
        expected_results = [
            {'lang': 'FR', 'object': 1, 'sources': [1], 'value': "Hier"},
            {'lang': 'FR', 'object': 1, 'sources': [], 'value': None},
            {'lang': 'FR', 'object': 1, 'sources': [1], 'value': "Demain"},
            {'lang': 'FR', 'object': 1, 'sources': [1], 'value': "Maintenant"},
            {'lang': 'FR', 'object': 1, 'sources': [], 'value': None},
            {'lang': 'FR', 'object': 1, 'sources': [1], 'value': "Aujourd'hui"},
        ]
        self.maxDiff = None
        self.assertCountEqual(expected_results, results)

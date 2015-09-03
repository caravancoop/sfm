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
            lang="fr",
            value="Aujourd'hui"
        )
        self.person_name.save()
        self.person_name.sources.add(self.source)
        with reversion.create_revision():
            self.person_name.save()

    def test_translate_new(self):
        self.person.name.translate('Today', 'en')

        translations = PersonName.objects.filter(object=self.person)
        self.assertEqual(len(translations), 2)

        languages = [
            ('fr', self.source, 1, "Aujourd'hui"),
            ('en', self.source, 1, "Today")
        ]
        langs = [
            (trans.lang, trans.sources.first(), len(trans.sources.all()), trans.value)
            for trans in translations
        ]
        self.assertCountEqual(langs, languages)

    def test_translate_existing_fail(self):
        with self.assertRaises(ValidationError):
            self.person.name.translate('Today', 'fr')

    def test_translate_inexisting_field_fail(self):
        other_person = Person.objects.create()
        with self.assertRaises(FieldDoesNotExist):
            other_person.name.translate('Ayer', 'es')

    def test_update_alone_field(self):
        self.person.name.update('Demain', 'fr', [self.source])

        translations = PersonName.objects.filter(object=self.person)
        self.assertEqual(len(translations), 1)

        language = translations[0].lang
        self.assertEqual('fr', language)

    def test_update_multiple_field(self):
        self.person.name.translate('Tomorrow', 'en')
        self.person.name.translate('Mañana', 'es')
        self.person.name.update('Ayer', 'es', [self.source])

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
        self.person.name.translate('Tomorrow', 'en')
        self.person.name.update('Ayer', 'es', [self.source])

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
            self.person.name.update('Now', 'en', [self.source])
        with reversion.create_revision():
            self.person.name.translate('Maintenant', 'fr')
        with reversion.create_revision():
            self.person.name.translate('Ahora', 'es')
        with reversion.create_revision():
            self.person.name.update('Demain', 'fr', [self.source])
        with reversion.create_revision():
            self.person.name.update('YYYY', 'it', [self.source])
        with reversion.create_revision():
            self.person.name.translate('Hier', 'fr')

        #self.person.name.get_history()
        vers = {'fr': 6, 'es': 5}
        print(self.person.name)

        #print(self.person.get_name(lang='FR'))
        #print(self.person.get_name(lang='ES'))


        fr_trans = PersonName.objects.get(object=self.person, lang='fr')
        fr_version_list = reversion.get_for_object(fr_trans)
        results = [
            json.loads(fr_version.serialized_data)[0]['fields']
            for fr_version in fr_version_list
        ]
        expected_results = [
            {'lang': 'fr', 'object': 1, 'sources': [1], 'value': "Hier"},
            {'lang': 'fr', 'object': 1, 'sources': [], 'value': None},
            {'lang': 'fr', 'object': 1, 'sources': [1], 'value': "Demain"},
            {'lang': 'fr', 'object': 1, 'sources': [1], 'value': "Maintenant"},
            {'lang': 'fr', 'object': 1, 'sources': [], 'value': None},
            {'lang': 'fr', 'object': 1, 'sources': [1], 'value': "Aujourd'hui"},
        ]
        self.maxDiff = None
        self.assertCountEqual(expected_results, results)

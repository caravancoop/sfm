# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-02-13 20:54
from __future__ import unicode_literals

import complex_fields.base_models
from django.db import migrations, models
import django.db.models.deletion
import django_date_extensions.fields
import sfm_pc.models
import sfm_pc.utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('source', '0037_source_metadata'),
        ('person', '0014_remove_extra_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonBiography',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'person biographies',
            },
            bases=(models.Model, complex_fields.base_models.BaseModel, sfm_pc.utils.VersionsMixin, sfm_pc.models.GetComplexSpreadsheetFieldNameMixin),
        ),
        migrations.CreateModel(
            name='PersonBiographyDateOfBirth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', django_date_extensions.fields.ApproximateDateField(blank=True, default=None, null=True)),
                ('accesspoints', models.ManyToManyField(related_name='personbiography_personbiographydateofbirth_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personbiography.PersonBiography')),
                ('sources', models.ManyToManyField(related_name='personbiography_personbiographydateofbirth_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonBiographyDateOfDeath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', django_date_extensions.fields.ApproximateDateField(blank=True, default=None, null=True)),
                ('accesspoints', models.ManyToManyField(related_name='personbiography_personbiographydateofdeath_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personbiography.PersonBiography')),
                ('sources', models.ManyToManyField(related_name='personbiography_personbiographydateofdeath_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonBiographyDeceased',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.BooleanField(default=False)),
                ('accesspoints', models.ManyToManyField(related_name='personbiography_personbiographydeceased_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personbiography.PersonBiography')),
                ('sources', models.ManyToManyField(related_name='personbiography_personbiographydeceased_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonBiographyGender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.TextField(blank=True, default=None, null=True)),
                ('accesspoints', models.ManyToManyField(related_name='personbiography_personbiographygender_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personbiography.PersonBiography')),
                ('sources', models.ManyToManyField(related_name='personbiography_personbiographygender_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonBiographyPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('accesspoints', models.ManyToManyField(related_name='personbiography_personbiographyperson_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personbiography.PersonBiography')),
                ('sources', models.ManyToManyField(related_name='personbiography_personbiographyperson_related', to='source.Source')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

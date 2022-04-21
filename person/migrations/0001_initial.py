# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import complex_fields.base_models
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            bases=(models.Model, complex_fields.base_models.BaseModel),
        ),
        migrations.CreateModel(
            name='PersonAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='person.Person', on_delete=django.db.models.deletion.CASCADE)),
                ('sources', models.ManyToManyField(to='source.Source', related_name='person_personalias_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonDeathDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10, blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='person.Person', on_delete=django.db.models.deletion.CASCADE)),
                ('sources', models.ManyToManyField(to='source.Source', related_name='person_persondeathdate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='person.Person', on_delete=django.db.models.deletion.CASCADE)),
                ('sources', models.ManyToManyField(to='source.Source', related_name='person_personname_related')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import complex_fields.base_models
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Composition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            bases=(models.Model, complex_fields.base_models.BaseModel),
        ),
        migrations.CreateModel(
            name='CompositionChild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='composition.Composition')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionchild_related')),
                ('value', models.ForeignKey(related_name='parent_organization', to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompositionClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='composition.Composition')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionclassification_related')),
                ('value', models.ForeignKey(blank=True, null=True, to='organization.Classification', default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompositionEndDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10, blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='composition.Composition')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionenddate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompositionParent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='composition.Composition')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionparent_related')),
                ('value', models.ForeignKey(related_name='child_organization', to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompositionStartDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10, blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='composition.Composition')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionstartdate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

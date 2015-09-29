# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_auto_20150929_2129'),
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Composition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompositionChild',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionchild_related')),
                ('value', models.ForeignKey(to='organization.Organization', related_name='parent_organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompositionClassification',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionclassification_related')),
                ('value', models.ForeignKey(to='organization.Classification', default=None, blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompositionEndDate',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10, default=None, blank=True, null=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionenddate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompositionParent',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionparent_related')),
                ('value', models.ForeignKey(to='organization.Organization', related_name='child_organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompositionStartDate',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10, default=None, blank=True, null=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='composition_compositionstartdate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

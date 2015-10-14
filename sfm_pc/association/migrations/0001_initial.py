# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20151008_2038'),
        ('source', '0001_initial'),
        ('area', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Association',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AssociationArea',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('object_ref', models.ForeignKey(to='association.Association')),
                ('sources', models.ManyToManyField(related_name='association_associationarea_related', to='source.Source')),
                ('value', models.ForeignKey(to='area.Area')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssociationEndDate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', django_date_extensions.fields.ApproximateDateField(null=True, default=None, max_length=10, blank=True)),
                ('object_ref', models.ForeignKey(to='association.Association')),
                ('sources', models.ManyToManyField(related_name='association_associationenddate_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssociationOrganization',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('object_ref', models.ForeignKey(to='association.Association')),
                ('sources', models.ManyToManyField(related_name='association_associationorganization_related', to='source.Source')),
                ('value', models.ForeignKey(to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssociationStartDate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10)),
                ('object_ref', models.ForeignKey(to='association.Association')),
                ('sources', models.ManyToManyField(related_name='association_associationstartdate_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

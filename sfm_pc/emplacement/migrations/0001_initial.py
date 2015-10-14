# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('site_sfm', '0001_initial'),
        ('source', '0001_initial'),
        ('organization', '0004_auto_20151008_2038'),
    ]

    operations = [
        migrations.CreateModel(
            name='Emplacement',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmplacementEndDate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', django_date_extensions.fields.ApproximateDateField(blank=True, max_length=10, default=None, null=True)),
                ('object_ref', models.ForeignKey(to='emplacement.Emplacement')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='emplacement_emplacementenddate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmplacementOrganization',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(to='emplacement.Emplacement')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='emplacement_emplacementorganization_related')),
                ('value', models.ForeignKey(to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmplacementSite',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(to='emplacement.Emplacement')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='emplacement_emplacementsite_related')),
                ('value', models.ForeignKey(to='site_sfm.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EmplacementStartDate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', django_date_extensions.fields.ApproximateDateField(blank=True, max_length=10, default=None, null=True)),
                ('object_ref', models.ForeignKey(to='emplacement.Emplacement')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='emplacement_emplacementstartdate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='SiteAdminLevel1',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.TextField(default=None, blank=True, null=True)),
                ('object_ref', models.ForeignKey(to='site_sfm.Site')),
                ('sources', models.ManyToManyField(related_name='site_sfm_siteadminlevel1_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteAdminLevel2',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.TextField(default=None, blank=True, null=True)),
                ('object_ref', models.ForeignKey(to='site_sfm.Site')),
                ('sources', models.ManyToManyField(related_name='site_sfm_siteadminlevel2_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteCoordinates',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', django.contrib.gis.db.models.fields.PointField(default=None, blank=True, null=True, srid=4326)),
                ('object_ref', models.ForeignKey(to='site_sfm.Site')),
                ('sources', models.ManyToManyField(related_name='site_sfm_sitecoordinates_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteGeoname',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.TextField(default=None, blank=True, null=True)),
                ('object_ref', models.ForeignKey(to='site_sfm.Site')),
                ('sources', models.ManyToManyField(related_name='site_sfm_sitegeoname_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteGeonameId',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.TextField(default=None, blank=True, null=True)),
                ('object_ref', models.ForeignKey(to='site_sfm.Site')),
                ('sources', models.ManyToManyField(related_name='site_sfm_sitegeonameid_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteName',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.TextField(default=None, blank=True, null=True)),
                ('object_ref', models.ForeignKey(to='site_sfm.Site')),
                ('sources', models.ManyToManyField(related_name='site_sfm_sitename_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

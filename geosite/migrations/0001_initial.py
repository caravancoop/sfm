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
            name='Geosite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='GeositeAdminLevel1',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='geosite.Geosite')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='geosite_geositeadminlevel1_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeositeAdminLevel2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='geosite.Geosite')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='geosite_geositeadminlevel2_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeositeCoordinates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django.contrib.gis.db.models.fields.PointField(srid=4326, blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='geosite.Geosite')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='geosite_geositecoordinates_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeositeGeoname',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='geosite.Geosite')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='geosite_geositegeoname_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeositeGeonameId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='geosite.Geosite')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='geosite_geositegeonameid_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GeositeName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='geosite.Geosite')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='geosite_geositename_related')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

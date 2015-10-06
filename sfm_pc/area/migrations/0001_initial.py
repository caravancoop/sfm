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
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='AreaCode',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(to='area.Area')),
                ('sources', models.ManyToManyField(related_name='area_areacode_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AreaGeometry',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', django.contrib.gis.db.models.fields.PolygonField(null=True, srid=4326, blank=True, default=None)),
                ('object_ref', models.ForeignKey(to='area.Area')),
                ('sources', models.ManyToManyField(related_name='area_areageometry_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AreaGeoName',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.IntegerField(null=True, blank=True, default=None)),
                ('object_ref', models.ForeignKey(to='area.Area')),
                ('sources', models.ManyToManyField(related_name='area_areageoname_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AreaName',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.TextField(null=True, blank=True, default=None)),
                ('object_ref', models.ForeignKey(to='area.Area')),
                ('sources', models.ManyToManyField(related_name='area_areaname_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='areacode',
            name='value',
            field=models.ForeignKey(null=True, blank=True, default=None, to='area.Code'),
        ),
    ]

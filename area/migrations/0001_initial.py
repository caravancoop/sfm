# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import complex_fields.base_models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0023_auto_20180604_1610'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            bases=(models.Model, complex_fields.base_models.BaseModel),
        ),
        migrations.CreateModel(
            name='AreaCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='area.Area', on_delete=django.db.models.deletion.CASCADE)),
                ('sources', models.ManyToManyField(to='source.Source', related_name='area_areacode_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AreaGeometry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django.contrib.gis.db.models.fields.PolygonField(srid=4326, blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='area.Area', on_delete=django.db.models.deletion.CASCADE)),
                ('sources', models.ManyToManyField(to='source.Source', related_name='area_areageometry_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AreaGeoName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.IntegerField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='area.Area', on_delete=django.db.models.deletion.CASCADE)),
                ('sources', models.ManyToManyField(to='source.Source', related_name='area_areageoname_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AreaName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='area.Area', on_delete=django.db.models.deletion.CASCADE)),
                ('sources', models.ManyToManyField(to='source.Source', related_name='area_areaname_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('value', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='areacode',
            name='value',
            field=models.ForeignKey(blank=True, null=True, to='area.Code', default=None, on_delete=django.db.models.deletion.CASCADE),
        ),
    ]

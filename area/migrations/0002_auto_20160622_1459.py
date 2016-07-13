# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0009_auto_20160615_1511'),
        ('area', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaGeonameId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.IntegerField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='area.Area')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='area_areageonameid_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='areageoname',
            name='value',
            field=models.TextField(null=True, default=None, blank=True),
        ),
    ]

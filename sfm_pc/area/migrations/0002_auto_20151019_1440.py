# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('area', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='areacode',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='areageometry',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='areageoname',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='areaname',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
    ]

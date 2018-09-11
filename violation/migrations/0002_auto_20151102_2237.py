# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
        ('violation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='violationlocationdescription',
            name='confidence',
            field=models.CharField(default=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1),
        ),
        migrations.AddField(
            model_name='violationlocationdescription',
            name='lang',
            field=models.CharField(null=True, max_length=5),
        ),
        migrations.AddField(
            model_name='violationlocationdescription',
            name='sources',
            field=models.ManyToManyField(related_name='violation_violationlocationdescription_related', to='source.Source', db_column='uuid'),
        ),
    ]

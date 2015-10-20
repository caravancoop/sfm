# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('composition', '0002_auto_20150930_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='compositionchild',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='compositionclassification',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='compositionenddate',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='compositionparent',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='compositionstartdate',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
    ]

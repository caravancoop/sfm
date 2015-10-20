# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0007_auto_20150924_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalias',
            name='confidence',
            field=models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1),
        ),
        migrations.AddField(
            model_name='persondeathdate',
            name='confidence',
            field=models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1),
        ),
        migrations.AddField(
            model_name='personname',
            name='confidence',
            field=models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1),
        ),
    ]

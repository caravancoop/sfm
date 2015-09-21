# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0004_auto_20150918_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalias',
            name='lang',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='persondeathdate',
            name='lang',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='personname',
            name='lang',
            field=models.CharField(max_length=5, null=True),
        ),
    ]

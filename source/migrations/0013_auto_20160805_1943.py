# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-05 19:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0012_auto_20160805_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='title',
            field=models.TextField(),
        ),
    ]

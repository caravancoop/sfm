# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-23 16:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_auto_20160617_1413'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizationalias',
            name='confidence',
        ),
        migrations.RemoveField(
            model_name='organizationalias',
            name='lang',
        ),
        migrations.RemoveField(
            model_name='organizationalias',
            name='sources',
        ),
    ]

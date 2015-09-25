# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0006_auto_20150922_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persondeathdate',
            name='value',
            field=django_date_extensions.fields.ApproximateDateField(blank=True, max_length=10, null=True, default=None),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_auto_20150922_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationdissolutiondate',
            name='value',
            field=django_date_extensions.fields.ApproximateDateField(blank=True, null=True, max_length=10, default=None),
        ),
    ]

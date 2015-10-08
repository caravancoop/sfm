# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_auto_20150929_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationfoundingdate',
            name='value',
            field=django_date_extensions.fields.ApproximateDateField(blank=True, null=True, default=None, max_length=10),
        ),
    ]

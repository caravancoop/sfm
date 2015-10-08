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
            field=django_date_extensions.fields.ApproximateDateField(blank=True, default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='organizationrealdissolution',
            name='value',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='organizationrealfounding',
            name='value',
            field=models.BooleanField(default=False),
        ),
    ]

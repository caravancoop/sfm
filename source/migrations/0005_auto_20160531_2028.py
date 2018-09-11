# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0004_auto_20160513_2044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='country',
        ),
        migrations.AddField(
            model_name='publication',
            name='country_iso',
            field=models.CharField(max_length=2, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='publication',
            name='country_name',
            field=models.CharField(max_length=2, default=''),
            preserve_default=False,
        ),
    ]

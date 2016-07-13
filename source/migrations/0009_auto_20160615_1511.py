# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0008_auto_20160601_1714'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='country_name',
            new_name='country',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='country_iso',
        ),
    ]

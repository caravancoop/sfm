# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0003_auto_20160513_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='country',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='publication',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]

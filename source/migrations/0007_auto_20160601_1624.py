# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0006_auto_20160531_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='country_name',
            field=models.CharField(max_length=255),
        ),
    ]

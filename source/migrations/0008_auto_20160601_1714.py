# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0007_auto_20160601_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='publication_id',
            field=models.UUIDField(),
        ),
    ]

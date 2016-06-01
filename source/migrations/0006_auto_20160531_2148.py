# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0005_auto_20160531_2028'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='id',
        ),
        migrations.AddField(
            model_name='publication',
            name='uuid',
            field=models.UUIDField(primary_key=True, serialize=False, default='0ebee800-570f-4861-8827-50adfc8fd4c8'),
            preserve_default=False,
        ),
    ]

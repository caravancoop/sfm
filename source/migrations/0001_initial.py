# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('source', models.TextField()),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1)),
            ],
        ),
    ]

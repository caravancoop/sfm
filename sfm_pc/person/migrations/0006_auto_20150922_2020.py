# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0005_auto_20150921_1748'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='personalias',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='persondeathdate',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='personname',
            unique_together=set([]),
        ),
    ]

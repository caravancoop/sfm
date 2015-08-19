# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0004_auto_20150817_1357'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='personalias',
            unique_together=set([('person', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='personname',
            unique_together=set([('person', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='personnotes',
            unique_together=set([('person', 'lang')]),
        ),
    ]

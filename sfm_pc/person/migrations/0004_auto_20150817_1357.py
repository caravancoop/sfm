# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0003_auto_20150814_1757'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='alias',
        ),
        migrations.RemoveField(
            model_name='person',
            name='name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='notes',
        ),
        migrations.AddField(
            model_name='personalias',
            name='person',
            field=models.ForeignKey(to='person.Person', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='personname',
            name='person',
            field=models.ForeignKey(to='person.Person', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='personnotes',
            name='person',
            field=models.ForeignKey(to='person.Person', default=1),
            preserve_default=False,
        ),
    ]

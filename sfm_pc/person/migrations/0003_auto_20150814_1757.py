# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0002_remove_person_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='personalias',
            name='person',
        ),
        migrations.RemoveField(
            model_name='personname',
            name='person',
        ),
        migrations.RemoveField(
            model_name='personnotes',
            name='person',
        ),
        migrations.AddField(
            model_name='person',
            name='alias',
            field=models.ForeignKey(to='person.PersonAlias', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='name',
            field=models.ForeignKey(to='person.PersonName', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='notes',
            field=models.ForeignKey(to='person.PersonNotes', default=1),
            preserve_default=False,
        ),
    ]

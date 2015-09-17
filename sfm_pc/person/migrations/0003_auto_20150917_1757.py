# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0002_auto_20150915_2128'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personalias',
            old_name='object',
            new_name='object_ref',
        ),
        migrations.RenameField(
            model_name='personname',
            old_name='object',
            new_name='object_ref',
        ),
        migrations.RenameField(
            model_name='personnotes',
            old_name='object',
            new_name='object_ref',
        ),
        migrations.AlterField(
            model_name='personalias',
            name='lang',
            field=models.CharField(max_length=5, default='en'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='personname',
            name='lang',
            field=models.CharField(max_length=5, default='en'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='personnotes',
            name='lang',
            field=models.CharField(max_length=5, default='en'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='personalias',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='personname',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='personnotes',
            unique_together=set([('object_ref', 'lang')]),
        ),
    ]

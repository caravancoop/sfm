# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('composition', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compositionchild',
            name='object_ref',
            field=models.ForeignKey(to='composition.Composition'),
        ),
        migrations.AlterField(
            model_name='compositionclassification',
            name='object_ref',
            field=models.ForeignKey(to='composition.Composition'),
        ),
        migrations.AlterField(
            model_name='compositionenddate',
            name='object_ref',
            field=models.ForeignKey(to='composition.Composition'),
        ),
        migrations.AlterField(
            model_name='compositionparent',
            name='object_ref',
            field=models.ForeignKey(to='composition.Composition'),
        ),
        migrations.AlterField(
            model_name='compositionstartdate',
            name='object_ref',
            field=models.ForeignKey(to='composition.Composition'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0003_auto_20150922_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipdate',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershipendcontext',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershiporganization',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershipperson',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershiprank',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershiprealend',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershiprealstart',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershiprole',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershipstartcontext',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
        migrations.AddField(
            model_name='membershiptitle',
            name='confidence',
            field=models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1),
        ),
    ]

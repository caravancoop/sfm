# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0005_auto_20151020_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershiporganizationmember',
            name='value',
            field=models.ForeignKey(to='organization.Organization', null=True, blank=True, default=None),
        ),
        migrations.AlterField(
            model_name='membershippersonmember',
            name='value',
            field=models.ForeignKey(to='person.Person', null=True, blank=True, default=None),
        ),
    ]

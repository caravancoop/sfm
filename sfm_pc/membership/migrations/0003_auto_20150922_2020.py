# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0002_auto_20150922_2002'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='membershipdate',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershipendcontext',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiporganization',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershipperson',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiprank',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiprealend',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiprealstart',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiprole',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershipstartcontext',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiptitle',
            unique_together=set([]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='organizationalias',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationclassification',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationdissolutiondate',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationfoundingdate',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationname',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationrealdissolution',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationrealfounding',
            unique_together=set([]),
        ),
    ]

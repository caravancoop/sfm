# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizationdissolutiondate',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='organizationdissolutiondate',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='organizationrealdissolution',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='organizationrealdissolution',
            name='sources',
        ),
        migrations.DeleteModel(
            name='OrganizationDissolutionDate',
        ),
        migrations.DeleteModel(
            name='OrganizationRealDissolution',
        ),
    ]

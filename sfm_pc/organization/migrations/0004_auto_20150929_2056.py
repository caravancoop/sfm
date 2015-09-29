# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_organizationcomposition_organizationcompositionchild_organizationcompositionclassification_organizat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationdissolutiondate',
            name='value',
            field=django_date_extensions.fields.ApproximateDateField(default=None, null=True, blank=True, max_length=10),
        ),
    ]

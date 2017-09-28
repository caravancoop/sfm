# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0007_auto_20160601_1624'),
    ]

    operations = [
            migrations.RunSQL('''
                ALTER TABLE source_source 
                ALTER COLUMN publication_id 
                TYPE UUID USING publication_id::VARCHAR::UUID
            '''),
    ]

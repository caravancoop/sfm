# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geosite', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("ALTER TABLE geosite_geositegeonameid ALTER COLUMN value TYPE integer USING value::integer")
    ]

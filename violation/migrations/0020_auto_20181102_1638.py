# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-02 16:38
from __future__ import unicode_literals
from collections import namedtuple
import os

from django.db import migrations, models, connection
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('violation', '0019_auto_20181018_2151'),
    ]

    state_operations = [
        migrations.AlterField(
            model_name='violationadminlevel1',
            name='value',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='location.Location'),
        ),
        migrations.AlterField(
            model_name='violationadminlevel2',
            name='value',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='location.Location'),
        ),
    ]

    database_operations = [
        migrations.RunSQL('DROP MATERIALIZED VIEW IF EXISTS violation'),
        migrations.RunSQL('DROP MATERIALIZED VIEW IF EXISTS violation_all_export'),
        migrations.RunSQL('DROP MATERIALIZED VIEW IF EXISTS violation_sources'),
        migrations.RunSQL('ALTER TABLE violation_violationadminlevel1 RENAME COLUMN value TO value_id'),
        migrations.RunSQL('ALTER TABLE violation_violationadminlevel1 ALTER COLUMN value_id TYPE bigint USING NULL'),
        migrations.RunSQL('ALTER TABLE violation_violationadminlevel2 RENAME COLUMN value TO value_id'),
        migrations.RunSQL('ALTER TABLE violation_violationadminlevel2 ALTER COLUMN value_id TYPE bigint USING NULL'),
        migrations.RunSQL('TRUNCATE violation_violationadminlevel1 CASCADE'),
        migrations.RunSQL('TRUNCATE violation_violationadminlevel2 CASCADE'),
        migrations.RunSQL('''
            ALTER TABLE violation_violationadminlevel1 ADD CONSTRAINT
            violation_violationadminlevel1_location FOREIGN KEY (value_id) REFERENCES location_location (id)
            DEFERRABLE INITIALLY DEFERRED
        '''),
        migrations.RunSQL('''
            ALTER TABLE violation_violationadminlevel2 ADD CONSTRAINT
            violation_violationadminlevel2_location FOREIGN KEY (value_id) REFERENCES location_location (id)
            DEFERRABLE INITIALLY DEFERRED
        '''),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations,
                                            database_operations=database_operations)
    ]
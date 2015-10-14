# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Violation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationAdminLevel1',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationAdminLevel2',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationDescription',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationEndDate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', django_date_extensions.fields.ApproximateDateField(null=True, default=None, blank=True, max_length=10)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationGeoname',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationGeonameId',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationLocation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', django.contrib.gis.db.models.fields.PointField(null=True, default=None, blank=True, srid=4326)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationLocationDescription',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationPerpetrator',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationPerpetratorOrganization',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationSource',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('source', models.ForeignKey(to='source.Source')),
                ('violation', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationStartDate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('value', django_date_extensions.fields.ApproximateDateField(null=True, default=None, blank=True, max_length=10)),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
            ],
        ),
        migrations.CreateModel(
            name='ViolationType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('object_ref', models.ForeignKey(to='violation.Violation')),
                ('value', models.ForeignKey(null=True, blank=True, default=None, to='violation.Type')),
            ],
        ),
    ]

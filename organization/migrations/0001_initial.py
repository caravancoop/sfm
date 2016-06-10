# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import complex_fields.base_models
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            bases=(models.Model, complex_fields.base_models.BaseModel),
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.ForeignKey(blank=True, null=True, to='organization.Alias', default=None)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationalias_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationclassification_related')),
                ('value', models.ForeignKey(blank=True, null=True, to='organization.Classification', default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationDissolutionDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10, blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationdissolutiondate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationFoundingDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10, blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationfoundingdate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationname_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationRealDissolution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.BooleanField(default=False)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationrealdissolution_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationRealFounding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.BooleanField(default=False)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationrealfounding_related')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

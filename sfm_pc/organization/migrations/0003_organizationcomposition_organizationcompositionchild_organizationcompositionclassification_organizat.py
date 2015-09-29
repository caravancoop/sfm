# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
        ('organization', '0002_auto_20150922_2020'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationComposition',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationCompositionChild',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationcompositionchild_related')),
                ('value', models.ForeignKey(related_name='parent_organization', to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationCompositionClassification',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationcompositionclassification_related')),
                ('value', models.ForeignKey(null=True, default=None, blank=True, to='organization.Classification')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationCompositionEndDate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', django_date_extensions.fields.ApproximateDateField(null=True, blank=True, default=None, max_length=10)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationcompositionenddate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationCompositionParent',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationcompositionparent_related')),
                ('value', models.ForeignKey(related_name='child_organization', to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationCompositionStartDate',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', django_date_extensions.fields.ApproximateDateField(null=True, blank=True, default=None, max_length=10)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='organization_organizationcompositionstartdate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

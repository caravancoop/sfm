# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationAlias',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(related_name='organization_organizationalias_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationClassification',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(related_name='organization_organizationclassification_related', to='source.Source')),
                ('value', models.ForeignKey(blank=True, null=True, to='organization.Classification', default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationDissolutionDate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.DateField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(related_name='organization_organizationdissolutiondate_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationFoundingDate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.DateField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(related_name='organization_organizationfoundingdate_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationName',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(related_name='organization_organizationname_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationRealDissolution',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.BooleanField(default=None)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(related_name='organization_organizationrealdissolution_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationRealFounding',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.BooleanField(default=None)),
                ('object_ref', models.ForeignKey(to='organization.Organization')),
                ('sources', models.ManyToManyField(related_name='organization_organizationrealfounding_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='organizationrealfounding',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationrealdissolution',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationname',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationfoundingdate',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationdissolutiondate',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationclassification',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='organizationalias',
            unique_together=set([('object_ref', 'lang')]),
        ),
    ]

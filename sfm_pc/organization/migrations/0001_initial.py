# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParentOrganization',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(related_name='child_org', to='organization.Organization')),
                ('sources', models.ManyToManyField(related_name='organization_parentorganization_related', to='source.Source')),
                ('value', models.ForeignKey(default=None, related_name='parent_org', to='organization.Organization', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='parentorganization',
            unique_together=set([('object_ref', 'lang')]),
        ),
    ]

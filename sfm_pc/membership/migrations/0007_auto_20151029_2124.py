# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0002_remove_source_confidence'),
        ('membership', '0006_auto_20151021_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipFirstCitedDate',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(related_name='membership_membershipfirstciteddate_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipLastCitedDate',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(related_name='membership_membershiplastciteddate_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='membershipdate',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='membershipdate',
            name='sources',
        ),
        migrations.DeleteModel(
            name='MembershipDate',
        ),
    ]

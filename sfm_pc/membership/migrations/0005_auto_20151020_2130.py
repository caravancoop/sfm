# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0008_auto_20151016_1937'),
        ('organization', '0005_auto_20151019_1440'),
        ('source', '0002_remove_source_confidence'),
        ('membership', '0004_auto_20151019_1440'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipOrganizationMember',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiporganizationmember_related')),
                ('value', models.ForeignKey(to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonMember',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershippersonmember_related')),
                ('value', models.ForeignKey(to='person.Person')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='membershipperson',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='membershipperson',
            name='sources',
        ),
        migrations.RemoveField(
            model_name='membershipperson',
            name='value',
        ),
        migrations.DeleteModel(
            name='MembershipPerson',
        ),
    ]

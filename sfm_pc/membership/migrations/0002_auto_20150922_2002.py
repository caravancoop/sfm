# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
        ('membership', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipEndContext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(related_name='membership_membershipendcontext_related', to='source.Source')),
                ('value', models.ForeignKey(to='membership.Context')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipRealEnd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.BooleanField(default=None)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(related_name='membership_membershiprealend_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipRealStart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('value', models.BooleanField(default=None)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(related_name='membership_membershiprealstart_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipStartContext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(related_name='membership_membershipstartcontext_related', to='source.Source')),
                ('value', models.ForeignKey(to='membership.Context')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='membershipdate',
            name='lang',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='membershipdate',
            name='sources',
            field=models.ManyToManyField(related_name='membership_membershipdate_related', to='source.Source'),
        ),
        migrations.AlterUniqueTogether(
            name='membershipdate',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='membershipstartcontext',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiprealstart',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='membershiprealend',
            unique_together=set([('object_ref', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='membershipendcontext',
            unique_together=set([('object_ref', 'lang')]),
        ),
    ]

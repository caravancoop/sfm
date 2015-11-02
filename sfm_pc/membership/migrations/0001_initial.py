# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import complex_fields.base_models
import django_date_extensions.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
        ('person', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            bases=(models.Model, complex_fields.base_models.BaseModel),
        ),
        migrations.CreateModel(
            name='MembershipEndContext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershipendcontext_related')),
                ('value', models.ForeignKey(to='membership.Context')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipFirstCitedDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershipfirstciteddate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipLastCitedDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiplastciteddate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipOrganization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiporganization_related')),
                ('value', models.ForeignKey(to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipOrganizationMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiporganizationmember_related')),
                ('value', models.ForeignKey(blank=True, null=True, to='organization.Organization', default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershippersonmember_related')),
                ('value', models.ForeignKey(blank=True, null=True, to='person.Person', default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipRank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiprank_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipRealEnd',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.BooleanField(default=None)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiprealend_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipRealStart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.BooleanField(default=None)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiprealstart_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiprole_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipStartContext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershipstartcontext_related')),
                ('value', models.ForeignKey(to='membership.Context')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(default=1, max_length=1, choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')])),
                ('value', models.TextField(blank=True, null=True, default=None)),
                ('object_ref', models.ForeignKey(to='membership.Membership')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='membership_membershiptitle_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('value', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='membershiprole',
            name='value',
            field=models.ForeignKey(blank=True, null=True, to='membership.Role', default=None),
        ),
        migrations.AddField(
            model_name='membershiprank',
            name='value',
            field=models.ForeignKey(blank=True, null=True, to='membership.Rank', default=None),
        ),
    ]

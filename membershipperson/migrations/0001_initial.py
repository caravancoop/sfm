# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_date_extensions.fields
import complex_fields.base_models


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
        ('organization', '0001_initial'),
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MembershipPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
            ],
            bases=(models.Model, complex_fields.base_models.BaseModel),
        ),
        migrations.CreateModel(
            name='MembershipPersonEndContext',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonendcontext_related', to='source.Source')),
                ('value', models.ForeignKey(to='membershipperson.Context')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonFirstCitedDate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonfirstciteddate_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonLastCitedDate',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('value', django_date_extensions.fields.ApproximateDateField(max_length=10)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonlastciteddate_related', to='source.Source')),
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
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonmember_related', to='source.Source')),
                ('value', models.ForeignKey(blank=True, default=None, to='person.Person', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonOrganization',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonorganization_related', to='source.Source')),
                ('value', models.ForeignKey(to='organization.Organization')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonRank',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonrank_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonRealEnd',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('value', models.BooleanField(default=None)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonrealend_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonRealStart',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('value', models.BooleanField(default=None)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonrealstart_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonRole',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonrole_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonStartContext',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersonstartcontext_related', to='source.Source')),
                ('value', models.ForeignKey(to='membershipperson.Context')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MembershipPersonTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(null=True, max_length=5)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], max_length=1, default=1)),
                ('value', models.TextField(null=True, blank=True, default=None)),
                ('object_ref', models.ForeignKey(to='membershipperson.MembershipPerson')),
                ('sources', models.ManyToManyField(related_name='membershipperson_membershippersontitle_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='membershippersonrole',
            name='value',
            field=models.ForeignKey(blank=True, default=None, to='membershipperson.Role', null=True),
        ),
        migrations.AddField(
            model_name='membershippersonrank',
            name='value',
            field=models.ForeignKey(blank=True, default=None, to='membershipperson.Rank', null=True),
        ),
    ]

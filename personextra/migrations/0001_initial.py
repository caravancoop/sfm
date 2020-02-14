# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-02-13 20:54
from __future__ import unicode_literals

import complex_fields.base_models
from django.db import migrations, models
import django.db.models.deletion
import sfm_pc.models
import sfm_pc.utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('person', '0014_remove_extra_fields'),
        ('source', '0037_source_metadata'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonExtra',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            bases=(models.Model, complex_fields.base_models.BaseModel, sfm_pc.utils.VersionsMixin, sfm_pc.models.GetComplexSpreadsheetFieldNameMixin),
        ),
        migrations.CreateModel(
            name='PersonExtraAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.TextField(blank=True, default=None, null=True)),
                ('accesspoints', models.ManyToManyField(related_name='personextra_personextraaccount_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personextra.PersonExtra')),
                ('sources', models.ManyToManyField(related_name='personextra_personextraaccount_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonExtraAccountType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.TextField(blank=True, default=None, null=True)),
                ('accesspoints', models.ManyToManyField(related_name='personextra_personextraaccounttype_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personextra.PersonExtra')),
                ('sources', models.ManyToManyField(related_name='personextra_personextraaccounttype_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonExtraExternalLinkDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.TextField(blank=True, default=None, null=True)),
                ('accesspoints', models.ManyToManyField(related_name='personextra_personextraexternallinkdescription_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personextra.PersonExtra')),
                ('sources', models.ManyToManyField(related_name='personextra_personextraexternallinkdescription_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonExtraMediaDescription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.TextField(blank=True, default=None, null=True)),
                ('accesspoints', models.ManyToManyField(related_name='personextra_personextramediadescription_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personextra.PersonExtra')),
                ('sources', models.ManyToManyField(related_name='personextra_personextramediadescription_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonExtraNotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('value', models.TextField(blank=True, default=None, null=True)),
                ('accesspoints', models.ManyToManyField(related_name='personextra_personextranotes_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personextra.PersonExtra')),
                ('sources', models.ManyToManyField(related_name='personextra_personextranotes_related', to='source.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonExtraPerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=5, null=True)),
                ('confidence', models.CharField(choices=[('1', 'Low'), ('2', 'Medium'), ('3', 'High')], default=1, max_length=1)),
                ('accesspoints', models.ManyToManyField(related_name='personextra_personextraperson_related', to='source.AccessPoint')),
                ('object_ref', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personextra.PersonExtra')),
                ('sources', models.ManyToManyField(related_name='personextra_personextraperson_related', to='source.Source')),
                ('value', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

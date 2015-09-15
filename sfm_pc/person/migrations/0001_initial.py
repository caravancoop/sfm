# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='PersonAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object', models.ForeignKey(to='person.Person')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='person_personalias_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object', models.ForeignKey(to='person.Person')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='person_personname_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonNotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('lang', models.CharField(null=True, max_length=5)),
                ('value', models.TextField(null=True, default=None, blank=True)),
                ('object', models.ForeignKey(to='person.Person')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='person_personnotes_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='personnotes',
            unique_together=set([('object', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='personname',
            unique_together=set([('object', 'lang')]),
        ),
        migrations.AlterUniqueTogether(
            name='personalias',
            unique_together=set([('object', 'lang')]),
        ),
    ]

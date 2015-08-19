# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('notes', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PersonAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5)),
                ('value', models.TextField()),
                ('person', models.ForeignKey(to='person.Person')),
            ],
        ),
        migrations.CreateModel(
            name='PersonName',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5)),
                ('value', models.TextField()),
                ('person', models.ForeignKey(to='person.Person')),
            ],
        ),
        migrations.CreateModel(
            name='PersonNotes',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lang', models.CharField(max_length=5)),
                ('value', models.TextField()),
                ('person', models.ForeignKey(to='person.Person')),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
        ('person', '0003_auto_20150917_1757'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonDeathDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('lang', models.CharField(max_length=5)),
                ('value', models.DateField(null=True, default=None, blank=True)),
                ('object_ref', models.ForeignKey(to='person.Person')),
                ('sources', models.ManyToManyField(to='source.Source', related_name='person_persondeathdate_related')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='personnotes',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='personnotes',
            name='object_ref',
        ),
        migrations.RemoveField(
            model_name='personnotes',
            name='sources',
        ),
        migrations.DeleteModel(
            name='PersonNotes',
        ),
        migrations.AlterUniqueTogether(
            name='persondeathdate',
            unique_together=set([('object_ref', 'lang')]),
        ),
    ]

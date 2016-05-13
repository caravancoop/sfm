# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0002_auto_20160513_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('title', models.TextField()),
                ('country', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='source',
            name='publication_country',
        ),
        migrations.RemoveField(
            model_name='source',
            name='publication_name',
        ),
        migrations.AddField(
            model_name='source',
            name='publication',
            field=models.ForeignKey(to='source.Publication', null=True),
        ),
    ]

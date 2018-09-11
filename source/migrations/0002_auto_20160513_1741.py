# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='source',
            old_name='source',
            new_name='title',
        ),
        migrations.AddField(
            model_name='source',
            name='archive_url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='source',
            name='publication_country',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='source',
            name='publication_name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='source',
            name='published_on',
            field=models.DateField(default=datetime.datetime(2016, 5, 13, 17, 41, 40, 895434, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='source',
            name='source_url',
            field=models.URLField(default=''),
            preserve_default=False,
        ),
    ]

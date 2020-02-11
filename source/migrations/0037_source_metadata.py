# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2020-02-11 20:30
from __future__ import unicode_literals

from django.db import migrations
import source.fields


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0036_auto_20190131_2040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accesspoint',
            name='page_number',
        ),
        migrations.AddField(
            model_name='accesspoint',
            name='trigger',
            field=source.fields.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='accesspoint',
            name='type',
            field=source.fields.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='source',
            name='author',
            field=source.fields.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='source',
            name='created_on',
            field=source.fields.ApproximateDateField(null=True, verbose_name='creation date'),
        ),
        migrations.AddField(
            model_name='source',
            name='type',
            field=source.fields.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name='source',
            name='uploaded_on',
            field=source.fields.ApproximateDateField(null=True, verbose_name='upload date'),
        ),
        migrations.AlterField(
            model_name='accesspoint',
            name='accessed_on',
            field=source.fields.DateField(null=True, verbose_name='access date'),
        ),
        migrations.AlterField(
            model_name='accesspoint',
            name='archive_url',
            field=source.fields.URLField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='publication',
            field=source.fields.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='publication_country',
            field=source.fields.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='published_on',
            field=source.fields.ApproximateDateField(verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='source',
            name='source_url',
            field=source.fields.URLField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='title',
            field=source.fields.TextField(),
        ),
    ]

# Generated by Django 3.0 on 2022-04-11 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('composition', '0013_auto_20190208_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compositionrealstart',
            name='value',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
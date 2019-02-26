
from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.RunSQL('drop table if exists socialaccount_socialaccount cascade;'),
        migrations.RunSQL('drop table if exists socialaccount_socialapp cascade;'),
        migrations.RunSQL('drop table if exists socialaccount_socialapp_sites cascade;'),
        migrations.RunSQL('drop table if exists socialaccount_socialtoken cascade;'),
        migrations.RunSQL('drop table if exists account_emailaddress cascade;'),
        migrations.RunSQL('drop table if exists account_confirmation cascade;'),
    ]

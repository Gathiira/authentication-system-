# Generated by Django 3.2.3 on 2021-06-01 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20210515_1753'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='username',
            new_name='phone_number',
        ),
    ]

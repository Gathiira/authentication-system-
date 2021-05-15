# Generated by Django 3.2 on 2021-05-15 04:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CodeVerification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user', models.CharField(max_length=500)),
                ('send_to', models.CharField(max_length=500)),
                ('code', models.IntegerField(blank=True, null=True)),
                ('creation_date', models.DateTimeField()),
                ('expiry_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('REVOKED', 'REVOKED'), ('PENDING', 'PENDING')], max_length=20)),
                ('module', models.CharField(max_length=255)),
            ],
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-09 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yt_auth', '0005_credentials_date_acquired'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credentials',
            name='date_acquired',
        ),
    ]
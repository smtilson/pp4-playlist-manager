# Generated by Django 4.2.13 on 2024-06-09 14:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('yt_auth', '0004_credentials_account_credentials_client_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='credentials',
            name='date_acquired',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

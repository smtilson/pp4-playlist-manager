# Generated by Django 4.2.13 on 2024-06-13 08:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0017_delete_guestprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='is_guest',
        ),
    ]

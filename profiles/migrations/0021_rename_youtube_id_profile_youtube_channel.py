# Generated by Django 4.2.13 on 2024-06-20 06:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0020_rename_youtube_url_profile_youtube_handle'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='youtube_id',
            new_name='youtube_channel',
        ),
    ]

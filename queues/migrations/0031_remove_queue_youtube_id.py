# Generated by Django 4.2.13 on 2024-06-15 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0030_alter_entry_options_rename_position_entry__position_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='queue',
            name='youtube_id',
        ),
    ]
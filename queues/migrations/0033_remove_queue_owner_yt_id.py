# Generated by Django 4.2.13 on 2024-06-18 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0032_entry_to_delete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='queue',
            name='owner_yt_id',
        ),
    ]
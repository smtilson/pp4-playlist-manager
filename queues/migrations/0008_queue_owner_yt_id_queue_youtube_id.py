# Generated by Django 4.2.13 on 2024-06-11 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0007_alter_entry_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='owner_yt_id',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='queue',
            name='youtube_id',
            field=models.CharField(default='', max_length=100),
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-11 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0003_alter_entry_options_entry_number_entry_queue_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='length',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
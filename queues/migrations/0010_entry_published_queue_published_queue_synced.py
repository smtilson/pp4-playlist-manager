# Generated by Django 4.2.13 on 2024-06-12 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0009_alter_entry_queue'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='published',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='queue',
            name='published',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='queue',
            name='synced',
            field=models.BooleanField(default=False),
        ),
    ]
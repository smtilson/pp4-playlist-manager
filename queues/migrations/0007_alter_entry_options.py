# Generated by Django 4.2.13 on 2024-06-11 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0006_entry_duration_entry_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'ordering': ['-number']},
        ),
    ]
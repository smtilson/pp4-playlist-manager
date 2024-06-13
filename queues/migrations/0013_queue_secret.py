# Generated by Django 4.2.13 on 2024-06-12 15:58

from django.db import migrations, models
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0012_alter_entry_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='queue',
            name='secret',
            field=models.CharField(default=utils.get_secret, max_length=20),
        ),
    ]

# Generated by Django 4.2.13 on 2024-06-13 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0022_rename_queue_entry_p_queue'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='kind',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='entry',
            name='resource_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='queue',
            name='kind',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='queue',
            name='resource_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]
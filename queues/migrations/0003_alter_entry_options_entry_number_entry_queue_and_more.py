# Generated by Django 4.2.13 on 2024-06-11 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('queues', '0002_queue_collaborators_queue_date_created_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'ordering': ['number']},
        ),
        migrations.AddField(
            model_name='entry',
            name='number',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='entry',
            name='queue',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='queues.queue'),
        ),
        migrations.AddField(
            model_name='entry',
            name='title',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='entry',
            name='video_id',
            field=models.CharField(default='', max_length=100),
        ),
    ]

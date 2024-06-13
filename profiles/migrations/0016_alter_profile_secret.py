# Generated by Django 4.2.13 on 2024-06-12 15:58

from django.db import migrations, models
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_profile_secret'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='secret',
            field=models.CharField(default=utils.get_secret, max_length=20, unique=True),
        ),
    ]
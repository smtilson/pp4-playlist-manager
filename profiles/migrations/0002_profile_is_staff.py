# Generated by Django 4.2.13 on 2024-06-06 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_staff',
            field=models.BooleanField(default=True),
        ),
    ]

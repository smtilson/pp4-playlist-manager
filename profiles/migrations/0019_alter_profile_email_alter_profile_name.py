# Generated by Django 4.2.13 on 2024-06-13 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_remove_profile_is_guest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='email',
            field=models.EmailField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]

# Generated by Django 2.2.24 on 2021-07-20 22:00
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('adserver', '0055_adding_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='view_time',
            field=models.PositiveIntegerField(default=None, null=True, verbose_name='Seconds that the ad was in view'),
        ),
    ]

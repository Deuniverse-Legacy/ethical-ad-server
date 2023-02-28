# Generated by Django 3.2.18 on 2023-02-24 22:57
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('adserver', '0077_publisher_paid_impressions'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='sampled_ctr',
            field=models.FloatField(default=0.0, help_text='A periodically calculated CTR for this ad.'),
        ),
        migrations.AddField(
            model_name='historicaladvertisement',
            name='sampled_ctr',
            field=models.FloatField(default=0.0, help_text='A periodically calculated CTR for this ad.'),
        ),
    ]

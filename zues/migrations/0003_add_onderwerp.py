# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zues', '0002_change_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='actuelepolitiekemotie',
            name='onderwerp',
            field=models.CharField(null=True, max_length=250, blank=True),
        ),
        migrations.AddField(
            model_name='amendement',
            name='onderwerp',
            field=models.CharField(null=True, max_length=250, blank=True),
        ),
        migrations.AddField(
            model_name='hrwijziging',
            name='onderwerp',
            field=models.CharField(null=True, max_length=250, blank=True),
        ),
        migrations.AddField(
            model_name='organimo',
            name='onderwerp',
            field=models.CharField(null=True, max_length=250, blank=True),
        ),
        migrations.AddField(
            model_name='politiekemotie',
            name='onderwerp',
            field=models.CharField(null=True, max_length=250, blank=True),
        ),
        migrations.AddField(
            model_name='resolutie',
            name='onderwerp',
            field=models.CharField(null=True, max_length=250, blank=True),
        ),
    ]

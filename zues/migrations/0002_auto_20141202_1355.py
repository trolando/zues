# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zues', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actuelepolitiekemotie',
            name='boeknummer',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='amendement',
            name='boeknummer',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='amendement',
            name='type',
            field=models.CharField(max_length=2, choices=[(b'W', b'Vervangen'), (b'S', b'Schrappen'), (b'T', b'Toevoegen')]),
        ),
        migrations.AlterField(
            model_name='hrwijziging',
            name='boeknummer',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='hrwijziging',
            name='type',
            field=models.CharField(max_length=2, choices=[(b'W', b'Vervangen'), (b'S', b'Schrappen'), (b'T', b'Toevoegen')]),
        ),
        migrations.AlterField(
            model_name='organimo',
            name='boeknummer',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='politiekemotie',
            name='boeknummer',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='resolutie',
            name='boeknummer',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='resolutie',
            name='type',
            field=models.CharField(max_length=2, choices=[(b'W', b'Vervangen'), (b'S', b'Schrappen'), (b'T', b'Toevoegen')]),
        ),
    ]

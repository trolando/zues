# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import zues.utils


class Migration(migrations.Migration):

    dependencies = [
        ('zues', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='actuelepolitiekemotie',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='amendement',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='categorie',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='hrwijziging',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='login',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='organimo',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='politiekemotie',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='resolutie',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='settings',
            managers=[
                ('objects', zues.utils.CurrentSiteManager()),
            ],
        ),
    ]

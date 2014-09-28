# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appolo', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activiteit',
            options={'verbose_name_plural': 'activiteiten'},
        ),
        migrations.AlterModelOptions(
            name='dag',
            options={'verbose_name_plural': 'dagen'},
        ),
        migrations.AlterModelOptions(
            name='hashtag',
            options={'verbose_name_plural': 'hashtags'},
        ),
        migrations.AlterModelOptions(
            name='locatie',
            options={'verbose_name_plural': 'locaties'},
        ),
        migrations.AlterModelOptions(
            name='nieuwsitem',
            options={'verbose_name_plural': 'nieuwsitems'},
        ),
    ]

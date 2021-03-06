# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActuelePolitiekeMotie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('titel', models.CharField(max_length=250)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Ingediend'), (2, 'Verwijderd'), (3, 'Repareren'), (4, 'Geaccepteerd'), (5, 'Publiek')])),
                ('admin_opmerkingen', models.TextField(blank=True, help_text='Opmerkingen van de beheerder')),
                ('boeknummer', models.IntegerField(blank=True, default=0)),
                ('indienmoment', models.DateField(auto_now_add=True)),
                ('laatsteupdate', models.DateField(auto_now=True)),
                ('secret', models.CharField(max_length=250)),
                ('indieners', models.TextField()),
                ('woordvoerder', models.CharField(max_length=250)),
                ('toelichting', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')),
                ('constateringen', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')),
                ('overwegingen', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')),
                ('uitspraken', models.TextField(help_text='Gebruik een dubbele enter voor de volgende bullet')),
            ],
            options={
                'ordering': ('-laatsteupdate',),
                'verbose_name_plural': 'actuele politieke moties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Amendement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('titel', models.CharField(max_length=250)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Ingediend'), (2, 'Verwijderd'), (3, 'Repareren'), (4, 'Geaccepteerd'), (5, 'Publiek')])),
                ('admin_opmerkingen', models.TextField(blank=True, help_text='Opmerkingen van de beheerder')),
                ('boeknummer', models.IntegerField(blank=True, default=0)),
                ('indienmoment', models.DateField(auto_now_add=True)),
                ('laatsteupdate', models.DateField(auto_now=True)),
                ('secret', models.CharField(max_length=250)),
                ('indieners', models.TextField()),
                ('woordvoerder', models.CharField(max_length=250)),
                ('toelichting', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')),
                ('betreft', models.CharField(max_length=250)),
                ('type', models.CharField(max_length=2, choices=[('W', 'Vervangen'), ('S', 'Schrappen'), ('T', 'Toevoegen')])),
                ('tekst1', models.TextField()),
                ('tekst2', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'amendementen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('prefix', models.CharField(max_length=50)),
                ('titel', models.CharField(max_length=250)),
                ('index', models.IntegerField()),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'categorieen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HRWijziging',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('titel', models.CharField(max_length=250)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Ingediend'), (2, 'Verwijderd'), (3, 'Repareren'), (4, 'Geaccepteerd'), (5, 'Publiek')])),
                ('admin_opmerkingen', models.TextField(blank=True, help_text='Opmerkingen van de beheerder')),
                ('boeknummer', models.IntegerField(blank=True, default=0)),
                ('indienmoment', models.DateField(auto_now_add=True)),
                ('laatsteupdate', models.DateField(auto_now=True)),
                ('secret', models.CharField(max_length=250)),
                ('indieners', models.TextField()),
                ('woordvoerder', models.CharField(max_length=250)),
                ('toelichting', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')),
                ('betreft', models.CharField(max_length=250)),
                ('type', models.CharField(max_length=2, choices=[('W', 'Vervangen'), ('S', 'Schrappen'), ('T', 'Toevoegen')])),
                ('tekst1', models.TextField()),
                ('tekst2', models.TextField(blank=True)),
                ('categorie', models.ForeignKey(to='zues.Categorie', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
            ],
            options={
                'verbose_name_plural': 'HR-wijzigingen',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('naam', models.CharField(max_length=250)),
                ('lidnummer', models.IntegerField()),
                ('secret', models.CharField(max_length=250)),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organimo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('titel', models.CharField(max_length=250)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Ingediend'), (2, 'Verwijderd'), (3, 'Repareren'), (4, 'Geaccepteerd'), (5, 'Publiek')])),
                ('admin_opmerkingen', models.TextField(blank=True, help_text='Opmerkingen van de beheerder')),
                ('boeknummer', models.IntegerField(blank=True, default=0)),
                ('indienmoment', models.DateField(auto_now_add=True)),
                ('laatsteupdate', models.DateField(auto_now=True)),
                ('secret', models.CharField(max_length=250)),
                ('indieners', models.TextField()),
                ('woordvoerder', models.CharField(max_length=250)),
                ('toelichting', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')),
                ('constateringen', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')),
                ('overwegingen', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')),
                ('uitspraken', models.TextField(help_text='Gebruik een dubbele enter voor de volgende bullet')),
                ('categorie', models.ForeignKey(to='zues.Categorie', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('eigenaar', models.ForeignKey(to='zues.Login', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
            ],
            options={
                'ordering': ('-laatsteupdate',),
                'verbose_name_plural': 'organimos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PolitiekeMotie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('titel', models.CharField(max_length=250)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Ingediend'), (2, 'Verwijderd'), (3, 'Repareren'), (4, 'Geaccepteerd'), (5, 'Publiek')])),
                ('admin_opmerkingen', models.TextField(blank=True, help_text='Opmerkingen van de beheerder')),
                ('boeknummer', models.IntegerField(blank=True, default=0)),
                ('indienmoment', models.DateField(auto_now_add=True)),
                ('laatsteupdate', models.DateField(auto_now=True)),
                ('secret', models.CharField(max_length=250)),
                ('indieners', models.TextField()),
                ('woordvoerder', models.CharField(max_length=250)),
                ('toelichting', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')),
                ('constateringen', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')),
                ('overwegingen', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')),
                ('uitspraken', models.TextField(help_text='Gebruik een dubbele enter voor de volgende bullet')),
                ('categorie', models.ForeignKey(to='zues.Categorie', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('eigenaar', models.ForeignKey(to='zues.Login', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
            ],
            options={
                'ordering': ('-laatsteupdate',),
                'verbose_name_plural': 'politieke moties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resolutie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('titel', models.CharField(max_length=250)),
                ('status', models.IntegerField(default=1, choices=[(1, 'Ingediend'), (2, 'Verwijderd'), (3, 'Repareren'), (4, 'Geaccepteerd'), (5, 'Publiek')])),
                ('admin_opmerkingen', models.TextField(blank=True, help_text='Opmerkingen van de beheerder')),
                ('boeknummer', models.IntegerField(blank=True, default=0)),
                ('indienmoment', models.DateField(auto_now_add=True)),
                ('laatsteupdate', models.DateField(auto_now=True)),
                ('secret', models.CharField(max_length=250)),
                ('indieners', models.TextField()),
                ('woordvoerder', models.CharField(max_length=250)),
                ('toelichting', models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')),
                ('betreft', models.CharField(max_length=250)),
                ('type', models.CharField(max_length=2, choices=[('W', 'Vervangen'), ('S', 'Schrappen'), ('T', 'Toevoegen')])),
                ('tekst1', models.TextField()),
                ('tekst2', models.TextField(blank=True)),
                ('categorie', models.ForeignKey(to='zues.Categorie', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('eigenaar', models.ForeignKey(to='zues.Login', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'resoluties',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('naam', models.CharField(max_length=250)),
                ('mededeling', models.CharField(max_length=250)),
                ('public', models.BooleanField(default=False)),
                ('pm_start', models.DateTimeField(blank=True, null=True)),
                ('pm_stop', models.DateTimeField(blank=True, null=True)),
                ('apm_start', models.DateTimeField(blank=True, null=True)),
                ('apm_stop', models.DateTimeField(blank=True, null=True)),
                ('org_start', models.DateTimeField(blank=True, null=True)),
                ('org_stop', models.DateTimeField(blank=True, null=True)),
                ('res_start', models.DateTimeField(blank=True, null=True)),
                ('res_stop', models.DateTimeField(blank=True, null=True)),
                ('am_start', models.DateTimeField(blank=True, null=True)),
                ('am_stop', models.DateTimeField(blank=True, null=True)),
                ('hr_start', models.DateTimeField(blank=True, null=True)),
                ('hr_stop', models.DateTimeField(blank=True, null=True)),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'settings',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='hrwijziging',
            name='eigenaar',
            field=models.ForeignKey(to='zues.Login', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='hrwijziging',
            name='site',
            field=models.ForeignKey(editable=False, to='sites.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='amendement',
            name='categorie',
            field=models.ForeignKey(to='zues.Categorie', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='amendement',
            name='eigenaar',
            field=models.ForeignKey(to='zues.Login', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='amendement',
            name='site',
            field=models.ForeignKey(editable=False, to='sites.Site'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actuelepolitiekemotie',
            name='categorie',
            field=models.ForeignKey(to='zues.Categorie', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actuelepolitiekemotie',
            name='eigenaar',
            field=models.ForeignKey(to='zues.Login', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actuelepolitiekemotie',
            name='site',
            field=models.ForeignKey(editable=False, to='sites.Site'),
            preserve_default=True,
        ),
    ]

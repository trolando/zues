# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Locatie'
        db.create_table(u'appolo_locatie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('naam', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('lat', self.gf('django.db.models.fields.FloatField')()),
            ('long', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'appolo', ['Locatie'])

        # Adding model 'Dag'
        db.create_table(u'appolo_dag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datum', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'appolo', ['Dag'])

        # Adding model 'Activiteit'
        db.create_table(u'appolo_activiteit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('naam', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('begintijd', self.gf('django.db.models.fields.TimeField')()),
            ('eindtijd', self.gf('django.db.models.fields.TimeField')()),
            ('dag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appolo.Dag'])),
            ('locatie', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['appolo.Locatie'])),
        ))
        db.send_create_signal(u'appolo', ['Activiteit'])

        # Adding model 'Nieuwsitem'
        db.create_table(u'appolo_nieuwsitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('titel', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('tekst', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'appolo', ['Nieuwsitem'])

        # Adding model 'Hashtag'
        db.create_table(u'appolo_hashtag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tekst', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'appolo', ['Hashtag'])


    def backwards(self, orm):
        # Deleting model 'Locatie'
        db.delete_table(u'appolo_locatie')

        # Deleting model 'Dag'
        db.delete_table(u'appolo_dag')

        # Deleting model 'Activiteit'
        db.delete_table(u'appolo_activiteit')

        # Deleting model 'Nieuwsitem'
        db.delete_table(u'appolo_nieuwsitem')

        # Deleting model 'Hashtag'
        db.delete_table(u'appolo_hashtag')


    models = {
        u'appolo.activiteit': {
            'Meta': {'object_name': 'Activiteit'},
            'begintijd': ('django.db.models.fields.TimeField', [], {}),
            'dag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['appolo.Dag']"}),
            'eindtijd': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locatie': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['appolo.Locatie']"}),
            'naam': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'appolo.dag': {
            'Meta': {'object_name': 'Dag'},
            'datum': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'appolo.hashtag': {
            'Meta': {'object_name': 'Hashtag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tekst': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'appolo.locatie': {
            'Meta': {'object_name': 'Locatie'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'long': ('django.db.models.fields.FloatField', [], {}),
            'naam': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'appolo.nieuwsitem': {
            'Meta': {'object_name': 'Nieuwsitem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tekst': ('django.db.models.fields.TextField', [], {}),
            'titel': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['appolo']
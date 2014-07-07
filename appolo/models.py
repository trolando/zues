from django.db import models

class Locatie(models.Model):
    def __unicode__(self):
        return self.naam
    naam = models.CharField(max_length=200)
    lat = models.FloatField()
    long = models.FloatField()

class Dag(models.Model):
    def __unicode__(self):
        return unicode(self.datum)
    datum = models.DateField()

class Activiteit(models.Model):
    def __unicode__(self):
        return self.naam
    naam = models.CharField(max_length=200)
    begintijd = models.TimeField()
    eindtijd = models.TimeField()
    dag = models.ForeignKey(Dag)
    locatie = models.ForeignKey(Locatie)

class Nieuwsitem(models.Model):
    def __unicode__(self):
        return self.titel
    titel = models.CharField(max_length=200)
    tekst = models.TextField()

class Hashtag(models.Model):
    def __unicode__(self):
        return self.tekst
    tekst = models.CharField(max_length=200)

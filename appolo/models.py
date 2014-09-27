from django.db import models

class Locatie(models.Model):
    def __unicode__(self):
        return self.naam
    naam = models.CharField(max_length=200)
    lat = models.FloatField()
    long = models.FloatField()

    class Meta:
        verbose_name_plural = 'locaties'

class Dag(models.Model):
    def __unicode__(self):
        return unicode(self.datum)
    datum = models.DateField()

    class Meta:
        verbose_name_plural = 'dagen'

class Activiteit(models.Model):
    def __unicode__(self):
        return self.naam
    naam = models.CharField(max_length=200)
    begintijd = models.DateTimeField()
    eindtijd = models.DateTimeField()
    dag = models.ForeignKey(Dag)
    locatie = models.ForeignKey(Locatie)

    class Meta:
        verbose_name_plural = 'activiteiten'

class Nieuwsitem(models.Model):
    def __unicode__(self):
        return self.titel
    titel = models.CharField(max_length=200)
    tekst = models.TextField()

    class Meta:
        verbose_name_plural = 'nieuwsitems'

class Hashtag(models.Model):
    def __unicode__(self):
        return self.tekst
    tekst = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'hashtags'

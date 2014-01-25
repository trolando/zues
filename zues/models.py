from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Ondersteuning(models.Model):
    naam = models.CharField(max_length=250,)
    secret = models.CharField(max_length=250,) # code voor verwijderen
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = 'ondersteuningen'

    def __unicode__(self):
        return "Steun van '%s' voor '%s'" % (self.naam,str(self.content_object))

class Stuk(models.Model):
    titel = models.CharField(max_length=250,)
    woordvoerder = models.CharField(max_length=250,)
    indienmoment = models.DateField(auto_now_add=True)
    laatsteupdate = models.DateField(auto_now=True)
    admin_opmerkingen = models.TextField(blank=True, help_text='Opmerkingen van de beheerder')
    secret = models.CharField(max_length=250,) # code voor wijzigen
    steuners = generic.GenericRelation(Ondersteuning)
    toelichting = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')

    class Meta:
        abstract = True

class Motie(Stuk):
    constateringen = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')
    overwegingen = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')
    uitspraken = models.TextField(help_text='Gebruik een dubbele enter voor de volgende bullet')

    class Meta:
        abstract = True

class Organimo(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'organimos'

    def __unicode__(self):
        return 'Organimo %s' % self.titel

class PolitiekeMotie(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'politieke moties'

    def __unicode__(self):
        return 'Politieke Motie %s' % self.titel

class ActuelePolitiekeMotie(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'actuele politieke moties'

    def __unicode__(self):
        return 'Actuele Politieke Motie %s' % self.titel

class Modificatie(Stuk):
    WIJZIGEN = 'W'
    SCHRAPPEN = 'S'
    TOEVOEGEN = 'T'
    type_CHOICES = ((WIJZIGEN, 'Wijzigen'),(SCHRAPPEN, 'Schrappen'),(TOEVOEGEN, 'Toevoegen'))

    betreft = models.CharField(max_length=250,)
    type = models.CharField(max_length=2, choices=type_CHOICES, blank=False)
    tekst1 = models.TextField()
    tekst2 = models.TextField(blank=True)

    class Meta:
        abstract = True

class Resolutie(Modificatie):
    class Meta:
        verbose_name_plural = 'resoluties'

class AmendementRes(Modificatie):
    resolutie = models.ForeignKey(Resolutie)

    class Meta:
        verbose_name_plural = 'amendementen op een resolutie'

class AmendementPP(Modificatie):
    class Meta:
        verbose_name_plural = 'amendementen op het politieke programma'

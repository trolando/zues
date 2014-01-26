from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from re import sub

class Login(models.Model):
    lidnummer = models.CharField(max_length=250,)
    secret = models.CharField(max_length=250,)

    def __unicode__(self):
        return "Login %s" % self.lidnummer

    def get_secret_url(self):
        return reverse('zues:login', kwargs={'key': self.secret, 'lid': self.lidnummer})

class Stuk(models.Model):
    titel = models.CharField(max_length=250,)
    indieners = models.TextField()
    woordvoerder = models.CharField(max_length=250,)
    indienmoment = models.DateField(auto_now_add=True)
    laatsteupdate = models.DateField(auto_now=True)
    admin_opmerkingen = models.TextField(blank=True, help_text='Opmerkingen van de beheerder')
    secret = models.CharField(max_length=250,)
    toelichting = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')
    eigenaar = models.ForeignKey(Login)
    verwijderd = models.BooleanField(default=False)

    class Meta:
        abstract = True

class Motie(Stuk):
    constateringen = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')
    overwegingen = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')
    uitspraken = models.TextField(help_text='Gebruik een dubbele enter voor de volgende bullet')

    class Meta:
        abstract = True

    def to_list(self, str):
        if str == None: return []
        str = "\n".join([s.strip() for s in str.strip().split("\n")])
        str = [s for s in str.split("\n") if len(s)]
        return str

    def to_p(self, str):
        if str == None: return ""
        str = "\n".join([s.strip() for s in str.strip().split("\n")])
        str = sub("(?<!\n)(\n)(?!\n)", "<br />", str)
        str = [s for s in str.split("\n") if len(s)]
        if len(str) == 0: return ""
        return "<p>" + "</p><p>".join(str) + "</p>"

    def get_content(self):
        con = self.to_list(self.constateringen)
        if len(con)>1: con = "<p><strong>constaterende dat</strong></p><ul><li>" + "</li><li>".join(con) + "</li></ul>"
        elif len(con): con = "<p><strong>constaterende dat</strong></p><p>" + con[0] + "</p>"
        else: con = ""

        over = self.to_list(self.overwegingen)
        if len(over)>1: over = "<p><strong>overwegende dat</strong></p><ul><li>" + "</li><li>".join(over) + "</li></ul>"
        elif len(over): over = "<p><strong>overwegende dat</strong></p><p>" + over[0] + "</p>"
        else: over = ""

        uit = self.to_list(self.uitspraken)
        if len(uit)>1: uit = "<p><strong>spreekt uit dat</strong></p><ul><li>" + "</li><li>".join(uit) + "</li></ul>"
        elif len(uit): uit = "<p><strong>spreekt uit dat</strong></p><p>" + uit[0] + "</p>"
        else: uit = ""

        toe = self.to_p(self.toelichting)
        toe = len(toe) and ("<p><strong>Toelichting:</strong></p><p>" + toe + "</p>") or ""

        orde = "<p><em>en gaat over tot de orde van de dag.</em></p>"

        return "<p>De ALV der Jonge Democraten,</p>" + con + over + uit + orde + toe

    def as_html(self):
        html = []
        html.append("<div class='pm'>")
        html.append("<fieldset>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Titel:</label></div>")
        html.append("<div class='cell'><p>%s</p></div>" % self.titel)
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Indieners:</label></div>")
        html.append("<div class='cell'><p>%s</p></div>" % self.indieners)
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Woordvoerder:</label></div>")
        html.append("<div class='cell'><p>%s</p></div>" % self.woordvoerder)
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Inhoud:</label></div>")
        html.append("<div class='cell'>%s</div>" % self.get_content())
        html.append("</div>")
        html.append("</fieldset>")
        html.append("</div>")
        return mark_safe('\n'.join(html))

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

    def get_secret_url(self):
        return reverse('zues:pm', kwargs={'key': self.secret, 'pk': self.pk})

    def get_absolute_url(self):
        return self.get_secret_url()

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

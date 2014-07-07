from datetime import datetime
from django.utils import formats
from django.utils.timezone import utc, is_aware, now, localtime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.core.urlresolvers import reverse
from re import sub
from solo.models import SingletonModel
import json

class Login(models.Model):
    naam = models.CharField(max_length=250,)
    lidnummer = models.IntegerField(primary_key=True,)
    secret = models.CharField(max_length=250,)

    def __unicode__(self):
        return unicode("Login {0} ({1})".format(self.lidnummer, self.naam))

class Tijden(SingletonModel):
    pm_start = models.DateTimeField(null=True, blank=True)
    pm_stop = models.DateTimeField(null=True, blank=True)
    apm_start = models.DateTimeField(null=True, blank=True)
    apm_stop = models.DateTimeField(null=True, blank=True)
    org_start = models.DateTimeField(null=True, blank=True)
    org_stop = models.DateTimeField(null=True, blank=True)
    res_start = models.DateTimeField(null=True, blank=True)
    res_stop = models.DateTimeField(null=True, blank=True)
    am_start = models.DateTimeField(null=True, blank=True)
    am_stop = models.DateTimeField(null=True, blank=True)
    hr_start = models.DateTimeField(null=True, blank=True)
    hr_stop = models.DateTimeField(null=True, blank=True)

    def _check(self, start, stop):
        _now = now()
        if start != None and _now < start: return False
        if stop != None and _now > stop: return False
        return True

    def mag_pm(self):
        return self._check(self.pm_start, self.pm_stop)

    def mag_apm(self):
        return self._check(self.apm_start, self.apm_stop)

    def mag_org(self):
        return self._check(self.org_start, self.org_stop)

    def mag_res(self):
        return self._check(self.res_start, self.res_stop)

    def mag_am(self):
        return self._check(self.am_start, self.am_stop)

    def mag_hr(self):
        return self._check(self.hr_start, self.hr_stop)

    def deadline_pm(self):
        if self.pm_stop == None: return "geen"
        else: return formats.date_format(localtime(self.pm_stop), "DATETIME_FORMAT")

    def deadline_apm(self):
        if self.apm_stop == None: return "geen"
        else: return formats.date_format(localtime(self.apm_stop), "DATETIME_FORMAT")

    def deadline_org(self):
        if self.org_stop == None: return "geen"
        else: return formats.date_format(localtime(self.org_stop), "DATETIME_FORMAT")

    def deadline_res(self):
        if self.res_stop == None: return "geen"
        else: return formats.date_format(localtime(self.res_stop), "DATETIME_FORMAT")

    def deadline_am(self):
        if self.am_stop == None: return "geen"
        else: return formats.date_format(localtime(self.am_stop), "DATETIME_FORMAT")

    def deadline_hr(self):
        if self.hr_stop == None: return "geen"
        else: return formats.date_format(localtime(self.hr_stop), "DATETIME_FORMAT")

    class Meta:
        verbose_name_plural = 'tijden'

class Stuk(models.Model):
    titel = models.CharField(max_length=250,)
    indieners = models.TextField()
    woordvoerder = models.CharField(max_length=250,)
    indienmoment = models.DateField(auto_now_add=True)
    laatsteupdate = models.DateField(auto_now=True)
    admin_opmerkingen = models.TextField(blank=True, help_text='Opmerkingen van de beheerder')
    secret = models.CharField(max_length=250,)
    toelichting = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')
    eigenaar = models.ForeignKey(Login, blank=True, null=True, on_delete=models.SET_NULL) # bij verwijderen eigenaar, verliest eigenaar
    verwijderd = models.BooleanField(default=False)
    publiek = models.BooleanField(default=False)

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

    def to_commas(self, str):
        if str == None: return None
        str = ", ".join([s.strip() for s in str.strip().split("\n")])
        return str

    def get_content(self):
        con = self.to_list(escape(self.constateringen))
        if len(con)>1: con = "<p><strong>constaterende dat</strong></p><ul><li>" + "</li><li>".join(con) + "</li></ul>"
        elif len(con): con = "<p><strong>constaterende dat</strong></p><p>" + con[0] + "</p>"
        else: con = ""

        over = self.to_list(escape(self.overwegingen))
        if len(over)>1: over = "<p><strong>overwegende dat</strong></p><ul><li>" + "</li><li>".join(over) + "</li></ul>"
        elif len(over): over = "<p><strong>overwegende dat</strong></p><p>" + over[0] + "</p>"
        else: over = ""

        uit = self.to_list(escape(self.uitspraken))
        if len(uit)>1: uit = "<p><strong>spreekt uit dat</strong></p><ul><li>" + "</li><li>".join(uit) + "</li></ul>"
        elif len(uit): uit = "<p><strong>spreekt uit dat</strong></p><p>" + uit[0] + "</p>"
        else: uit = ""

        toe = self.to_p(escape(self.toelichting))
        toe = len(toe) and ("<p><strong>Toelichting:</strong></p><p>" + toe + "</p>") or ""

        orde = "<p><em>en gaat over tot de orde van de dag.</em></p>"

        return "<p>De ALV der Jonge Democraten,</p>" + con + over + uit + orde + toe

    def as_csv(self, typje):
        # Raar bestandsformaatje voor de congresapp
        res = []
        res.append('"' + typje + '"') # id
        res.append('\t')
        res.append('"' + escape(self.titel) + '"')
        res.append('\t')
        res.append('""') # lege betreft
        res.append('\t')
        res.append('"' + typje + '"') # groep
        res.append('\t')
        res.append('"' + escape(self.woordvoerder) + '"')
        res.append('\t')
        res.append('"' + escape(self.to_commas(self.indieners)) + '"')
        res.append('\t')
        res.append('"Constaterende dat"')
        res.append('\t')
        con = self.to_list(escape(self.constateringen))
        if con:
            if len(con)>1: res.append('"' + "\r\n".join(['* '+c for c in con]) + '"')
            else: res.append('"' + con[0] + '"')
        else: res.append('""')
        res.append('\t')
        res.append('"Overwegende dat"')
        res.append('\t')
        over = self.to_list(escape(self.overwegingen))
        if over:
            if len(over)>1: res.append('"'+ "\r\n".join(['* '+o for o in over]) + '"')
            else: res.append('"' + over[0] + '"')
        else: res.append('""')
        res.append('\t')
        res.append('"Spreekt uit dat"')
        res.append('\t')
        uit = self.to_list(escape(self.uitspraken))
        if uit:
            if len(uit)>1: res.append('"'+ "\r\n".join(['* '+u for u in uit]) + '"')
            else: res.append('"' + uit[0] + '"')
        else: res.append('""')
        res.append('\t')
        res.append('"' + escape(self.toelichting) + '"')
        res.append('\t')
        res.append('"Excel"')
        return mark_safe("".join(res))

    def as_dict(self, typje):
        # Dict-output, kan hergebruikt worden om JSON te genereren
        res = {}
        res['id'] = typje
        res['titel'] = self.titel
        res['groep'] = typje
        res['woordvoerder'] = self.woordvoerder
        res['indieners'] = self.to_commas(self.indieners)
        res['actie1'] = "Constaterende dat"
        con = self.to_list(escape(self.constateringen))
        if con:
            if len(con)>1: 
                res['tekst1'] = con
            else: 
                res['tekst1'] = con[0]
        res['actie2'] = "Overwegende dat"
        over = self.to_list(escape(self.overwegingen))
        if over:
            if len(over)>1: 
                res['tekst2'] = over
            else: res['tekst2'] = over[0]
        res['actie3'] = "Spreekt uit dat"
        uit = self.to_list(escape(self.uitspraken))
        if uit:
            if len(uit)>1: 
                res['tekst3'] = uit
            else: 
                res['tekst3'] = uit[0]
        res['toelichting'] = self.toelichting
        return res

    def as_html(self):
        html = []
        html.append("<div class='pm'>")
        html.append("<fieldset>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><p>Titel:</p></div>")
        html.append("<div class='cell'><p>%s</p></div>" % escape(self.titel))
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><p>Indieners:</p></div>")
        html.append("<div class='cell'><p>%s</p></div>" % escape(self.to_commas(self.indieners)))
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><p>Woordvoerder:</p></div>")
        html.append("<div class='cell'><p>%s</p></div>" % escape(self.woordvoerder))
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><p>Inhoud:</p></div>")
        html.append("<div class='cell'>%s</div>" % self.get_content())
        html.append("</div>")
        html.append("</fieldset>")
        html.append("</div>")
        return mark_safe('\n'.join(html))

    def as_html_table(self, ik):
        html = []
        html.append("<table border='1' class='export'>")
        html.append("<tr class='exporttitle'>")
        html.append("<td><p>%s</p></td>" % ik)
        html.append("<td><p>%s</p></td>" % escape(self.titel))
        html.append("</tr>")
        html.append("<tr class='exporthead'>")
        html.append("<td><p><strong>Indieners:</strong></p></td>")
        html.append("<td><p>%s</p></td>" % escape(self.to_commas(self.indieners)))
        html.append("</tr>")
        html.append("<tr class='exporthead'>")
        html.append("<td><p><strong>Woordvoerder:</strong></p></td>")
        html.append("<td><p>%s</p></td>" % escape(self.woordvoerder))
        html.append("</tr>")

        con = self.to_list(escape(self.constateringen))
        if len(con):
            if len(con)>1: con = "<ul><li>" + "</li><li>".join(con) + "</li></ul>"
            else: con = "<p>" + con[0] + "</p>"
            html.append("<tr>")
            html.append("<td><p><strong>Constaterende dat</strong></p></td>")
            html.append("<td>%s</td>" % con)
            html.append("</tr>")

        over = self.to_list(escape(self.overwegingen))
        if len(over):
            if len(over)>1: over = "<ul><li>" + "</li><li>".join(over) + "</li></ul>"
            else: over = "<p>" + over[0] + "</p>"
            html.append("<tr>")
            html.append("<td><p><strong>Overwegende dat</strong></p></td>")
            html.append("<td>%s</td>" % over)
            html.append("</tr>")

        uit = self.to_list(escape(self.uitspraken))
        if len(uit)>1: uit = "<ul><li>" + "</li><li>".join(uit) + "</li></ul>"
        elif len(uit): uit = "<p>" + uit[0] + "</p>"
        else: uit = ""
        html.append("<tr>")
        html.append("<td><p><strong>Spreekt uit dat</strong></p></td>")
        html.append("<td>%s</td>" % uit)
        html.append("</tr>")

        toe = self.to_p(escape(self.toelichting))
        if len(toe):
            html.append("<tr class='exporttoelichting'>")
            html.append("<td><p><strong>Toelichting:</strong></p></td>")
            html.append("<td>%s</td>" % toe)
            html.append("</tr>")

        html.append("</table>")
        return mark_safe('\n'.join(html))

class Organimo(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'organimos'

    def __unicode__(self):
        return 'ORG %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:org', kwargs={'key': self.secret, 'pk': self.pk})

    def as_csv(self):
        return super(Organimo, self).as_csv('ORG')

    def as_dict(self):
        return super(Organimo, self).as_dict('ORG')

    def as_html_table(self):
        return super(Organimo, self).as_html_table('ORG')

class PolitiekeMotie(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'politieke moties'

    def __unicode__(self):
        return 'PM %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:pm', kwargs={'key': self.secret, 'pk': self.pk})

    def as_csv(self):
        return super(PolitiekeMotie, self).as_csv('PM')

    def as_dict(self):
        return super(PolitiekeMotie, self).as_dict('PM')

    def as_html_table(self):
        return super(PolitiekeMotie, self).as_html_table('PM')

class ActuelePolitiekeMotie(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'actuele politieke moties'

    def __unicode__(self):
        return 'APM %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:apm', kwargs={'key': self.secret, 'pk': self.pk})

    def as_csv(self):
        return super(ActuelePolitiekeMotie, self).as_csv('APM')

    def as_dict(self):
        return super(ActuelePolitiekeMotie, self).as_dict('APM')

    def as_html_table(self):
        return super(ActuelePolitiekeMotie, self).as_html_table('APM')

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

    def to_commas(self, str):
        if str == None: return None
        str = ", ".join([s.strip() for s in str.strip().split("\n")])
        return str

    def to_p(self, str):
        if str == None: return ""
        str = "\n".join([s.strip() for s in str.strip().split("\n")])
        str = sub("(?<!\n)(\n)(?!\n)", "<br />", str)
        str = [s for s in str.split("\n") if len(s)]
        if len(str) == 0: return ""
        return "<p>" + "</p><p>".join(str) + "</p>"

    def get_content(self):
        if self.type == self.SCHRAPPEN:
            return "<p><strong>Schrap:</strong></p>" + self.to_p(escape(self.tekst1))

        if self.type == self.TOEVOEGEN:
            return "<p><strong>Voeg toe:</strong></p>" + self.to_p(escape(self.tekst1))

        if self.type == self.WIJZIGEN:
            return "<p><strong>Schrap:</strong></p>" + self.to_p(escape(self.tekst1)) + "<p><strong>Vervang door:</strong></p>" + self.to_p(escape(self.tekst2))

        return "Geen inhoud?!"

    def as_csv(self, typje):
        # Raar bestandsformaatje voor de congresapp
        res = []
        res.append('"'+typje+'"')
        res.append('\t')
        res.append('"' + escape(self.titel) + '"')
        res.append('\t')
        res.append('"' + escape(self.betreft) + '"')
        res.append('\t')
        res.append('"'+typje+'"') # groep
        res.append('\t')
        res.append('"' + escape(self.woordvoerder) + '"')
        res.append('\t')
        res.append('"' + escape(self.to_commas(self.indieners)) + '"')
        res.append('\t')
        if self.type == self.SCHRAPPEN or self.type == self.WIJZIGEN: res.append('"Schrap"')
        elif self.type == self.TOEVOEGEN: res.append('"Voeg toe"')
        else: res.append('""')
        res.append('\t')
        res.append('"' + escape(self.tekst1) + '"')
        res.append('\t')
        if self.type == self.WIJZIGEN: res.append('"Vervang door"')
        else: res.append('""')
        res.append('\t')
        res.append('"' + escape(self.tekst2) + '"')
        res.append('\t')
        res.append('\t')
        res.append('\t')
        res.append('"' + escape(self.toelichting) + '"')
        res.append('\t')
        res.append('"Excel"')
        return mark_safe("".join(res))

    def as_dict(self, typje):
        # Dict-output, kan hergebruikt worden om JSON te genereren
        res = {}
        res['id'] = typje
        res['titel'] = self.titel
        res['betreft'] = self.betreft
        res['groep'] = typje
        res['woordvoerder'] = self.woordvoerder
        res['indieners'] = self.to_commas(self.indieners)
        if self.type == self.SCHRAPPEN or self.type == self.WIJZIGEN:
            res['actie1'] = "Schrap"
        elif self.type == self.TOEVOEGEN:
            res['actie1'] = "Voeg toe"
        res['tekst1'] = self.tekst1
        if self.type == self.WIJZIGEN:
            res['actie2'] = "Vervang door"
        res['tekst2'] = self.tekst2
        res['toelichting'] = self.toelichting
        return res

    def as_html(self):
        html = []
        html.append("<div class='pm'>")
        html.append("<fieldset>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Titel:</label></div>")
        html.append("<div class='cell'><p>%s</p></div>" % escape(self.titel))
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Indieners:</label></div>")
        html.append("<div class='cell'><p>%s</p></div>" % escape(self.to_commas(self.indieners)))
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Woordvoerder:</label></div>")
        html.append("<div class='cell'><p>%s</p></div>" % escape(self.woordvoerder))
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Betreft:</label></div>")
        html.append("<div class='cell'><p>%s</p></div>" % escape(self.betreft))
        html.append("</div>")
        html.append("<div class='row'>")
        html.append("<div class='cell'><label>Inhoud:</label></div>")
        html.append("<div class='cell'>%s</div>" % self.get_content())
        html.append("</div>")
        html.append("</fieldset>")
        html.append("</div>")
        return mark_safe('\n'.join(html))

    def as_html_table(self, ik):
        html = []
        html.append("<table border='1' class='export'>")
        html.append("<tr class='exporttitle'>")
        html.append("<td><p>%s</p></td>" % ik)
        html.append("<td><p>%s</p></td>" % escape(self.titel))
        html.append("</tr>")
        html.append("<tr class='exporthead'>")
        html.append("<td><p><strong>Indieners:</strong></p></td>")
        html.append("<td><p>%s</p></td>" % escape(self.to_commas(self.indieners)))
        html.append("</tr>")
        html.append("<tr class='exporthead'>")
        html.append("<td><p><strong>Woordvoerder:</strong></p></td>")
        html.append("<td><p>%s</p></td>" % escape(self.woordvoerder))
        html.append("</tr>")
        if len(self.betreft):
            html.append("<tr class='exporthead'>")
            html.append("<td><p><strong>Betreft:</strong></p></td>")
            html.append("<td><p>%s</p></td>" % escape(self.betreft))
            html.append("</tr>")

        if self.type == self.WIJZIGEN:
            html.append("<tr>")
            html.append("<td><p><strong>Schrap:</strong></p></td>")
            html.append("<td>%s</td>" % self.to_p(escape(self.tekst1)))
            html.append("</tr>")
            html.append("<tr>")
            html.append("<td><p><strong>Vervang door:</strong></p></td>")
            html.append("<td>%s</td>" % self.to_p(escape(self.tekst2)))
            html.append("</tr>")
        elif self.type == self.SCHRAPPEN:
            html.append("<tr>")
            html.append("<td><p><strong>Schrap:</strong></p></td>")
            html.append("<td>%s</td>" % self.to_p(escape(self.tekst1)))
            html.append("</tr>")
        elif self.type == self.TOEVOEGEN:
            html.append("<tr>")
            html.append("<td><p><strong>Voeg toe:</strong></p></td>")
            html.append("<td>%s</td>" % self.to_p(escape(self.tekst1)))
            html.append("</tr>")

        toe = self.to_p(escape(self.toelichting))
        if len(toe):
            html.append("<tr class='exporttoelichting'>")
            html.append("<td><p><strong>Toelichting:</strong></p></td>")
            html.append("<td>%s</td>" % toe)
            html.append("</tr>")

        html.append("</table>")
        return mark_safe('\n'.join(html))

class Resolutie(Modificatie):
    class Meta:
        verbose_name_plural = 'resoluties'

    def __unicode__(self):
        return 'RES %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:res', kwargs={'key': self.secret, 'pk': self.pk})

    def as_csv(self):
        return super(Resolutie, self).as_csv('RES')

    def as_dict(self):
        return super(Resolutie, self).as_dict('RES')

    def as_html_table(self):
        return super(Resolutie, self).as_html_table('RES')

class Amendement(Modificatie):
    class Meta:
        verbose_name_plural = 'amendementen'

    def __unicode__(self):
        return 'AM %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:am', kwargs={'key': self.secret, 'pk': self.pk})

    def as_csv(self):
        return super(Amendement, self).as_csv('AM')

    def as_dict(self):
        return super(Amendement, self).as_dict('AM')

    def as_html_table(self):
        return super(Amendement, self).as_html_table('AM')

class HRWijziging(Modificatie):
    class Meta:
        verbose_name_plural = "HR-wijzigingen"

    def __unicode__(self):
        return 'HR %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:hr', kwargs={'key': self.secret, 'pk': self.pk})

    def as_csv(self):
        return super(HRWijziging, self).as_csv('HR')

    def as_dict(self):
        return super(HRWijziging, self).as_dict('HR')

    def as_html_table(self):
        return super(HRWijziging, self).as_html_table('HR')

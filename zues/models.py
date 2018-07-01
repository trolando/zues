from django.core.urlresolvers import reverse
from django.db import models
from django.utils import formats
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.timezone import now, localtime
from re import match, sub, split

from . import utils


class SiteRelated(models.Model):
    objects = utils.CurrentSiteManager()

    class Meta:
        abstract = True

    site = models.ForeignKey("sites.Site", editable=False)

    def save(self, update_site=False, *args, **kwargs):
        if update_site or not self.site_id:
            self.site_id = utils.current_site_id()
        super(SiteRelated, self).save(*args, **kwargs)


class Login(SiteRelated):
    naam = models.CharField(max_length=250)
    lidnummer = models.IntegerField()
    secret = models.CharField(max_length=250)

    def __str__(self):
        return "Login {0} ({1})".format(self.lidnummer, self.naam)


class Settings(SiteRelated):
    naam = models.CharField(max_length=250)
    mededeling = models.CharField(max_length=250)
    public = models.BooleanField(default=False)

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
        if start is None or stop is None:
            return False
        return start < _now and _now < stop

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

    def _deadline(self, start, stop):
        _now = now()
        if stop is None or start is None:
            return "deadline niet ingesteld"
        if stop < _now:
            return "deadline verlopen"
        if start < _now:
            return "tot " + formats.date_format(localtime(stop), "DATETIME_FORMAT")
        else:
            return "vanaf " + formats.date_format(localtime(start), "DATETIME_FORMAT")

    def deadline_pm(self):
        return self._deadline(self.pm_start, self.pm_stop)

    def deadline_apm(self):
        return self._deadline(self.apm_start, self.apm_stop)

    def deadline_org(self):
        return self._deadline(self.org_start, self.org_stop)

    def deadline_res(self):
        return self._deadline(self.res_start, self.res_stop)

    def deadline_am(self):
        return self._deadline(self.am_start, self.am_stop)

    def deadline_hr(self):
        return self._deadline(self.hr_start, self.hr_stop)

    class Meta:
        verbose_name_plural = 'settings'


def get_settings():
    try:
        return Settings.objects.get()
    except Settings.DoesNotExist:
        s = Settings()
        s.save()
        return s


class Categorie(SiteRelated):
    prefix = models.CharField(max_length=50)
    titel = models.CharField(max_length=250,)
    index = models.IntegerField()

    def __str__(self):
        return "Categorie {0}".format(self.prefix)

    class Meta:
        verbose_name_plural = u'categorieën'


class Stuk(SiteRelated):
    INGEDIEND = 1
    VERWIJDERD = 2
    REPAREREN = 3
    GEACCEPTEERD = 4
    PUBLIEK = 5
    STATUS_CHOICES = (
        (INGEDIEND, 'Ingediend'),
        (VERWIJDERD, 'Verwijderd'),
        (REPAREREN, 'Repareren'),
        (GEACCEPTEERD, 'Geaccepteerd'),
        (PUBLIEK, 'Publiek'),
    )

    titel = models.CharField(max_length=250,)
    onderwerp = models.CharField(max_length=250, blank=True, null=True)
    eigenaar = models.ForeignKey(Login, blank=True, null=True, on_delete=models.SET_NULL)  # bij verwijderen eigenaar, verliest eigenaar
    status = models.IntegerField(choices=STATUS_CHOICES, default=INGEDIEND)
    admin_opmerkingen = models.TextField(blank=True, help_text='Opmerkingen van de beheerder')
    categorie = models.ForeignKey(Categorie, blank=True, null=True, on_delete=models.SET_NULL)  # bij verwijderen categorie, doei categorie
    boeknummer = models.IntegerField(blank=True, default=0)
    indienmoment = models.DateField(auto_now_add=True)
    laatsteupdate = models.DateField(auto_now=True)
    secret = models.CharField(max_length=250,)
    indieners = models.TextField()
    woordvoerder = models.CharField(max_length=250,)
    toelichting = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende paragraaf')

    def format_boeknummer(self, boeknrlen=2):
        if self.categorie is None:
            return self.stuk_type()
        else:
            format = "%s%.0" + str(max([boeknrlen, 2])) + "d"
            return escape(format % (self.categorie.prefix, self.boeknummer))

    def is_verwijderd(self):
        return self.status == Stuk.VERWIJDERD

    def in_reorder(self):
        return self.status == Stuk.GEACCEPTEERD or self.status == Stuk.PUBLIEK

    def mag_wijzigen(self):
        return self.status == Stuk.REPAREREN or (self.status == Stuk.INGEDIEND and self.mag())

    def mag_verwijderen(self):
        return self.status == Stuk.INGEDIEND and self.mag()

    class Meta:
        abstract = True


class Motie(Stuk):
    constateringen = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')
    overwegingen = models.TextField(blank=True, help_text='Gebruik een dubbele enter voor de volgende bullet')
    uitspraken = models.TextField(help_text='Gebruik een dubbele enter voor de volgende bullet')

    class Meta:
        abstract = True

    def to_list(self, str):
        if str is None:
            return []
        str = "\n".join([s.strip() for s in str.strip().split("\n")])
        str = [s for s in str.split("\n") if len(s)]
        return str

    def to_p(self, str):
        if str is None:
            return ""
        str = "\n".join([s.strip() for s in str.strip().split("\n")])
        str = sub("(?<!\n)(\n)(?!\n)", "<br />", str)
        str = [s for s in str.split("\n") if len(s)]
        if len(str) == 0:
            return ""
        return "<p>" + "</p><p>".join(str) + "</p>"

    def to_commas(self, str):
        if str is None:
            return None
        str = ", ".join([s.strip() for s in str.strip().split("\n")])
        return str

    def get_content(self):
        con = self.to_list(escape(self.constateringen))
        if len(con) > 1:
            con = "<p><strong>constaterende dat</strong></p><ul><li>" + "</li><li>".join(con) + "</li></ul>"
        elif len(con):
            con = "<p><strong>constaterende dat</strong></p><p>" + con[0] + "</p>"
        else:
            con = ""

        over = self.to_list(escape(self.overwegingen))
        if len(over) > 1:
            over = "<p><strong>overwegende dat</strong></p><ul><li>" + "</li><li>".join(over) + "</li></ul>"
        elif len(over):
            over = "<p><strong>overwegende dat</strong></p><p>" + over[0] + "</p>"
        else:
            over = ""

        uit = self.to_list(escape(self.uitspraken))
        if len(uit) > 1:
            uit = "<p><strong>spreekt uit dat</strong></p><ul><li>" + "</li><li>".join(uit) + "</li></ul>"
        elif len(uit):
            uit = "<p><strong>spreekt uit dat</strong></p><p>" + uit[0] + "</p>"
        else:
            uit = ""

        toe = self.to_p(escape(self.toelichting))
        toe = len(toe) and ("<p><strong>Toelichting:</strong></p><p>" + toe + "</p>") or ""

        orde = "<p><em>en gaat over tot de orde van de dag.</em></p>"

        return "<p>De ALV der Jonge Democraten,</p>" + con + over + uit + orde + toe

    def as_dict(self, typje, boeknrlen=2):
        # Dict-output, kan hergebruikt worden om JSON te genereren
        res = {}
        res['id'] = self.format_boeknummer(boeknrlen)
        res['titel'] = self.titel
        if self.categorie:
            res['groep'] = self.categorie.titel
        else:
            res['groep'] = typje
        res['woordvoerder'] = self.woordvoerder
        res['indieners'] = self.to_commas(self.indieners)
        inhoud = []
        con = self.to_list(escape(self.constateringen))
        if con:
            if len(con) > 1:
                inhoud.append(["Constaterende dat", con])
            else:
                inhoud.append(["Constaterende dat", con[0]])
        over = self.to_list(escape(self.overwegingen))
        if over:
            if len(over) > 1:
                inhoud.append(["Overwegende dat", over])
            else:
                inhoud.append(["Overwegende dat", over[0]])
        uit = self.to_list(escape(self.uitspraken))
        if uit:
            if len(uit) > 1:
                inhoud.append(["Spreekt uit dat", uit])
            else:
                inhoud.append(["Spreekt uit dat", uit[0]])
        res['inhoud'] = inhoud
        res['toelichting'] = self.toelichting
        return res

    def as_html_table(self, ik):
        html = []
        html.append("<table border='1' class='export pk-{0}-{1}'>".format(ik, self.pk))
        html.append("<tr class='exporttitle'>")
        html.append("<td><p>%s</p></td>" % self.format_boeknummer())
        html.append("<td><p>%s</p></td>" % escape(self.titel))
        html.append("</tr>")
        html.append("<tr class='exporthead'>")
        html.append("<td><p><strong>Onderwerp:</strong></p></td>")
        html.append("<td><p>%s</p></td>" % escape(self.to_commas(self.onderwerp)))
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
            if len(con) > 1:
                con = "<ul><li>" + "</li><li>".join(con) + "</li></ul>"
            else:
                con = "<p>" + con[0] + "</p>"
            html.append("<tr>")
            html.append("<td><p><strong>Constaterende dat</strong></p></td>")
            html.append("<td>%s</td>" % con)
            html.append("</tr>")

        over = self.to_list(escape(self.overwegingen))
        if len(over):
            if len(over) > 1:
                over = "<ul><li>" + "</li><li>".join(over) + "</li></ul>"
            else:
                over = "<p>" + over[0] + "</p>"
            html.append("<tr>")
            html.append("<td><p><strong>Overwegende dat</strong></p></td>")
            html.append("<td>%s</td>" % over)
            html.append("</tr>")

        uit = self.to_list(escape(self.uitspraken))
        if len(uit) > 1:
            uit = "<ul><li>" + "</li><li>".join(uit) + "</li></ul>"
        elif len(uit):
            uit = "<p>" + uit[0] + "</p>"
        else:
            uit = ""
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

    def as_html_table_snc(self, ik):
        html = []
        html.append("<table border='1' class='exportsnc pk-{0}-{1}'>".format(ik, self.pk))
        html.append("<tr class='exporttitle'>")
        html.append("<td><p>%s</p></td>" % self.format_boeknummer())
        html.append("<td colspan='2'><p>%s</p></td>" % escape(self.titel))
        html.append("</tr>")
        html.append("<tr class='exporthead'>")
        html.append("<td><p><strong>Onderwerp:</strong></p></td>")
        html.append("<td valign='top' colspan='2'><p>%s</p></td>" % escape(self.to_commas(self.onderwerp)))
        html.append("</tr>")

        uit = self.to_list(escape(self.uitspraken))
        if len(uit) > 1:
            uit = "<ul><li>" + "</li><li>".join(uit) + "</li></ul>"
        elif len(uit):
            uit = "<p>" + uit[0] + "</p>"
        else:
            uit = ""
        html.append("<tr class='exporthead'>")
        html.append("<td valign='top'><p><strong>Dictum</strong></p></td>")
        html.append("<td valign='top' colspan='2'>%s</td>" % uit)
        html.append("</tr>")

        html.append("<tr>")
        html.append("<td valign='top'><p>Woordvoerder:<br/>%s</p></td>" % escape(self.woordvoerder))
        html.append("<td valign='top' height='50px' colspan='2'><p></p></td>")
        html.append("</tr>")

        html.append("<tr class='exporthead'>");
        html.append("<td width='260px' valign='top'><p><strong>Voor</strong></p></td>");
        html.append("<td width='260px' valign='top'><p><strong>Neutraal</strong></p></td>");
        html.append("<td width='260px' valign='top'><p><strong>Tegen</strong></p></td>");
        html.append("</tr>");

        html.append("<tr class='sncvotecount'>");
        html.append("<td height='200px' valign='top'><p></p></td>");
        html.append("<td height='200px' valign='top'><p></p></td>");
        html.append("<td height='200px' valign='top'><p></p></td>");
        html.append("</tr>");

        html.append("<tr>")
        html.append("<td valign='top'><p>Woordvoerder:</p></td>")
        html.append("<td valign='top' height='50px' colspan='2'><p></p></td>")
        html.append("</tr>")

        html.append("<tr>");
        html.append("<td valign='top'><p>Stemming:</p></td>");
        html.append("<td valign='top' colspan='2'><p></p></td>");
        html.append("</tr>");

        html.append("</table>")
        return mark_safe('\n'.join(html))


class Organimo(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'organimo\'s'

    def __str__(self):
        return 'ORG %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:org', kwargs={'key': self.secret, 'pk': self.pk})

    def as_dict(self):
        return super(Organimo, self).as_dict('ORG')

    def as_html_table(self):
        return super(Organimo, self).as_html_table('ORG')

    def as_html_table_snc(self):
        return super(Organimo, self).as_html_table_snc('ORG')

    def stuk_type(self):
        return 'ORG'

    def mag(self):
        return get_settings().mag_org()


class PolitiekeMotie(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'politieke moties'

    def __str__(self):
        return 'PM %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:pm', kwargs={'key': self.secret, 'pk': self.pk})

    def as_dict(self, boeknrlen=2):
        return super(PolitiekeMotie, self).as_dict('PM', boeknrlen)

    def as_html_table(self):
        return super(PolitiekeMotie, self).as_html_table('PM')

    def as_html_table_snc(self):
        return super(PolitiekeMotie, self).as_html_table_snc('PM')

    def stuk_type(self):
        return 'PM'

    def mag(self):
        return get_settings().mag_pm()


class ActuelePolitiekeMotie(Motie):
    class Meta:
        ordering = ('-laatsteupdate',)
        verbose_name_plural = 'actuele politieke moties'

    def __str__(self):
        return 'APM %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:apm', kwargs={'key': self.secret, 'pk': self.pk})

    def as_dict(self):
        return super(ActuelePolitiekeMotie, self).as_dict('APM')

    def as_html_table(self):
        return super(ActuelePolitiekeMotie, self).as_html_table('APM')

    def as_html_table_snc(self):
        return super(ActuelePolitiekeMotie, self).as_html_table_snc('APM')

    def stuk_type(self):
        return 'APM'

    def mag(self):
        return get_settings().mag_apm()


class Modificatie(Stuk):
    WIJZIGEN = 'W'
    SCHRAPPEN = 'S'
    TOEVOEGEN = 'T'
    type_CHOICES = ((WIJZIGEN, 'Vervangen'), (SCHRAPPEN, 'Schrappen'), (TOEVOEGEN, 'Toevoegen'))

    betreft = models.CharField(max_length=250,)
    type = models.CharField(max_length=2, choices=type_CHOICES, blank=False)
    tekst1 = models.TextField()
    tekst2 = models.TextField(blank=True)

    class Meta:
        abstract = True

    def to_commas(self, str):
        if str is None:
            return None
        str = ", ".join([s.strip() for s in str.strip().split("\n")])
        return str

    def to_p(self, str):
        if str is None:
            return ""
        str = "\n".join([s.strip() for s in str.strip().split("\n")])
        str = sub("(?<!\n)(\n)(?!\n)", "<br />", str)
        str = [s for s in str.split("\n") if len(s)]
        if len(str) == 0:
            return ""
        return "<p>" + "</p><p>".join(str) + "</p>"

    def to_p_numbered(self, str):
        if str is None:
            return ""
        # First remove excessive whitespace
        str = "\n".join([s.strip() for s in str.strip().split("\n")])
        # Handle each part, splitting on multi-newline
        i = 1
        parts = []
        for part in split("\n\n+", str):
            # Check if this part is a chapter start
            m = match("(?P<header>\d+(\.\d+)*\.?[^\.\n]*\.?)\n*(?P<rest>.*)", part)
            if m is not None:
                parts += ["<p>{}</p>".format(m.group("header")), ]
                part = m.group("rest")
            # Convert "dot space" to "dot newline"
            part = sub("\. ", ".\n", part)
            newpart = ""
            for s in split("\n", part):
                if s.strip() != "":
                    newpart += "<span class=\"v\">{:d} </span>{:s} ".format(i, s)
                    i += 1
            parts += ["<p>{}</p>".format(newpart), ]
        return "".join(parts)

    def get_content(self):
        if self.type == self.SCHRAPPEN:
            return "<p><strong>Schrap:</strong></p>" + self.to_p(escape(self.tekst1))

        if self.type == self.TOEVOEGEN:
            return "<p><strong>Voeg toe:</strong></p>" + self.to_p(escape(self.tekst1))

        if self.type == self.WIJZIGEN:
            return "<p><strong>Schrap:</strong></p>" + self.to_p(escape(self.tekst1)) + "<p><strong>Vervang door:</strong></p>" + self.to_p(escape(self.tekst2))

        return "Geen inhoud?!"

    def as_dict(self, typje):
        # Dict-output, kan hergebruikt worden om JSON te genereren
        res = {}
        res['id'] = self.format_boeknummer()
        res['titel'] = self.titel
        if self.categorie:
            res['groep'] = self.categorie.titel
        else:
            res['groep'] = typje
        res['woordvoerder'] = self.woordvoerder
        res['indieners'] = self.to_commas(self.indieners)
        inhoud = [['Betreft', self.betreft]]
        if self.type == self.SCHRAPPEN or self.type == self.WIJZIGEN:
            inhoud.append(["Schrap", self.tekst1])
        elif self.type == self.TOEVOEGEN:
            inhoud.append(["Voeg toe", self.tekst1])
        if self.type == self.WIJZIGEN:
            inhoud.append(["Vervang door", self.tekst2])
        res['inhoud'] = inhoud
        res['toelichting'] = self.toelichting
        return res

    def as_html_table(self, ik):
        html = []
        html.append("<table border='1' class='export pk-{0}-{1}'>".format(ik, self.pk))
        html.append("<tr class='exporttitle'>")
        html.append("<td><p>%s</p></td>" % self.format_boeknummer())
        html.append("<td><p>%s</p></td>" % escape(self.titel))
        html.append("</tr>")
        html.append("<tr class='exporthead'>")
        html.append("<td><p><strong>Onderwerp:</strong></p></td>")
        html.append("<td><p>%s</p></td>" % escape(self.to_commas(self.onderwerp)))
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
            # html.append("<td>%s</td>" % self.to_p_numbered(escape(self.tekst2)))
            html.append("</tr>")
        elif self.type == self.SCHRAPPEN:
            html.append("<tr>")
            html.append("<td><p><strong>Schrap:</strong></p></td>")
            html.append("<td>%s</td>" % self.to_p(escape(self.tekst1)))
            html.append("</tr>")
        elif self.type == self.TOEVOEGEN:
            html.append("<tr>")
            html.append("<td><p><strong>Voeg toe:</strong></p></td>")
            # html.append("<td>%s</td>" % self.to_p_numbered(escape(self.tekst1)))
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

    def as_html_table_snc(self, ik):
        html = []
        html.append("<table border='1' class='exportsnc pk-{0}-{1}'>".format(ik, self.pk))
        html.append("<tr class='exporttitle'>")
        html.append("<td><p>%s</p></td>" % self.format_boeknummer())
        html.append("<td colspan='2'><p>%s</p></td>" % escape(self.titel))
        html.append("</tr>")

        html.append("<tr class='exporthead'>")
        html.append("<td><p><strong>Onderwerp:</strong></p></td>")
        html.append("<td valign='top' colspan='2'><p>%s</p></td>" % escape(self.to_commas(self.onderwerp)))
        html.append("</tr>")

        html.append("<tr>")
        html.append("<td valign='top'><p>Woordvoerder:<br/>%s</p></td>" % escape(self.woordvoerder))
        html.append("<td valign='top' height='50px' colspan='2'><p></p></td>")
        html.append("</tr>")

        html.append("<tr class='exporthead'>");
        html.append("<td width='260px' valign='top'><p><strong>Voor</strong></p></td>");
        html.append("<td width='260px' valign='top'><p><strong>Neutraal</strong></p></td>");
        html.append("<td width='260px' valign='top'><p><strong>Tegen</strong></p></td>");
        html.append("</tr>");

        html.append("<tr class='sncvotecount'>");
        html.append("<td height='200px' valign='top'><p></p></td>");
        html.append("<td height='200px' valign='top'><p></p></td>");
        html.append("<td height='200px' valign='top'><p></p></td>");
        html.append("</tr>");

        html.append("<tr>")
        html.append("<td valign='top'><p>Woordvoerder:</p></td>")
        html.append("<td valign='top' height='50px' colspan='2'><p></p></td>")
        html.append("</tr>")

        html.append("<tr>");
        html.append("<td valign='top'><p>Stemming:</p></td>");
        html.append("<td valign='top' colspan='2'><p></p></td>");
        html.append("</tr>");

        html.append("</table>")
        return mark_safe('\n'.join(html))


class Resolutie(Modificatie):
    class Meta:
        verbose_name_plural = 'resoluties'

    def __str__(self):
        return 'RES %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:res', kwargs={'key': self.secret, 'pk': self.pk})

    def as_dict(self):
        return super(Resolutie, self).as_dict('RES')

    def as_html_table(self):
        return super(Resolutie, self).as_html_table('RES')

    def as_html_table_snc(self):
        return super(Resolutie, self).as_html_table_snc('RES')

    def stuk_type(self):
        return 'RES'

    def mag(self):
        return get_settings().mag_res()


class Amendement(Modificatie):
    class Meta:
        verbose_name_plural = 'amendementen'

    def __str__(self):
        return 'AM %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:am', kwargs={'key': self.secret, 'pk': self.pk})

    def as_dict(self):
        return super(Amendement, self).as_dict('AM')

    def as_html_table(self):
        return super(Amendement, self).as_html_table('AM')

    def as_html_table_snc(self):
        return super(Amendement, self).as_html_table_snc('AM')

    def stuk_type(self):
        return 'AM'

    def mag(self):
        return get_settings().mag_am()


class HRWijziging(Modificatie):
    class Meta:
        verbose_name_plural = "HR-wijzigingen"

    def __str__(self):
        return 'HR %s' % self.titel

    def get_absolute_url(self):
        return reverse('zues:hr', kwargs={'key': self.secret, 'pk': self.pk})

    def as_dict(self):
        return super(HRWijziging, self).as_dict('HR')

    def as_html_table(self):
        return super(HRWijziging, self).as_html_table('HR')

    def as_html_table_snc(self):
        return super(HRWijziging, self).as_html_table_snc('HR')

    def stuk_type(self):
        return 'HR'

    def mag(self):
        return get_settings().mag_hr()

    def to_p_numbered(self, str):
        return self.to_p(str)

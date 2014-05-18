from django.forms import Form, ModelForm, CharField, IntegerField, Textarea, EmailField
from captcha.fields import ReCaptchaField
from zues import models

class MotieForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['titel'].widget.attrs.update({'placeholder': 'Titel van het voorstel'})
        self.fields['woordvoerder'].widget.attrs.update({'placeholder': 'Naam van de woordvoerder'})
        self.fields['indieners'].widget.attrs.update({'placeholder': '"[JD Afdeling] Voorzitter, Secretaris" of "Naam 1, Naam 2, etc... (minimaal 5)"'})
        self.fields['constateringen'].widget.attrs.update({'placeholder': 'Elke (optionele) constatering gescheiden door een of meerdere witregels..."'})
        self.fields['overwegingen'].widget.attrs.update({'placeholder': 'Elke (optionele) overweging gescheiden door een of meerdere witregels..."'})
        self.fields['uitspraken'].widget.attrs.update({'placeholder': 'Elke uitspraak gescheiden door een of meerdere witregels..."'})
        self.fields['toelichting'].widget.attrs.update({'placeholder': 'Optionele toelichting van maximaal 250 woorden...'})

class ResolutieForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResolutieForm, self).__init__(*args, **kwargs)
        self.fields['titel'].widget.attrs.update({'placeholder': 'Titel van het voorstel'})
        self.fields['woordvoerder'].widget.attrs.update({'placeholder': 'Naam van de woordvoerder'})
        self.fields['indieners'].widget.attrs.update({'placeholder': '"[JD Afdeling] Voorzitter, Secretaris" of "Naam 1, Naam 2, etc... (minimaal 5)"'})
        self.fields['betreft'].widget.attrs.update({'placeholder': 'Resolutie/Voorstel/Hoofdstuk N, pagina M, regels X-Y'})
        self.fields['tekst1'].widget.attrs.update({'placeholder': 'Volledige tekst die geschrapt of toegevoegd wordt...'})
        self.fields['tekst2'].widget.attrs.update({'placeholder': 'Volledige tekst die de geschrapte tekst vervangt... (alleen gebruiken bij type Wijzigen)'})
        self.fields['toelichting'].widget.attrs.update({'placeholder': 'Optionele toelichting van maximaal 250 woorden...'})

class PMForm(MotieForm):
    constateringen = CharField(widget=Textarea, label='Constaterende dat', required=False)
    overwegingen = CharField(widget=Textarea, label='Overwegende dat', required=False)
    uitspraken = CharField(widget=Textarea, label='Spreekt uit dat')

    class Meta:
        model = models.PolitiekeMotie
        fields = ('titel', 'woordvoerder', 'indieners', 'constateringen', 'overwegingen', 'uitspraken', 'toelichting',)

class APMForm(MotieForm):
    constateringen = CharField(widget=Textarea, label='Constaterende dat', required=False)
    overwegingen = CharField(widget=Textarea, label='Overwegende dat', required=False)
    uitspraken = CharField(widget=Textarea, label='Spreekt uit dat')

    class Meta:
        model = models.ActuelePolitiekeMotie
        fields = ('titel', 'woordvoerder', 'indieners', 'constateringen', 'overwegingen', 'uitspraken', 'toelichting',)

class ORGForm(MotieForm):
    constateringen = CharField(widget=Textarea, label='Constaterende dat', required=False)
    overwegingen = CharField(widget=Textarea, label='Overwegende dat', required=False)
    uitspraken = CharField(widget=Textarea, label='Spreekt uit dat')

    class Meta:
        model = models.Organimo
        fields = ('titel', 'woordvoerder', 'indieners', 'constateringen', 'overwegingen', 'uitspraken', 'toelichting',)

class RESForm(ResolutieForm):
    tekst1 = CharField(widget=Textarea, label='Schrap/Voeg toe:')
    tekst2 = CharField(widget=Textarea, label='Vervang door:', required=False)

    class Meta:
        model = models.Resolutie
        fields = ('titel', 'woordvoerder', 'indieners', 'betreft', 'type', 'tekst1', 'tekst2','toelichting',)

    def __init__(self, *args, **kwargs):
        super(RESForm, self).__init__(*args, **kwargs)
        self.fields['betreft'].widget.attrs.update({'placeholder': 'Hoofdstuk N, pagina M, regels X-Y'})
 
class AMForm(ResolutieForm):
    tekst1 = CharField(widget=Textarea, label='Schrap/Voeg toe:')
    tekst2 = CharField(widget=Textarea, label='Vervang door:', required=False)

    class Meta:
        model = models.Amendement
        fields = ('titel', 'woordvoerder', 'indieners', 'betreft', 'type', 'tekst1', 'tekst2','toelichting',)

    def __init__(self, *args, **kwargs):
        super(AMForm, self).__init__(*args, **kwargs)
        self.fields['betreft'].widget.attrs.update({'placeholder': 'Voorstel/Resolutie N, pagina M, regels X-Y'})

class HRForm(ResolutieForm):
    tekst1 = CharField(widget=Textarea, label='Schrap/Voeg toe:')
    tekst2 = CharField(widget=Textarea, label='Vervang door:', required=False)

    class Meta:
        model = models.HRWijziging
        fields = ('titel', 'woordvoerder', 'indieners', 'betreft', 'type', 'tekst1', 'tekst2', 'toelichting',)

    def __init__(self, *args, **kwargs):
        super(HRForm, self).__init__(*args, **kwargs)
        self.fields['betreft'].widget.attrs.update({'placeholder': 'Hoofdstuk N, pagina M, regels X-Y'})

class LidnummerForm(Form):
    lidnummer = IntegerField(label='Lidnummer:')

class LidnummerRecaptchaForm(LidnummerForm):
    captcha = ReCaptchaField()

class HelpLidnummerForm(Form):
    email = EmailField(max_length=254, label='Emailadres:')

class HelpLidnummerRecaptchaForm(HelpLidnummerForm):
    captcha = ReCaptchaField()



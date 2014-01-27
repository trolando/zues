from django.forms import Form, ModelForm, CharField, IntegerField, Textarea
from captcha.fields import ReCaptchaField
from zues import models

class PMForm(ModelForm):
    constateringen = CharField(widget=Textarea, label='Constaterende dat', required=False)
    overwegingen = CharField(widget=Textarea, label='Overwegende dat', required=False)
    uitspraken = CharField(widget=Textarea, label='Spreekt uit dat')

    class Meta:
        model = models.PolitiekeMotie
        fields = ('titel', 'woordvoerder', 'indieners', 'constateringen', 'overwegingen', 'uitspraken', 'toelichting',)

class APMForm(ModelForm):
    constateringen = CharField(widget=Textarea, label='Constaterende dat', required=False)
    overwegingen = CharField(widget=Textarea, label='Overwegende dat', required=False)
    uitspraken = CharField(widget=Textarea, label='Spreekt uit dat')

    class Meta:
        model = models.ActuelePolitiekeMotie
        fields = ('titel', 'woordvoerder', 'indieners', 'constateringen', 'overwegingen', 'uitspraken', 'toelichting',)

class ORGForm(ModelForm):
    constateringen = CharField(widget=Textarea, label='Constaterende dat', required=False)
    overwegingen = CharField(widget=Textarea, label='Overwegende dat', required=False)
    uitspraken = CharField(widget=Textarea, label='Spreekt uit dat')

    class Meta:
        model = models.Organimo
        fields = ('titel', 'woordvoerder', 'indieners', 'constateringen', 'overwegingen', 'uitspraken', 'toelichting',)

class RESForm(ModelForm):
    tekst1 = CharField(widget=Textarea, label='Schrap/Voeg toe:')
    tekst2 = CharField(widget=Textarea, label='Vervang door:', required=False)

    class Meta:
        model = models.Resolutie
        fields = ('titel', 'woordvoerder', 'indieners', 'betreft', 'type', 'tekst1', 'tekst2',)

class AMRESForm(ModelForm):
    tekst1 = CharField(widget=Textarea, label='Schrap/Voeg toe:')
    tekst2 = CharField(widget=Textarea, label='Vervang door:', required=False)

    class Meta:
        model = models.AmendementRes
        fields = ('titel', 'woordvoerder', 'indieners', 'betreft', 'type', 'tekst1', 'tekst2',)

class AMPPForm(ModelForm):
    tekst1 = CharField(widget=Textarea, label='Schrap/Voeg toe:')
    tekst2 = CharField(widget=Textarea, label='Vervang door:', required=False)

    class Meta:
        model = models.AmendementPP
        fields = ('titel', 'woordvoerder', 'indieners', 'betreft', 'type', 'tekst1', 'tekst2',)

class LidnummerForm(Form):
    lidnummer = IntegerField()
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(LidnummerForm, self).__init__(*args, **kwargs)
        self.fields['lidnummer'].label = "Lidnummer:"

    def is_valid(self):
        if not super(LidnummerForm, self).is_valid(): return False
        return True

from django.forms import Form, ModelForm, CharField, IntegerField, Textarea
from captcha.fields import ReCaptchaField
from zues import models

class PMForm(ModelForm):
    constateringen = CharField(widget=Textarea, label='Constaterende dat')
    overwegingen = CharField(widget=Textarea, label='Overwegende dat')
    uitspraken = CharField(widget=Textarea, label='Spreekt uit dat')

    class Meta:
        model = models.PolitiekeMotie
        fields = ('titel', 'woordvoerder', 'indieners', 'constateringen', 'overwegingen', 'uitspraken', 'toelichting',)

class LidnummerForm(Form):
    lidnummer = IntegerField()
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(LidnummerForm, self).__init__(*args, **kwargs)
        self.fields['lidnummer'].label = "Lidnummer:"

    def is_valid(self):
        if not super(LidnummerForm, self).is_valid(): return False
        return True

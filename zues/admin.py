from django.contrib import admin
from django import forms
from zues.models import PolitiekeMotie, ActuelePolitiekeMotie, Organimo, Resolutie, Amendement, HRWijziging, Login, Tijden, Categorie
from solo.admin import SingletonModelAdmin


class MotieForm(forms.ModelForm):
    class Meta:
        widgets = {
            'admin_opmerkingen': forms.Textarea(attrs={'rows': '4', })
        }


class MotieAdmin(admin.ModelAdmin):
    list_display = ('titel', 'status', 'admin_opmerkingen', 'categorie', 'boeknummer', 'eigenaar', 'woordvoerder', 'laatsteupdate')
    list_editable = ('categorie', 'admin_opmerkingen', 'boeknummer', 'status')

    def get_changelist_form(self, request, **kwargs):
        kwargs.setdefault('form', MotieForm)
        return super(MotieAdmin, self).get_changelist_form(request, **kwargs)

admin.site.register(Login)
admin.site.register(Tijden, SingletonModelAdmin)
admin.site.register(PolitiekeMotie, MotieAdmin)
admin.site.register(ActuelePolitiekeMotie, MotieAdmin)
admin.site.register(Organimo, MotieAdmin)
admin.site.register(Resolutie, MotieAdmin)
admin.site.register(Amendement, MotieAdmin)
admin.site.register(HRWijziging, MotieAdmin)
admin.site.register(Categorie)

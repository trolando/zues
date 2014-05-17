from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline
from zues.models import PolitiekeMotie, ActuelePolitiekeMotie, Organimo, Resolutie, AmendementRes, AmendementPP, Login, Tijden
from solo.admin import SingletonModelAdmin

class MotieAdmin(admin.ModelAdmin):
    list_display = ('titel', 'publiek', 'verwijderd', 'woordvoerder', 'indienmoment', 'laatsteupdate')
    list_editable = ('verwijderd', 'publiek',)

admin.site.register(Login)
admin.site.register(Tijden, SingletonModelAdmin)
admin.site.register(PolitiekeMotie, MotieAdmin)
admin.site.register(ActuelePolitiekeMotie, MotieAdmin)
admin.site.register(Organimo, MotieAdmin)
admin.site.register(Resolutie)
admin.site.register(AmendementRes)
admin.site.register(AmendementPP)

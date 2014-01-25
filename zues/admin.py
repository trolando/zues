from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline
from zues.models import Ondersteuning, PolitiekeMotie, ActuelePolitiekeMotie, Organimo, Resolutie, AmendementRes, AmendementPP

class SteunInline(GenericTabularInline):
    model = Ondersteuning

class MotieAdmin(admin.ModelAdmin):
    inlines = [SteunInline]
    list_display = ('titel', 'status', 'woordvoerder', 'indienmoment', 'laatsteupdate')

#admin.site.register(Ondersteuning)
admin.site.register(PolitiekeMotie, MotieAdmin)
admin.site.register(ActuelePolitiekeMotie, MotieAdmin)
admin.site.register(Organimo, MotieAdmin)
admin.site.register(Resolutie)
admin.site.register(AmendementRes)
admin.site.register(AmendementPP)

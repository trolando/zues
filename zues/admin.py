from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from zues.models import PolitiekeMotie, ActuelePolitiekeMotie, Organimo, Resolutie, Amendement, HRWijziging, Login, Settings, Categorie, Stuk


class MotieForm(forms.ModelForm):
    class Meta:
        widgets = {
            'admin_opmerkingen': forms.Textarea(attrs={'rows': '4', })
        }


def ingediend(modeladmin, request, queryset):
    queryset.update(status=Stuk.INGEDIEND)
ingediend.short_description = "Mark selected as Ingediend"


def verwijderen(modeladmin, request, queryset):
    queryset.update(status=Stuk.VERWIJDERD)
verwijderen.short_description = "Mark selected as Verwijderd"


def accepteren(modeladmin, request, queryset):
    queryset.update(status=Stuk.GEACCEPTEERD)
accepteren.short_description = "Mark selected as Geaccepteerd"


def repareren(modeladmin, request, queryset):
    queryset.update(status=Stuk.REPAREREN)
repareren.short_description = "Mark selected as Repareren"


def publiek(modeladmin, request, queryset):
    queryset.update(status=Stuk.PUBLIEK)
publiek.short_description = "Mark selected as Publiek"


class MotieAdmin(admin.ModelAdmin):
    list_display = ('titel', 'status', 'admin_opmerkingen', 'categorie', 'boeknummer', 'eigenaar', 'woordvoerder', 'laatsteupdate')
    list_editable = ('categorie', 'admin_opmerkingen', 'boeknummer', 'status')
    actions = [ingediend, verwijderen, accepteren, repareren, publiek]

    def get_changelist_form(self, request, **kwargs):
        kwargs.setdefault('form', MotieForm)
        return super(MotieAdmin, self).get_changelist_form(request, **kwargs)


def admin_url(model, url, object_id=None):
    """
    Returns the URL for the given model and admin url name.
    """
    opts = model._meta
    url = "admin:%s_%s_%s" % (opts.app_label, opts.object_name.lower(), url)
    args = ()
    if object_id is not None:
        args = (object_id,)
    return reverse(url, args=args)


class SingletonAdmin(admin.ModelAdmin):
    """
    Admin class for models that should only contain a single instance
    in the database. Redirect all views to the change view when the
    instance exists, and to the add view when it doesn't.
    Copyright Mezzanine.
    """

    def handle_save(self, request, response):
        """
        Handles redirect back to the dashboard when save is clicked
        (eg not save and continue editing), by checking for a redirect
        response, which only occurs if the form is valid.
        """
        form_valid = isinstance(response, HttpResponseRedirect)
        if request.POST.get("_save") and form_valid:
            return redirect("admin:index")
        return response

    def add_view(self, *args, **kwargs):
        """
        Redirect to the change view if the singleton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
            kwargs.setdefault("extra_context", {})
            kwargs["extra_context"]["singleton"] = True
            response = super(SingletonAdmin, self).add_view(*args, **kwargs)
            return self.handle_save(args[0], response)
        return redirect(admin_url(self.model, "change", singleton.id))

    def changelist_view(self, *args, **kwargs):
        """
        Redirect to the add view if no records exist or the change
        view if the singleton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except self.model.MultipleObjectsReturned:
            return super(SingletonAdmin, self).changelist_view(*args, **kwargs)
        except self.model.DoesNotExist:
            return redirect(admin_url(self.model, "add"))
        return redirect(admin_url(self.model, "change", singleton.id))

    def change_view(self, *args, **kwargs):
        """
        If only the singleton instance exists, pass ``True`` for
        ``singleton`` into the template which will use CSS to hide
        the "save and add another" button.
        """
        kwargs.setdefault("extra_context", {})
        kwargs["extra_context"]["singleton"] = self.model.objects.count() == 1
        response = super(SingletonAdmin, self).change_view(*args, **kwargs)
        return self.handle_save(args[0], response)


admin.site.register(Login)
admin.site.register(Settings, SingletonAdmin)
admin.site.register(PolitiekeMotie, MotieAdmin)
admin.site.register(ActuelePolitiekeMotie, MotieAdmin)
admin.site.register(Organimo, MotieAdmin)
admin.site.register(Resolutie, MotieAdmin)
admin.site.register(Amendement, MotieAdmin)
admin.site.register(HRWijziging, MotieAdmin)
admin.site.register(Categorie)

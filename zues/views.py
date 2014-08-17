from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.sites.models import Site
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.views.generic import View, FormView, DetailView, UpdateView, DeleteView, CreateView
from zues import models
from zues import forms
from zues import jdldap
import base64
import hashlib
import ldap
import os
import re
import json

def generate_lid(lidnummer):
    lidnummer = int(lidnummer)
    res = jdldap.attributes(lidnummer)
    if res == None: return None
    email, naam = res
        
    code = hashlib.sha256(base64.urlsafe_b64encode(os.urandom(64))).hexdigest()

    lid = models.Login.objects.filter(lidnummer=lidnummer)
    if len(lid):
        # lid bestaat al
        lid = lid[0]
        lid.secret = hashlib.sha256(code).hexdigest()
    else:
        # lid bestaat nog njet
        lid = models.Login(naam=naam, lidnummer=lidnummer, secret=hashlib.sha256(code).hexdigest()) 

    lid.save()
    return (lid, email, naam, code)

def check_login(request):
    if 'lid' not in request.session: return None
    if 'key' not in request.session: return None
    leden = models.Login.objects.filter(lidnummer=int(request.session['lid'])).filter(secret=hashlib.sha256(request.session['key']).hexdigest())
    if len(leden) == 0:
        try:
            del request.session['lid']
            del request.session['key']
        except KeyError:
            pass
        return None
    return leden[0]

def view_lidnummer(request):
    if request.method == 'POST':
        if getattr(settings, 'SKIP_RECAPTCHA', False):
            form = forms.HelpLidnummerForm(request.POST)
        else:
            form = forms.HelpLidnummerRecaptchaForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if getattr(settings, 'SKIP_EMAIL', False):
                return HttpResponseRedirect('/lidnummerverzonden/')

            for lidnummer, naam in jdldap.lidnummers(email):
                subject = '[JD] Lidnummer'
                from_email = 'noreply@jongedemocraten.nl'

                inhoud = []
                inhoud.append('Beste %s,' % naam)
                inhoud.append('')
                inhoud.append('Je hebt via de site van de Jonge Democraten je lidnummer opgevraagd. Je lidnummer is ' + str(lidnummer) + '.')
                inhoud.append('')
                inhoud.append('Met vrijzinnige groet,')
                inhoud.append('De Jonge Democraten.')
                inhoud = '\n'.join(inhoud)

                msg = EmailMessage(subject, inhoud, from_email=from_email, to=[email])
                msg.send()

            return HttpResponseRedirect('/lidnummerverzonden/')
    else:
        if getattr(settings, 'SKIP_RECAPTCHA', False):
            form = forms.HelpLidnummerForm()
        else:
            form = forms.HelpLidnummerRecaptchaForm()

    context = {'form': form, }
    context.update(csrf(request))

    return render_to_response("zues/lidnummer.html", context)

def lidnummer_verzonden(request):
    return render_to_response("zues/lidnummerverzonden.html")

def view_home(request):
    lid = check_login(request)
    if lid:
        context = {}
        context['lid'] = lid
        context['pm'] = models.PolitiekeMotie.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['apm'] = models.ActuelePolitiekeMotie.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['org'] = models.Organimo.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['res'] = models.Resolutie.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['am'] = models.Amendement.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['hr'] = models.HRWijziging.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['count'] = len(context['pm'])+len(context['apm'])+len(context['org'])+len(context['res'])+len(context['am'])+len(context['hr'])
        tijden = models.Tijden.get_solo()
        context['tijden'] = tijden
        context['magiets'] = tijden.mag_pm() or tijden.mag_apm() or tijden.mag_org() or tijden.mag_res() or tijden.mag_am() or tijden.mag_hr()
        context['staff'] = request.user.is_active and request.user.is_staff
        context['allpm'] = models.PolitiekeMotie.objects.filter(verwijderd=False).filter(publiek=True)
        context['allapm'] = models.ActuelePolitiekeMotie.objects.filter(verwijderd=False).filter(publiek=True)
        context['allorg'] = models.Organimo.objects.filter(verwijderd=False).filter(publiek=True)
        context['allres'] = models.Resolutie.objects.filter(verwijderd=False).filter(publiek=True)
        context['allam'] = models.Amendement.objects.filter(verwijderd=False).filter(publiek=True)
        context['allhr'] = models.HRWijziging.objects.filter(verwijderd=False).filter(publiek=True)
        context['allcount'] = len(context['allpm'])+len(context['allapm'])+len(context['allorg'])+len(context['allres'])+len(context['allam'])+len(context['allhr'])
        return render_to_response("zues/yolo.html", context)

    if request.method == 'POST': 
        if getattr(settings, 'SKIP_RECAPTCHA', False):
            form = forms.LidnummerForm(request.POST)
        else:
            form = forms.LidnummerRecaptchaForm(request.POST)
        if form.is_valid():
            lidnummer = form.cleaned_data['lidnummer']

            # opzoeken email
            result = generate_lid(int(lidnummer))
            if result != None:
                lid, to, naam, key = result

                secret_url = reverse('zues:login', kwargs={'key': key, 'lid': lid.lidnummer})
                secret_url = request.build_absolute_uri(secret_url)
                secret_url = re.sub(r'^http://', r'https://', secret_url)

                if getattr(settings, 'SKIP_EMAIL', False):
                    return HttpResponseRedirect(secret_url)

                subject = '[JD] Toegang \'' + str(settings.NAAMKORT) + '\' voorstelsysteem'
                from_email = 'noreply@jongedemocraten.nl'

                inhoud = []
                inhoud.append('Beste %s,' % naam)
                inhoud.append('')
                inhoud.append('Je hebt toegang gevraagd tot het voorstelsysteem \'' + str(settings.NAAMKORT) + '\' van de Jonge Democraten. ')
                inhoud.append('Dit systeem kun je gebruiken met de volgende persoonlijke geheime URL:')
                inhoud.append(secret_url)
                inhoud.append('')
                inhoud.append('Deze URL kun je ook gebruiken om jouw ingediende voorstellen in te zien, te wijzigen en terug te trekken. Deel deze URL dus niet met anderen!')
                inhoud.append('')
                inhoud.append('Mocht je een nieuwe URL aanvragen via de website, dan wordt de bovenstaande URL automatisch ongeldig.')
                inhoud.append('')
                inhoud.append('Met vrijzinnige groet,')
                inhoud.append('De Jonge Democraten.')
                inhoud = '\n'.join(inhoud)

                msg = EmailMessage(subject, inhoud, from_email=from_email, to=[to])
                msg.send()

            return HttpResponseRedirect('/loginverzonden/')
    else:
        if getattr(settings, 'SKIP_RECAPTCHA', False):
            form = forms.LidnummerForm()
        else:
            form = forms.LidnummerRecaptchaForm()

    context = {'form': form, }
    context.update(csrf(request))

    return render_to_response("zues/home.html", context)

def verzamel_op_boeknummer(voorstellen, stukken, default):
    for x in stukken:
        if len(x.boeknummer) > 0:
            i = x.boeknummer.rfind(' ')
            if i != -1:
                try:
                    grp = x.boeknummer[:i]
                    idx = int(x.boeknummer[i+1:])
                except ValueError:
                    grp = x.boeknummer
                    idx = ''
            else:
                grp = x.boeknummer
                idx = ''
        else:
            grp = default
            idx = "rest"
        if grp not in voorstellen: voorstellen[grp] = {}
        if idx not in voorstellen[grp]: voorstellen[grp][idx] = []
        voorstellen[grp][idx].append(x);

def geplet(s):
    keys = s.keys()
    keys.sort()
    res = []
    for k in keys: res = res + s[k]
    return res

@staff_member_required
def view_export(request):
    voorstellen = {}
    verzamel_op_boeknummer(voorstellen, models.PolitiekeMotie.objects.filter(verwijderd=False), "PM")
    verzamel_op_boeknummer(voorstellen, models.ActuelePolitiekeMotie.objects.filter(verwijderd=False), "APM")
    verzamel_op_boeknummer(voorstellen, models.Organimo.objects.filter(verwijderd=False), "ORG")
    verzamel_op_boeknummer(voorstellen, models.Resolutie.objects.filter(verwijderd=False), "RES")
    verzamel_op_boeknummer(voorstellen, models.Amendement.objects.filter(verwijderd=False), "AM")
    verzamel_op_boeknummer(voorstellen, models.HRWijziging.objects.filter(verwijderd=False), "HR")
    # oke, pletten en sorteren
    for k in voorstellen:
        voorstellen[k] = geplet(voorstellen[k])
    keys = voorstellen.keys()
    keys.sort()
    context = {'categories': keys, 'voorstellen': voorstellen}
    return render_to_response("zues/export.html", context)

@staff_member_required
def view_reorder(request):
    if request.method == 'POST':
        for k in request.POST:
            try:
                if k.startswith("PM-"):
                    o = models.PolitiekeMotie.objects.get(pk=int(k[3:]))
                elif k.startswith("APM-"):
                    o = models.ActuelePolitiekeMotie.objects.get(pk=int(k[4:]))
                elif k.startswith("ORG-"):
                    o = models.Organimo.objects.get(pk=int(k[4:]))
                elif k.startswith("RES-"):
                    o = models.Resolutie.objects.get(pk=int(k[4:]))
                elif k.startswith("AM-"):
                    o = models.Amendement.objects.get(pk=int(k[3:]))
                elif k.startswith("HR-"):
                    o = models.HRWijziging.objects.get(pk=int(k[3:]))
                o.boeknummer = request.POST[k]
                o.save()
            except ObjectDoesNotExist:
                pass # huh? whatever.
            
    voorstellen = {}
    verzamel_op_boeknummer(voorstellen, models.PolitiekeMotie.objects.filter(verwijderd=False), "PM")
    verzamel_op_boeknummer(voorstellen, models.ActuelePolitiekeMotie.objects.filter(verwijderd=False), "APM")
    verzamel_op_boeknummer(voorstellen, models.Organimo.objects.filter(verwijderd=False), "ORG")
    verzamel_op_boeknummer(voorstellen, models.Resolutie.objects.filter(verwijderd=False), "RES")
    verzamel_op_boeknummer(voorstellen, models.Amendement.objects.filter(verwijderd=False), "AM")
    verzamel_op_boeknummer(voorstellen, models.HRWijziging.objects.filter(verwijderd=False), "HR")
    # oke, pletten en sorteren
    for k in voorstellen:
        voorstellen[k] = geplet(voorstellen[k])
    keys = voorstellen.keys()
    keys.sort()
    context = {'categories': keys, 'voorstellen': voorstellen}
    return render_to_response("zues/reorder.html", context)

def login_verzonden(request):
    return render_to_response("zues/loginverzonden.html")

def login(request, lid, key):
    # controleer login
    hetlid = models.Login.objects.filter(lidnummer=lid).filter(secret=hashlib.sha256(key).hexdigest())
    if len(hetlid):
        request.session['lid'] = lid
        request.session['key'] = key
        return HttpResponseRedirect('/')
    return render_to_response("zues/loginfout.html")

def loguit(request):
    try:
        del request.session['lid']
        del request.session['key']
    except KeyError:
        pass
    # ook uitloggen bij admin
    logout(request)
    return HttpResponseRedirect('/')

class LidMixin(object):
    def get_context_data(self, **kwargs):
        context = super(LidMixin, self).get_context_data(**kwargs)
        if self.lid != None: context['lid'] = self.lid
        return context

    def dispatch(self, request, *args, **kwargs):
        self.lid = check_login(request)
        return super(LidMixin, self).dispatch(request, *args, **kwargs)

class LoginMixin(object):
    def get_context_data(self, **kwargs):
        context = super(LoginMixin, self).get_context_data(**kwargs)
        if self.lid != None: context['lid'] = self.lid
        return context

    def dispatch(self, request, *args, **kwargs):
        self.lid = check_login(request)
        if self.lid == None: return HttpResponseForbidden()
        return super(LoginMixin, self).dispatch(request, *args, **kwargs)

class EigenaarMixin(object):
    def get_object(self, **kwargs):
        obj = super(EigenaarMixin, self).get_object(**kwargs)
        if obj.eigenaar != self.lid: raise PermissionDenied()
        return obj

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(EigenaarMixin, self).dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden()

class MagPMMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not models.Tijden.get_solo().mag_pm(): return HttpResponseForbidden()
        else: return super(MagPMMixin, self).dispatch(request, *args, **kwargs)

class MagAPMMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not models.Tijden.get_solo().mag_apm(): return HttpResponseForbidden()
        else: return super(MagAPMMixin, self).dispatch(request, *args, **kwargs)

class MagORGMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not models.Tijden.get_solo().mag_org(): return HttpResponseForbidden()
        else: return super(MagORGMixin, self).dispatch(request, *args, **kwargs)

class MagRESMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not models.Tijden.get_solo().mag_res(): return HttpResponseForbidden()
        else: return super(MagRESMixin, self).dispatch(request, *args, **kwargs)

class MagAMMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not models.Tijden.get_solo().mag_am(): return HttpResponseForbidden()
        else: return super(MagAMMixin, self).dispatch(request, *args, **kwargs)

class MagHRMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not models.Tijden.get_solo().mag_hr(): return HttpResponseForbidden()
        else: return super(MagHRMixin, self).dispatch(request, *args, **kwargs)

class PMView(LidMixin, DetailView):
    template_name = 'zues/pm.html'
    context_object_name = "motie"
    model = models.PolitiekeMotie
    queryset = models.PolitiekeMotie.objects.filter(verwijderd=False)

    def get_object(self, **kwargs):
        obj = super(PMView, self).get_object(**kwargs)
        if self.kwargs['key'] != obj.secret:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(PMView, self).get_context_data(**kwargs)
        context['mag'] = models.Tijden.get_solo().mag_pm() and self.lid == context['motie'].eigenaar
        return context

class NieuwePM(LoginMixin, MagPMMixin, CreateView):
    model = models.PolitiekeMotie
    form_class = forms.PMForm
    template_name = 'zues/pmnew.html'

    def form_valid(self, form):
        if 'preview' not in self.request.POST:
            self.object = form.save(commit=False)
            return self.render_to_response(self.get_context_data(form=form, obj=self.object))
        else:
            self.object = form.save(commit=False)
            self.object.secret = base64.urlsafe_b64encode(os.urandom(30))
            self.object.eigenaar = models.Login.objects.filter(lidnummer=self.request.session['lid'])[0]
            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())

class WijzigPM(LoginMixin, EigenaarMixin, MagPMMixin, UpdateView):
    model = models.PolitiekeMotie
    form_class = forms.PMForm
    template_name = 'zues/pmnew.html'
    queryset = models.PolitiekeMotie.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigPM, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderPM(LoginMixin, EigenaarMixin, MagPMMixin, DeleteView):
    model = models.PolitiekeMotie
    template_name = 'zues/pmdel.html'
    queryset = models.PolitiekeMotie.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))

class APMView(LidMixin, DetailView):
    template_name = 'zues/apm.html'
    context_object_name = "motie"
    model = models.ActuelePolitiekeMotie
    queryset = models.ActuelePolitiekeMotie.objects.filter(verwijderd=False)

    def get_object(self, **kwargs):
        obj = super(APMView, self).get_object(**kwargs)
        if self.kwargs['key'] != obj.secret:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(APMView, self).get_context_data(**kwargs)
        context['mag'] = models.Tijden.get_solo().mag_apm() and self.lid == context['motie'].eigenaar
        return context

class NieuweAPM(LoginMixin, MagAPMMixin, CreateView):
    model = models.ActuelePolitiekeMotie
    form_class = forms.APMForm
    template_name = 'zues/apmnew.html'

    def form_valid(self, form):
        if 'preview' not in self.request.POST:
            self.object = form.save(commit=False)
            return self.render_to_response(self.get_context_data(form=form, obj=self.object))
        else:
            self.object = form.save(commit=False)
            self.object.secret = base64.urlsafe_b64encode(os.urandom(30))
            self.object.eigenaar = models.Login.objects.filter(lidnummer=self.request.session['lid'])[0]
            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())

class WijzigAPM(LoginMixin, EigenaarMixin, MagAPMMixin, UpdateView):
    model = models.ActuelePolitiekeMotie
    form_class = forms.APMForm
    template_name = 'zues/apmnew.html'
    queryset = models.ActuelePolitiekeMotie.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigAPM, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderAPM(LoginMixin, EigenaarMixin, MagAPMMixin, DeleteView):
    model = models.ActuelePolitiekeMotie
    template_name = 'zues/apmdel.html'
    queryset = models.ActuelePolitiekeMotie.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))

class ORGView(LidMixin, DetailView):
    template_name = 'zues/org.html'
    context_object_name = "motie"
    model = models.Organimo
    queryset = models.Organimo.objects.filter(verwijderd=False)

    def get_object(self, **kwargs):
        obj = super(ORGView, self).get_object(**kwargs)
        if self.kwargs['key'] != obj.secret:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(ORGView, self).get_context_data(**kwargs)
        context['mag'] = models.Tijden.get_solo().mag_org() and self.lid == context['motie'].eigenaar
        return context

class NieuweORG(LoginMixin, MagORGMixin, CreateView):
    model = models.Organimo
    form_class = forms.ORGForm
    template_name = 'zues/orgnew.html'

    def form_valid(self, form):
        if 'preview' not in self.request.POST:
            self.object = form.save(commit=False)
            return self.render_to_response(self.get_context_data(form=form, obj=self.object))
        else:
            self.object = form.save(commit=False)
            self.object.secret = base64.urlsafe_b64encode(os.urandom(30))
            self.object.eigenaar = models.Login.objects.filter(lidnummer=self.request.session['lid'])[0]
            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())

class WijzigORG(LoginMixin, EigenaarMixin, MagORGMixin, UpdateView):
    model = models.Organimo
    form_class = forms.ORGForm
    template_name = 'zues/orgnew.html'
    queryset = models.Organimo.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigORG, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderORG(LoginMixin, EigenaarMixin, MagORGMixin, DeleteView):
    model = models.Organimo
    template_name = 'zues/orgdel.html'
    queryset = models.Organimo.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))

class RESView(LidMixin, DetailView):
    template_name = 'zues/res.html'
    context_object_name = "voorstel"
    model = models.Resolutie
    queryset = models.Resolutie.objects.filter(verwijderd=False)

    def get_object(self, **kwargs):
        obj = super(RESView, self).get_object(**kwargs)
        if self.kwargs['key'] != obj.secret:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(RESView, self).get_context_data(**kwargs)
        context['mag'] = models.Tijden.get_solo().mag_res() and self.lid == context['voorstel'].eigenaar
        return context

class NieuweRES(LoginMixin, MagRESMixin, CreateView):
    model = models.Resolutie
    form_class = forms.RESForm
    template_name = 'zues/resnew.html'

    def form_valid(self, form):
        if 'preview' not in self.request.POST:
            self.object = form.save(commit=False)
            return self.render_to_response(self.get_context_data(form=form, obj=self.object))
        else:
            self.object = form.save(commit=False)
            self.object.secret = base64.urlsafe_b64encode(os.urandom(30))
            self.object.eigenaar = models.Login.objects.filter(lidnummer=self.request.session['lid'])[0]
            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())

class WijzigRES(LoginMixin, EigenaarMixin, MagRESMixin, UpdateView):
    model = models.Resolutie
    form_class = forms.RESForm
    template_name = 'zues/resnew.html'
    queryset = models.Resolutie.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigRES, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderRES(LoginMixin, EigenaarMixin, MagRESMixin, DeleteView):
    model = models.Resolutie
    template_name = 'zues/resdel.html'
    queryset = models.Resolutie.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))

class AMView(LidMixin, DetailView):
    template_name = 'zues/am.html'
    context_object_name = "voorstel"
    model = models.Amendement
    queryset = models.Amendement.objects.filter(verwijderd=False)

    def get_object(self, **kwargs):
        obj = super(AMView, self).get_object(**kwargs)
        if self.kwargs['key'] != obj.secret:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(AMView, self).get_context_data(**kwargs)
        context['mag'] = models.Tijden.get_solo().mag_am() and self.lid == context['voorstel'].eigenaar
        return context

class NieuweAM(LoginMixin, MagAMMixin, CreateView):
    model = models.Amendement
    form_class = forms.AMForm
    template_name = 'zues/amnew.html'

    def form_valid(self, form):
        if 'preview' not in self.request.POST:
            self.object = form.save(commit=False)
            return self.render_to_response(self.get_context_data(form=form, obj=self.object))
        else:
            self.object = form.save(commit=False)
            self.object.secret = base64.urlsafe_b64encode(os.urandom(30))
            self.object.eigenaar = models.Login.objects.filter(lidnummer=self.request.session['lid'])[0]
            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())

class WijzigAM(LoginMixin, EigenaarMixin, MagAMMixin, UpdateView):
    model = models.Amendement
    form_class = forms.AMForm
    template_name = 'zues/amnew.html'
    queryset = models.Amendement.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigAM, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderAM(LoginMixin, EigenaarMixin, MagAMMixin, DeleteView):
    model = models.Amendement
    template_name = 'zues/amdel.html'
    queryset = models.Amendement.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))

class HRView(LidMixin, DetailView):
    template_name = 'zues/hr.html'
    context_object_name = "voorstel"
    model = models.HRWijziging
    queryset = models.HRWijziging.objects.filter(verwijderd=False)

    def get_object(self, **kwargs):
        obj = super(HRView, self).get_object(**kwargs)
        if self.kwargs['key'] != obj.secret:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(HRView, self).get_context_data(**kwargs)
        context['mag'] = models.Tijden.get_solo().mag_hr() and self.lid == context['voorstel'].eigenaar
        return context

class NieuweHR(LoginMixin, MagHRMixin, CreateView):
    model = models.HRWijziging
    form_class = forms.HRForm
    template_name = 'zues/hrnew.html'

    def form_valid(self, form):
        if 'preview' not in self.request.POST:
            self.object = form.save(commit=False)
            return self.render_to_response(self.get_context_data(form=form, obj=self.object))
        else:
            self.object = form.save(commit=False)
            self.object.secret = base64.urlsafe_b64encode(os.urandom(30))
            self.object.eigenaar = models.Login.objects.filter(lidnummer=self.request.session['lid'])[0]
            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())

class WijzigHR(LoginMixin, EigenaarMixin, MagHRMixin, UpdateView):
    model = models.HRWijziging
    form_class = forms.HRForm
    template_name = 'zues/hrnew.html'
    queryset = models.HRWijziging.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigHR, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderHR(LoginMixin, EigenaarMixin, MagHRMixin, DeleteView):
    model = models.HRWijziging
    template_name = 'zues/hrdel.html'
    queryset = models.HRWijziging.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))

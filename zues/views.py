from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.sites.models import Site
from django.core.context_processors import csrf
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response
from django.views.generic import View, FormView, DetailView, UpdateView, DeleteView, CreateView
from zues import models
from zues import forms
import base64
import ldap
import os

def ldap_connect():
    l = ldap.initialize(settings.LDAP_NAME)
    try:
        l.simple_bind_s(settings.LDAP_DN, settings.LDAP_PASS)
    except ldap.LDAPError, e:
        print e
    return l

def retrieve_attributes(lidnummer):
    if getattr(settings, 'SKIP_LDAP', False):
        return '','Lid %d' % lidnummer

    l = ldap_connect()
    baseDN = "cn="+str(int(lidnummer))+",ou=users,dc=jd,dc=nl"
    try:
        ldap_result_id = l.search(baseDN, ldap.SCOPE_BASE)
        result_type, result_data = l.result(ldap_result_id, 1)
        if (result_data == []):
            return None
        else:
            if result_type == ldap.RES_SEARCH_RESULT:
                userDN, userAttrs = result_data[0]
                return userAttrs["mail"][0], userAttrs["sn"][0]
    except ldap.NO_SUCH_OBJECT:
        return None
    except ldap.LDAPError:
        return None

def retrieve_lidnummers(email):
    l = ldap_connect()
    baseDN = "ou=users,dc=jd,dc=nl"
    searchFilter = "(mail="+str(email)+")"

    try:
        ldap_result_id = l.search(baseDN, ldap.SCOPE_SUBTREE, searchFilter, None)
        while True:
            result_type, result_data = l.result(ldap_result_id, 1)
            if (result_data == []): return ()
            elif result_type == ldap.RES_SEARCH_RESULT:
                result = []
                for userDN, userAttrs in result_data:
                    result.append((userAttrs['cn'][0], userAttrs['sn'][0]))
                return tuple(result)
    except ldap.LDAPError:
        return ()

def get_lid(lidnummer):
    lid = models.Login.objects.filter(lidnummer=lidnummer)
    if len(lid):
        # lid bestaat al
        lid = lid[0]
    else:
        # lid bestaat nog njet
        code = base64.urlsafe_b64encode(os.urandom(32))
        lid = models.Login(lidnummer=lidnummer, secret=code)
        lid.save()

    res = retrieve_attributes(lidnummer)
    if res == None: return None

    email, naam = res
    return (lid, email, naam)

def check_login(request):
    if 'lid' not in request.session: return None
    if 'key' not in request.session: return None
    leden = models.Login.objects.filter(lidnummer=request.session['lid']).filter(secret=request.session['key'])
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

            for lidnummer, naam in retrieve_lidnummers(email):
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
        context['amres'] = models.AmendementRes.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['ampp'] = models.AmendementPP.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['count'] = len(context['pm'])+len(context['apm'])+len(context['org'])+len(context['res'])+len(context['amres'])+len(context['ampp'])
        tijden = models.Tijden.get_solo()
        context['tijden'] = tijden
        context['magiets'] = tijden.mag_pm() or tijden.mag_apm() or tijden.mag_org() or tijden.mag_res() or tijden.mag_amres() or tijden.mag_ampp()
        context['staff'] = request.user.is_active and request.user.is_staff
        context['allpm'] = models.PolitiekeMotie.objects.filter(verwijderd=False).filter(publiek=True)
        context['allapm'] = models.ActuelePolitiekeMotie.objects.filter(verwijderd=False).filter(publiek=True)
        context['allorg'] = models.Organimo.objects.filter(verwijderd=False).filter(publiek=True)
        context['allres'] = models.Resolutie.objects.filter(verwijderd=False).filter(publiek=True)
        context['allamres'] = models.AmendementRes.objects.filter(verwijderd=False).filter(publiek=True)
        context['allampp'] = models.AmendementPP.objects.filter(verwijderd=False).filter(publiek=True)
        context['allcount'] = len(context['allpm'])+len(context['allapm'])+len(context['allorg'])+len(context['allres'])+len(context['allamres'])+len(context['allampp'])
        return render_to_response("zues/yolo.html", context)

    if request.method == 'POST': 
        if getattr(settings, 'SKIP_RECAPTCHA', False):
            form = forms.LidnummerForm(request.POST)
        else:
            form = forms.LidnummerRecaptchaForm(request.POST)
        if form.is_valid():
            lidnummer = form.cleaned_data['lidnummer']

            # opzoeken email
            result = get_lid(int(lidnummer))
            if result != None:
                lid, to, naam = result

                if getattr(settings, 'SKIP_EMAIL', False):
                    return HttpResponseRedirect(lid.get_secret_url())

                subject = '[JD] Toegang voorstelsysteem'
                from_email = 'noreply@jongedemocraten.nl'

                inhoud = []
                inhoud.append('Beste %s,' % naam)
                inhoud.append('')
                inhoud.append('Om het voorstelsysteem van de Jonge Democraten te gebruiken, gebruik de volgende persoonlijke geheime URL:')
                inhoud.append(request.build_absolute_uri(lid.get_secret_url()))
                inhoud.append('')
                inhoud.append('Deze URL kun je ook gebruiken om jouw ingediende voorstellen in te zien, te wijzigen en terug te trekken. Deel deze URL dus niet met anderen!')
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

@staff_member_required
def view_export(request):
    context = {}
    context['pm'] = models.PolitiekeMotie.objects.filter(verwijderd=False)
    context['apm'] = models.ActuelePolitiekeMotie.objects.filter(verwijderd=False)
    context['org'] = models.Organimo.objects.filter(verwijderd=False)
    context['res'] = models.Resolutie.objects.filter(verwijderd=False)
    context['amres'] = models.AmendementRes.objects.filter(verwijderd=False)
    context['ampp'] = models.AmendementPP.objects.filter(verwijderd=False)
    return render_to_response("zues/export.html", context)

def login_verzonden(request):
    return render_to_response("zues/loginverzonden.html")

def login(request, lid, key):
    # controleer login
    hetlid = models.Login.objects.filter(lidnummer=lid)
    if len(hetlid):
        if hetlid[0].secret == key:
            request.session['lid'] = lid
            request.session['key'] = key
            return HttpResponseRedirect('/')
    raise Http404

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
        if self.lid == None: raise Http404
        return super(LoginMixin, self).dispatch(request, *args, **kwargs)

class EigenaarMixin(object):
    def get_object(self, **kwargs):
        obj = super(EigenaarMixin, self).get_object(**kwargs)
        if obj.eigenaar != self.lid: raise Http404
        return obj

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

class MagAMRESMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not models.Tijden.get_solo().mag_amres(): return HttpResponseForbidden()
        else: return super(MagAMRESMixin, self).dispatch(request, *args, **kwargs)

class MagAMPPMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not models.Tijden.get_solo().mag_ampp(): return HttpResponseForbidden()
        else: return super(MagAMPPMixin, self).dispatch(request, *args, **kwargs)

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

class AMRESView(LidMixin, DetailView):
    template_name = 'zues/amres.html'
    context_object_name = "voorstel"
    model = models.AmendementRes
    queryset = models.AmendementRes.objects.filter(verwijderd=False)

    def get_object(self, **kwargs):
        obj = super(AMRESView, self).get_object(**kwargs)
        if self.kwargs['key'] != obj.secret:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(AMRESView, self).get_context_data(**kwargs)
        context['mag'] = models.Tijden.get_solo().mag_amres() and self.lid == context['voorstel'].eigenaar
        return context

class NieuweAMRES(LoginMixin, MagAMRESMixin, CreateView):
    model = models.AmendementRes
    form_class = forms.AMRESForm
    template_name = 'zues/amresnew.html'

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

class WijzigAMRES(LoginMixin, EigenaarMixin, MagAMRESMixin, UpdateView):
    model = models.AmendementRes
    form_class = forms.AMRESForm
    template_name = 'zues/amresnew.html'
    queryset = models.AmendementRes.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigAMRES, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderAMRES(LoginMixin, EigenaarMixin, MagAMRESMixin, DeleteView):
    model = models.AmendementRes
    template_name = 'zues/amresdel.html'
    queryset = models.AmendementRes.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))

class AMPPView(LidMixin, DetailView):
    template_name = 'zues/ampp.html'
    context_object_name = "voorstel"
    model = models.AmendementPP
    queryset = models.AmendementPP.objects.filter(verwijderd=False)

    def get_object(self, **kwargs):
        obj = super(AMPPView, self).get_object(**kwargs)
        if self.kwargs['key'] != obj.secret:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super(AMPPView, self).get_context_data(**kwargs)
        context['mag'] = models.Tijden.get_solo().mag_ampp() and self.lid == context['voorstel'].eigenaar
        return context

class NieuweAMPP(LoginMixin, MagAMPPMixin, CreateView):
    model = models.AmendementPP
    form_class = forms.AMPPForm
    template_name = 'zues/amppnew.html'

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

class WijzigAMPP(LoginMixin, EigenaarMixin, MagAMPPMixin, UpdateView):
    model = models.AmendementPP
    form_class = forms.AMPPForm
    template_name = 'zues/amppnew.html'
    queryset = models.AmendementPP.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigAMPP, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderAMPP(LoginMixin, EigenaarMixin, MagAMPPMixin, DeleteView):
    model = models.AmendementPP
    template_name = 'zues/amppdel.html'
    queryset = models.AmendementPP.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))



from django.conf import settings
from django.contrib.sites.models import Site
from django.core.context_processors import csrf
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
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
    l = ldap_connect()
    baseDN = "cn="+str(int(lidnummer))+",ou=users,dc=jd,dc=nl"
    retrieveAttributes = None
    try:
        ldap_result_id = l.search(baseDN, ldap.SCOPE_BASE)
        result_type, result_data = l.result(ldap_result_id, 1)
        if (result_data == []):
            return None
        else:
            if result_type == ldap.RES_SEARCH_RESULT:
                userDN, userAttrs = result_data[0]
                return userAttrs["mail"][0], userAttrs["sn"][0]
    except ldap.NO_SUCH_OBJECT, e:
        return None
    except ldap.LDAPError, e:
        pass

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

def view_home(request):
    lid = check_login(request)
    if lid:
        context = {}
        context['lid'] = lid
        context['pm'] = models.PolitiekeMotie.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['apm'] = models.ActuelePolitiekeMotie.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['org'] = models.Organimo.objects.filter(eigenaar=lid).filter(verwijderd=False)
        context['count'] = len(context['pm'])+len(context['apm'])+len(context['org'])
        return render_to_response("zues/yolo.html", context)

    if request.method == 'POST': 
        form = forms.LidnummerForm(request.POST)
        if form.is_valid():
            lidnummer = form.cleaned_data['lidnummer']

            # opzoeken email
            result = get_lid(int(lidnummer))
            if result != None:
                lid, to, naam = result
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
        form = forms.LidnummerForm()

    context = {'form': form}
    context.update(csrf(request))

    return render_to_response("zues/home.html", context)

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

class NieuwePM(LoginMixin, CreateView):
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

class WijzigPM(LoginMixin, UpdateView):
    model = models.PolitiekeMotie
    form_class = forms.PMForm
    template_name = 'zues/pmnew.html'
    queryset = models.PolitiekeMotie.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigPM, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderPM(LoginMixin, DeleteView):
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

class NieuweAPM(LoginMixin, CreateView):
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

class WijzigAPM(LoginMixin, UpdateView):
    model = models.ActuelePolitiekeMotie
    form_class = forms.APMForm
    template_name = 'zues/apmnew.html'
    queryset = models.ActuelePolitiekeMotie.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigAPM, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderAPM(LoginMixin, DeleteView):
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

class NieuweORG(LoginMixin, CreateView):
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

class WijzigORG(LoginMixin, UpdateView):
    model = models.Organimo
    form_class = forms.ORGForm
    template_name = 'zues/orgnew.html'
    queryset = models.Organimo.objects.filter(verwijderd=False)

    def get_context_data(self, **kwargs):
        context = super(WijzigORG, self).get_context_data(**kwargs)
        context['edit'] = 1
        return context

class VerwijderORG(LoginMixin, DeleteView):
    model = models.Organimo
    template_name = 'zues/orgdel.html'
    queryset = models.Organimo.objects.filter(verwijderd=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.verwijderd = True
        self.object.save()
        return HttpResponseRedirect(reverse_lazy("zues:home"))


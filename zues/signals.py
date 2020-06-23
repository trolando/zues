from django.contrib.auth.signals import user_logged_in
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMessage
import re


def on_user_login(sender, user, request, **kwargs):
    from janeus import Janeus
    from zues import models
    from zues import views

    if not hasattr(settings, 'JANEUS_SERVER'):
        return

    username = user.get_username()
    res = Janeus().by_uid(username)
    if res is None:
        return

    dn, attrs = res

    lidnummer = int(attrs['cn'][0].decode('utf-8'))
    email = attrs['mail'][0].decode('utf-8')
    naam = attrs['sn'][0].decode('utf-8')

    lid = models.Login.objects.filter(lidnummer=lidnummer)
    if len(lid) == 0:
        lid, to, naam, key = views._generate_lid(lidnummer, email, naam)
        if getattr(settings, 'EMAIL_HOST', '') != '':
            secret_url = reverse('zues:login', kwargs={'key': key, 'lid': lid.lidnummer})
            secret_url = request.build_absolute_uri(secret_url)
            secret_url = re.sub(r'^http://', r'https://', secret_url)
            subject = '[JD] Toegang voorstelsysteem {}'.format(request.get_host().lower())
            from_email = 'noreply@jongedemocraten.nl'
            inhoud = []
            inhoud.append('Beste %s,' % naam)
            inhoud.append('')
            inhoud.append('Als beheerder van het voorstelsysteem van de Jonge Democraten heb je ook automatisch een account voor de normale interface. Als je de site wilt gebruiken als gewone gebruiker (dus niet als beheerder), dan kun je de volgende persoonlijke geheime URL gebruiken:')
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
    else:
        lid = lid[0]

    request.session['lid'] = lidnummer
    request.session['key'] = lid.secret

user_logged_in.connect(on_user_login)

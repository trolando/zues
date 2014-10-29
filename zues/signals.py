from django.contrib.auth.signals import user_logged_in

def on_user_login(sender, user, request, **kwargs):
    from zues import jdldap
    from zues import models
    from zues import views
    username = user.get_username()
    with jdldap._connection() as l:
        res = jdldap._dn_from_uid(l, username)
        if res == None: return
        dn, attrs = res

    lidnummer = int(attrs['cn'][0])
    email = attrs['mail'][0]
    naam = attrs['sn'][0]

    lid = models.Login.objects.filter(lidnummer=lidnummer)
    if len(lid) == 0: lid, to, naam, key = views._generate_lid(lidnummer, email, naam)
    else: lid = lid[0]

    request.session['lid'] = lidnummer
    request.session['key'] = lid.secret

user_logged_in.connect(on_user_login)

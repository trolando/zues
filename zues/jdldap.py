from contextlib import contextmanager
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
import ldap
from ldap.filter import filter_format
from zues.ldappool import LDAPPool

import logging
logger = logging.getLogger(__name__)

@contextmanager
def _connection():
    with LDAPPool().connection(settings.LDAP_NAME, settings.LDAP_DN, settings.LDAP_PASS) as conn:
        yield conn

def attributes(lidnummer):
    """Vraag emailadres en naam van lid met lidnummer op.

    Voorbeeld:
    res = attributes(lidnummer)
    if res != None:
        email, naam = res
    """
    try:
        with _connection() as l:
            baseDN = "cn="+str(int(lidnummer))+",ou=users,dc=jd,dc=nl"
            result_data = l.search_st(baseDN, ldap.SCOPE_BASE, timeout=1)
            if len(result_data) == 1:
                dn, attrs = result_data[0]
                return attrs['mail'][0], attrs['sn'][0]
    except ldap.NO_SUCH_OBJECT:
        pass
    except ldap.INVALID_CREDENTIALS:
        pass
    except ldap.LDAPError:
        pass
    return None

def lidnummers(email):
    """Genereert alle lidnummers die bij een emailadres horen.

    Voorbeeld:
    for lidnummer in lidnummers('email@adr.es'):
        ...
    """
    try:
        with _connection() as l:
            baseDN = "ou=users,dc=jd,dc=nl"
            searchFilter = filter_format('(mail=%s)', (str(email),))
            for dn, attrs in l.search_st(baseDN, ldap.SCOPE_ONELEVEL, searchFilter, timeout=3):
                yield int(attrs['cn'][0]), attrs['sn'][0]
    except ldap.INVALID_CREDENTIALS:
        pass
    except ldap.LDAPError:
        pass

def _groups_of_dn(conn, dn):
    """Generator van alle groepen (dn) waarvan de gebruiker lid is"""
    baseDN = "ou=groups,dc=jd,dc=nl"
    searchFilter = filter_format('(&(objectClass=groupOfNames)(member=%s))',(str(dn),))
    result_data = conn.search_st(baseDN, ldap.SCOPE_SUBTREE, searchFilter, timeout=3)
    for dn, attrs in result_data: yield attrs['cn'][0]

def _dn_from_uid(conn, uid):
    """Opvragen (dn, attrs) van gebruiker met uid, of geeft None terug als niet uniek gevonden"""
    baseDN = "ou=users,dc=jd,dc=nl"
    searchFilter = filter_format('(uid=%s)', (str(uid),))
    result_data = conn.search_st(baseDN, ldap.SCOPE_ONELEVEL, searchFilter, timeout=1)
    if len(result_data) != 1: return None
    dn, attrs = result_data[0]
    return dn, attrs
           
def _test_login(dn, password):
    """Probeert in te loggen met dn+password, True/False indien gelukt/mislukt"""
    try:
        testconn = ldap.initialize(settings.LDAP_NAME)
        testconn.simple_bind_s(dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        pass
    except ldap.LDAPError:
        pass
    return False

def chpwd(uid, old, new):
    try:
        with _connection() as l:
            dn, attrs = _dn_from_uid(l, uid)
        testconn = ldap.initialize(settings.LDAP_NAME)
        testconn.simple_bind_s(dn, old)
        return testconn.passwd_s(dn, old, new)
    except ldap.INVALID_CREDENTIALS:
        pass
    except ldap.LDAPError:
        pass
    return None

class MijnJDBackend(object):
    def authenticate(self, username=None, password=None):
        logger.info("Trying to authenticate %s" % (username,))
        try:
            with _connection() as l:
                # get dn of user
                res = _dn_from_uid(l, username)
                if res == None: return None
                dn, attrs = res

                # ok we have dn, try to login
                if not _test_login(dn, password): return None

                # ok login works, get groups
                groups = [g for g in _groups_of_dn(l, dn)]
        except ldap.INVALID_CREDENTIALS:
            return None
        except ldap.LDAPError:
            return None
            
        if not settings.LDAP_AUTH(username, groups): return None

        model = get_user_model()
        username_field = getattr(model, 'USERNAME_FIELD', 'username')

        kwargs = {
            username_field + '__iexact': username,
            'defaults': {username_field: username.lower()}
        }

        user, created = model.objects.get_or_create(**kwargs)

        if created:
            logger.debug("Created Django user %s", username)
            user.set_unusable_password()

        setattr(user, 'last_name', attrs['sn'][0]);
        setattr(user, 'email', attrs['mail'][0]);
        setattr(user, 'is_active', True)
        setattr(user, 'is_staff', True)

        for p in Permission.objects.filter(settings.LDAP_AUTH_PERMISSIONS(username, groups)):
            user.user_permissions.add(p)

        user.save()
        return user
           
    def get_user(self, user_id):
        user = None

        try:
            user = get_user_model().objects.get(pk=user_id)
        except ObjectDoesNotExist:
            pass

        return user


from contextlib import contextmanager
from django.conf import settings
import ldap
from ldap.filter import filter_format
from zues.ldappool import LDAPPool

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
            result_data = l.search_st(baseDN, ldap.SCOPE_BASE, attrlist=['sn','mail'], timeout=1)
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
            for dn, attrs in l.search_st(baseDN, ldap.SCOPE_ONELEVEL, searchFilter, ['cn','sn'], timeout=3):
                yield int(attrs['cn'][0]), attrs['sn'][0]
    except ldap.INVALID_CREDENTIALS:
        pass
    except ldap.LDAPError:
        pass

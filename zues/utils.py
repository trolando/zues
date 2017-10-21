""" Copyright Mezzanine """

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager as DjangoCSM
from django.conf import settings
import logging
import threading


_thread_local = threading.local()
logger = logging.getLogger(__name__)


def current_request():
    return getattr(_thread_local, "request", None)


class CurrentRequestMiddleware(object):
    def process_request(self, request):
        _thread_local.request = request

        site_id = request.session.get("site_id", None)
        site = None

        if site_id is not None:
            try:
                site = Site.objects.get(id=site_id)
            except Site.DoesNotExist:
                site = None
                site_id = None

        if not site_id:
            domain = request.get_host().lower()

            try:
                site = Site.objects.get(domain__iexact=domain)
                site_id = site.id
            except Site.DoesNotExist:
                site = Site(domain=domain, name=domain)
                site.save()

            site_id = site.id

        _thread_local.site_id = site_id
        _thread_local.site = site

        import django.contrib.sites.shortcuts
        django.contrib.sites.shortcuts.get_current_site = lambda request: site


def set_current_site_id(site_id):
    _thread_local.site_id = site_id
    _thread_local.site = Site.objects.get(id=site_id)


def current_site_id():
    site_id = getattr(_thread_local, 'site_id', None)
    if site_id is None:
        logger.error('current_site_id: no site_id set in thread local')
        return getattr(settings, 'SITE_ID', None)
    return site_id


def current_site():
    site = getattr(_thread_local, 'site', None)
    if site is None:
        logger.error('current_site: no site set in thread local')
        return None
    return site


class CurrentSiteManager(DjangoCSM):
    def get_queryset(self):
        logger.warning("current site id = {}".format(current_site_id()))
        return super(DjangoCSM, self).get_queryset().filter(site__id=current_site_id())

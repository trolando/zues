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
        if not site_id:
            domain = request.get_host().lower()

            try:
                site = Site.objects.get(domain__iexact=domain)
            except Site.DoesNotExist:
                site = Site(domain=domain, name=domain)
                site.save()
                site_id = site.id
            else:
                site_id = site.id

        request.site_id = site_id
        request.site = site

        import django.contrib.sites.shortcuts
        django.contrib.sites.shortcuts.get_current_site = lambda request: request.site


def current_site_id():
    request = current_request()
    if request is None:
        logger.warning('current_site_id: current_request returned None!')
        return getattr(settings, 'SITE_ID', None)
    return getattr(request, 'site_id', None)


class CurrentSiteManager(DjangoCSM):
    def __init__(self, field_name=None, *args, **kwargs):
        super(DjangoCSM, self).__init__(*args, **kwargs)
        self.__field_name = field_name
        self.__is_validated = False

    def get_queryset(self):
        if not self.__is_validated:
            self._get_field_name()
        lookup = {self.__field_name + "__id__exact": current_site_id()}
        return super(DjangoCSM, self).get_queryset().filter(**lookup)

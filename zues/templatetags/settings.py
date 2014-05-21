from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()
@register.simple_tag
def mededeling():
    if hasattr(settings, 'MEDEDELING'): return mark_safe(settings.MEDEDELING)
    else: return ""

from django import template
from django.conf import settings

register = template.Library()

# https://stackoverflow.com/a/7716141
@register.simple_tag
def settings_value(name):
    """Usage: {% settings_value 'KEY' %} """
    return getattr(settings, name, "")

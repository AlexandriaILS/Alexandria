"""
Django's default `truncatechars` filter ends strings with a single character
ellipsis: `…`. While this looks nice, the receipt printer barfs on it.

So the answer apparently is to re-implement the same functionality, just
replacing the single-character ending with the three-character version so that
it prints correctly.
"""

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.text import Truncator

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def truncatecharswithellipsis(value, arg) -> str:
    """Truncate a string after `arg` number of characters."""
    try:
        length = int(arg)
    except ValueError:  # Invalid literal for int().
        return value  # Fail silently.
    return Truncator(value).chars(length, truncate="...")

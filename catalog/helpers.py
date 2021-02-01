from typing import Dict

from django.conf import settings


def build_context(data: Dict = None) -> Dict:
    """Prepare everything that needs to be passed to the templates on every request."""
    if not data:
        data = {}
    data.update({'SITE_NAME': settings.SITE_NAME})

    return data

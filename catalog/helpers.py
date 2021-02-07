from typing import Dict

from django.conf import settings


def build_context(data: Dict = None) -> Dict:
    """Prepare everything that needs to be passed to the templates on every request."""
    if not data:
        data = {}
    data.update({"LIBRARY_SYSTEM_NAME": settings.LIBRARY_SYSTEM_NAME})

    return data

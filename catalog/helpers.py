from typing import Dict

from django.conf import settings
from django.utils.translation import ugettext as _


def build_context(data: Dict = None) -> Dict:
    """Prepare everything that needs to be passed to the templates on every request."""
    if not data:
        data = {}
    data.update(
        {
            "LIBRARY_SYSTEM_NAME": settings.LIBRARY_SYSTEM_NAME,
            "messages": {
                "hold_success_message": _("Hold placed for {}!"),
                "hold_error_message": _("Something went wrong — please try again."),
            }
        }
    )

    return data

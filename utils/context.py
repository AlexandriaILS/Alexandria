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
            "LIBRARY_SYSTEM_URL": settings.LIBRARY_SYSTEM_URL,
            "alerts": {
                "hold_success_message": _("Hold placed for (itemType) — (itemTitle)! You're number (holdNum) in queue!"),
                "hold_error_message": _("Something went wrong — please try again."),
                "hold_duplicate": _("You already have a hold on this item."),
            },
            "name_keys": {"item_type_name": "(itemType)", "item_title": "(itemTitle)", "hold_number": "(holdNum)"},
        }
    )

    return data

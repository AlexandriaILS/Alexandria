from typing import Dict

from django.conf import settings
from django.utils.translation import ugettext as _


def build_context(data: Dict = None, request=None) -> Dict:
    """Prepare everything that needs to be passed to the templates on every request."""
    if not data:
        data = {}
    data.update(
        {
            "alerts": {
                "hold_success_message": _(
                    "Hold placed for (itemType) — (itemTitle)! You're number (holdNum) in queue!"
                ),
                "hold_error_message": _("Something went wrong — please try again."),
                "hold_duplicate": _("You already have a hold on this item."),
                "not_logged_in": _("You're not logged in! You'll need to log in before you can put items on hold."),
                # used to replace placeholders in the messages with values returned from the views
                "name_keys": {
                    "item_type_name": "(itemType)",
                    "item_title": "(itemTitle)",
                    "hold_number": "(holdNum)",
                },
            },
            "current_hash": settings.CURRENT_HASH,
            "branches": request.user.get_serializable_branches() if request else [],
        }
    )

    return data

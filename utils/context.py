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
                # Anything in parentheses is replaced using code in holdbuttons.js
                "hold_success_message": _(
                    "Hold placed for (itemType) — (itemTitle)! You're number (holdNum) in queue!"
                ),
                "hold_error_message": _("Something went wrong — please try again."),
                "hold_duplicate": _("You already have a hold on this item."),
                "not_logged_in": _("You're not logged in! You'll need to log in before you can put items on hold."),
                "quickhold_success_message": _("Hold placed for (itemTitle) for pickup at (branchName)!"),
            },
            "current_hash": settings.CURRENT_HASH,
            "branches": request.user.get_serializable_branches() if request else [],
        }
    )

    return data

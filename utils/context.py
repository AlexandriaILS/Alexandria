from typing import Dict

from django.conf import settings
from django.utils.translation import ugettext as _


def build_context(data: Dict = None, request=None) -> Dict:
    """Prepare everything that needs to be passed to the templates on every request."""
    if not data:
        data = {}

    if request and request.user.is_authenticated:
        branches = request.user.get_serializable_branches()
    else:
        branches = []

    data.update(
        {
            "alerts": {
                # Anything in parentheses is replaced using code in holdbuttons.js
                "hold_success_message": _(
                    "Hold placed for (itemType) — (itemTitle)! You're number (holdNum) in queue!"
                ),
                "hold_insufficient_permissions": _("Sorry, but you can't change this hold."),
                "already_checked_out": _(
                    "You can't put a hold on something you already have checked out."
                ),
                "general_error_message": _("Something went wrong — please try again."),
                "hold_duplicate": _("You already have a hold on this item."),
                "renew_success_message": _(
                    'Item successfully renewed!'
                ),
                "not_logged_in": _(
                    "You're not logged in! You'll need to log in before you can put items on hold."
                ),
                "quickhold_success_message": _(
                    "Hold placed for (itemTitle) for pickup at (branchName)!"
                ),
            },
            "current_hash": settings.CURRENT_HASH,
            "branches": branches,
        }
    )

    return data

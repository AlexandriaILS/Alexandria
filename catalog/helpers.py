from typing import Dict

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import ugettext as _


def build_context(data: Dict = None) -> Dict:
    """Prepare everything that needs to be passed to the templates on every request."""
    if not data:
        data = {}
    data.update(
        {
            "LIBRARY_SYSTEM_NAME": settings.LIBRARY_SYSTEM_NAME,
            "messages": {
                "hold_success_message": _("Hold placed for (itemType) — (itemTitle)!"),
                "hold_error_message": _("Something went wrong — please try again."),
                "hold_duplicate": _("You already have a hold on this item."),
            },
            "name_keys": {"item_type_name": "(itemType)", "item_title": "(itemTitle)"},
        }
    )

    return data


def get_results_per_page(request: WSGIRequest) -> int:
    try:
        results_per_page = int(
            request.GET.get("count", settings.DEFAULT_RESULTS_PER_PAGE)
        )
        if results_per_page < 1:
            # accidentally fell over this while testing
            return settings.DEFAULT_RESULTS_PER_PAGE
        else:
            return results_per_page
    except ValueError:
        return settings.DEFAULT_RESULTS_PER_PAGE

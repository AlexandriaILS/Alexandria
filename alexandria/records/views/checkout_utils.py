from django.http import JsonResponse
from django.utils.translation import gettext as _


class Toasts:
    MISSING_ITEM_ID = _("Missing item ID... please try again.")
    NO_ITEM_FOUND = _("No item found with that ID.")
    ITEM_ALREADY_PRESENT = _("That item is already in the list.")
    NO_ACTIVE_CHECKOUT_SESSION = _(
        "There is no checkout session currently active." " Please refresh the page."
    )
    EXPIRED_CHECKOUT_SESSION = _(
        "The checkout session has expired. Please refresh the page."
    )


def create_toast(toast_message: str, status=400) -> JsonResponse:
    return JsonResponse(data={"message": toast_message}, status=status)

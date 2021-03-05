from io import BytesIO
from typing import Dict
from uuid import uuid4
import os

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import ugettext as _
import requests
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage


def build_context(data: Dict = None) -> Dict:
    """Prepare everything that needs to be passed to the templates on every request."""
    if not data:
        data = {}
    data.update(
        {
            "LIBRARY_SYSTEM_NAME": settings.LIBRARY_SYSTEM_NAME,
            "alerts": {
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


def get_and_save_image(url: str, item):
    # `item` should be either a Record or an Item instance.
    # Returns the record that was passed in.
    result = requests.get(url)
    result.raise_for_status()
    pic = BytesIO(result.content)
    if pic.seek(0, 2) < 2000:
        # sometimes we get single pixel images, which is definitely not what we want.
        # If that happens, discard the result.
        # The single-pixel image that I received in testing has a length of 807, and
        # a valid image las a length around 19,500. 2000 seems like a wild guess, but
        # we'll run with that until it causes issues.
        return

    pic.seek(0)
    filename = default_storage.save(f"{item.id}-{uuid4()}.jpg", ContentFile(pic.read()))
    path = os.path.join(settings.MEDIA_ROOT, filename)
    item.image = ImageFile(open(path, "rb"))
    item.image.name = filename
    default_storage.delete(filename)

    return item

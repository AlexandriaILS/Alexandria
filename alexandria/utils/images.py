import logging
import os
from io import BytesIO
from typing import Any
from uuid import uuid4

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage

# from django_lightweight_queue import task

logger = logging.getLogger(__name__)


# @task()
def get_and_save_image(url: str, item_id: int = None, record_id: int = None) -> Any:
    from alexandria.records.models import Item, Record

    target = (
        Item.objects.filter(id=item_id).first()
        or Record.objects.filter(id=record_id).first()
    )
    if not target:
        return
    logger.info(f"Getting image for {target}, url {url}")
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
    filename = default_storage.save(
        f"{target.id}-{uuid4()}.jpg", ContentFile(pic.read())
    )
    path = os.path.join(settings.MEDIA_ROOT, filename)
    target.image = ImageFile(open(path, "rb"))
    target.image.name = filename
    target.save()
    default_storage.delete(filename)

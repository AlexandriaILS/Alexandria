import os
from io import BytesIO
from random import choice
from typing import Any, Union, TYPE_CHECKING

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage

if TYPE_CHECKING:
    from catalog.models import Item, Record


# Book Documentation https://openlibrary.org/dev/docs/api/books


def download_cover(item: Union["Item", "Record"], size: str = "M") -> None:
    # https://openlibrary.org/dev/docs/api/covers
    if item.image != "":
        # Django stores null images as empty strings, so if it's not an
        # empty string then there's already an image here. Jettison
        # early so that we don't make a call to openlibrary that we don't
        # have to make.
        return

    if not hasattr(item, "isbn"):
        # Records don't have ISBNs because those are stored on the items
        # that are under the records. However, records can still have a
        # cover image, so we'll grab an item from under the record and
        # steal the ISBN from that. There's also the possibility that any
        # given item won't actually have an ISBN but another might, so let's
        # grab all the ISBNs that we have available and nab one at random.
        isbn = choice([el.isbn for el in item.item_set.all() if el.isbn is not None])
        title = item.title
    else:
        isbn = item.isbn
        title = item.record.title

    URL = "http://covers.openlibrary.org/b/isbn/{value}-{size}.jpg"
    if size not in ["S", "M", "L"]:
        raise Exception("Can only request sizes in 'S', 'M', or 'L'.")
    result = requests.get(URL.format(value=isbn, size=size))
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
        f"{item.id}-{title}-cover.jpg", ContentFile(pic.read())
    )
    path = os.path.join(settings.MEDIA_ROOT, filename)
    item.image = ImageFile(open(path, "rb"))
    item.image.name = filename
    default_storage.delete(filename)


def get_by_isbn(isbn: str) -> str:
    ...


def get_openlibrary_book(isbn: str) -> Any:
    result = requests.get("https://openlibrary.org/isbn/9780140328721.json").json()

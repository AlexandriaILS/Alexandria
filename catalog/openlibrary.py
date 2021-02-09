from typing import Any, Union
from io import BytesIO
import os
from random import choice

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.conf import settings
import requests

from catalog.models import Item, Record

# Book Documentation https://openlibrary.org/dev/docs/api/books

def download_cover(item: Union[Item, Record], size: str="M") -> None:
    # https://openlibrary.org/dev/docs/api/covers
    if isinstance(item, Record):
        # Records don't have ISBNs because those are stored on the items
        # that are under the records. However, records can still have a
        # cover image, so we'll grab an item from under the record and
        # steal the ISBN from that. There's also the possibility that any
        # given item won't actually have an ISBN but another might, so let's
        # grab all the ISBNs that we have available and nab one at random.
        isbn = choice([el.isbn for el in item.item_set.all() if el.isbn is not None])
    else:
        isbn = item.isbn

    URL = "http://covers.openlibrary.org/b/isbn/{value}-{size}.jpg"
    if size not in ["S", "M", "L"]:
        raise Exception("Can only request sizes in 'S', 'M', or 'L'.")
    result = requests.get(URL.format(value=isbn, size=size))
    result.raise_for_status()
    pic = BytesIO(result.content)
    pic.seek(0)
    filename = default_storage.save(
        f"{item.id}-cover.jpg", ContentFile(pic.read())
    )
    path = os.path.join(settings.MEDIA_ROOT, filename)
    item.image = ImageFile(open(path, "rb"))
    item.image.name = filename
    item.save()


def get_by_isbn(isbn: str) -> str:
    ...


def get_openlibrary_book(isbn: str) -> Any:
    result = requests.get("https://openlibrary.org/isbn/9780140328721.json").json()


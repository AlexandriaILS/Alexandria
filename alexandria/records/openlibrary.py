from random import choice
from typing import TYPE_CHECKING, Any, Dict, Union

import requests

from alexandria.utils import get_and_save_image

if TYPE_CHECKING:
    from alexandria.records.models import Item, Record


# Book Documentation https://openlibrary.org/dev/docs/api/books


def download_cover(item: Union["Item", "Record"], size: str = "M") -> None:
    """
    This function is called by the `save` function on Records and Items.
    """
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
        try:
            isbn = choice(
                [el.isbn for el in item.item_set.all() if el.isbn is not None]
            )
        except IndexError:
            return
    else:
        isbn = item.isbn

    URL = "http://covers.openlibrary.org/b/isbn/{value}-{size}.jpg"
    if size not in ["S", "M", "L"]:
        raise Exception("Can only request sizes in 'S', 'M', or 'L'.")

    get_and_save_image(URL.format(value=isbn, size=size), item)


def get_by_isbn(isbn: str) -> Dict:
    return requests.get(
        f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json"
    ).json()


def get_openlibrary_book(isbn: str) -> Any:
    # TODO: finish
    result = requests.get("https://openlibrary.org/isbn/9780140328721.json").json()

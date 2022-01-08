import unicodedata
import string
from typing import Union


def clean_text(text: str) -> Union[str, None]:
    """
    Reduces text to bare ASCII with no punctuation for searching.

    Abstracted out here for use as a normal utility function.
    """
    if not text:
        return None
    text = text.strip().translate(str.maketrans("", "", string.punctuation))
    return (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    )

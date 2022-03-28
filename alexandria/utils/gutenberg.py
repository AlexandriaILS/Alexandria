"""
This script is meant to be run by hand to get raw data from Project Gutenberg.

Stage 1 creates `output.json`, which is a little over 95MB.
Stage 2 collapses that into a 3.5MB binary file ready for import.
"""

import gzip
import json
import time
from io import BytesIO

import requests

OUTFILE = "output.json"
OUTFILE2 = "raw_gutenberg_data"

DATA = {"results": []}


def get_from_gutendex():
    print("Starting!")
    URL = "http://gutendex.com/books/"
    # there are only 65000 entries, so we should be able to hold that in memory
    while True:
        response = requests.get(URL)
        resp = response.json()
        DATA["results"].append(resp["results"])
        if not resp.get("next"):
            break
        URL = resp["next"]
        time.sleep(0.5)
        print(f"Getting page {URL.split('=')[1]}...")

    print("Writing data...")
    with open(OUTFILE, "w") as f:
        f.write(json.dumps(DATA, indent=2))


"""
Raw book information:

{
    "id": 61,
    "title": "The Communist Manifesto",
    "authors": [
        {
            "name": "Engels, Friedrich",
            "birth_year": 1820,
            "death_year": 1895
        },
        {
            "name": "Marx, Karl",
            "birth_year": 1818,
            "death_year": 1883
        }
    ],
    "translators": [],
    "subjects": [
        "Communism",
        "Socialism"
    ],
    "bookshelves": [
        "Banned Books from Anne Haight's list",
        "Philosophy",
        "Politics"
    ],
    "languages": [
        "en"
    ],
    "copyright": false,
    "media_type": "Text",
    "formats": {
        "application/epub+zip": "https://www.gutenberg.org/ebooks/61.epub.images",
        "application/rdf+xml": "https://www.gutenberg.org/ebooks/61.rdf",
        "text/plain": "https://www.gutenberg.org/ebooks/61.txt.utf-8",
        "application/x-mobipocket-ebook": "https://www.gutenberg.org/ebooks/61.kindle.images",
        "image/jpeg": "https://www.gutenberg.org/cache/epub/61/pg61.cover.medium.jpg",
        "text/html": "https://www.gutenberg.org/files/61/61-h/61-h.htm",
        "application/octet-stream": "https://www.gutenberg.org/files/61/61-0.zip",
        "text/plain; charset=us-ascii": "https://www.gutenberg.org/files/61/61-0.txt",
        "application/zip": "https://www.gutenberg.org/files/61/61-h.zip"
    },
    "download_count": 4436
}
"""


# https://stackoverflow.com/a/52030410
def decompressBytesToString(inputBytes):
    """
    decompress the given byte array (which must be valid
    compressed gzip data) and return the decoded text (utf-8).
    """
    bio = BytesIO()
    stream = BytesIO(inputBytes)
    decompressor = gzip.GzipFile(fileobj=stream, mode="r")
    while True:  # until EOF
        chunk = decompressor.read(8192)
        if not chunk:
            decompressor.close()
            bio.seek(0)
            return bio.read().decode("utf-8")
        bio.write(chunk)


def compressStringToBytes(inputString):
    """
    read the given string, encode it in utf-8,
    compress the data and return it as a byte array.
    """
    bio = BytesIO()
    bio.write(inputString.encode("utf-8"))
    bio.seek(0)
    stream = BytesIO()
    compressor = gzip.GzipFile(fileobj=stream, mode="w")
    while True:  # until EOF
        chunk = bio.read(8192)
        if not chunk:  # EOF?
            compressor.close()
            return stream.getvalue()
        compressor.write(chunk)


def second_stage_compression():
    DATA = {"results": []}
    with open(OUTFILE, "r") as outfile:
        json_data = json.loads(outfile.read())

    for page in json_data["results"]:
        for obj in page:
            book = {
                "id": obj["id"],
                "title": obj["title"].encode("utf-8").decode(),
                # convert from "Bront\u00eb, Charlotte" to "Brontë, Charlotte"
                "authors": [_["name"].encode("utf-8").decode() for _ in obj["authors"]],
                "subjects": [sub.encode("utf-8").decode() for sub in obj["subjects"]],
            }
            if obj["translators"]:
                book.update(
                    {
                        "translators": [
                            _["name"].encode("utf-8").decode()
                            for _ in obj["translators"]
                        ]
                    }
                ),
            DATA["results"].append(book)

    DATA.update(
        {
            "image_format": "https://www.gutenberg.org/cache/epub/{0}/pg{0}.cover.medium.jpg"
        }
    )

    print("Writing data...")
    with open(OUTFILE2, "wb") as f:
        f.write(compressStringToBytes(json.dumps(DATA)))


if __name__ == "__main__":
    # get_from_gutendex()
    second_stage_compression()

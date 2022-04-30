import requests

from alexandria.records import openlibrary


class CoverUtilitiesMixin:
    def get_cover_image(self, context: dict) -> None:
        """Request a cover image from openlibrary."""
        # todo: farm this out to task worker
        if context.get("enable_openlibrary_cover_downloads", False):
            try:
                openlibrary.download_cover(self)
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
                pass

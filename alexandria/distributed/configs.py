import logging
import re

from django.conf import settings

logger = logging.getLogger("alexandria")


def get_site_host_key(domain: str) -> str:
    if (
        any(
            re.match(option.replace("*", ".+"), domain)
            for option in settings.DEFAULT_HOSTS
        )
        or domain == settings.DEFAULT_HOST_KEY
    ):
        return settings.DEFAULT_HOST_KEY
    else:
        return domain

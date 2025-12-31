from typing import Any

from django.conf import settings
from django.db import models
from django.db.utils import ProgrammingError
from django.utils.translation import gettext as _


class Domain(models.Model):
    name = models.CharField(max_length=253, default=settings.DEFAULT_HOST_KEY)

    @classmethod
    def get_default(cls):
        return cls.objects.get_or_create(name=settings.DEFAULT_HOST_KEY)[0]

    @classmethod
    def get_default_pk(cls):
        try:
            return cls.objects.get_or_create(name=settings.DEFAULT_HOST_KEY)[0].pk
        except ProgrammingError:
            # We're running migrations for the first time. There's nothing in the
            # db yet, so we can just return any value and the right one will be
            # pulled for future objects.
            return 1

    @classmethod
    def get_system(cls):
        return cls.objects.get_or_create(name=settings.DEFAULT_SYSTEM_HOST_KEY)[0]

    def __str__(self):
        return self.name


class SettingsContainer:
    def __init__(self, host):
        self.host = host
        # Grab all the settings in one call, then compile them into a
        # dict for easy access without repetitive calls later in the
        # templates.
        settings_values = Setting.objects.filter(host=self.host).values("name", "value")

        options = {Setting.options[i].value: i.lower() for i in Setting.options.names}
        self.values = {options[s["name"]]: s["value"] for s in settings_values}

    def __getattr__(self, item: str) -> str:
        if item in self.values:
            return self.values[item]

        return None

    def get(self, name: str, default: Any):
        return self.values.get(name, default)

    def get_int(self, name: str, default: int):
        return int(self.values.get(name, default))


class Setting(models.Model):
    class options(models.TextChoices):
        NAME = "name", _("Library system name")
        URL = "url", _("Library system base URL")
        ADDRESS_1 = "ad_1", _("Address: street 1")
        ADDRESS_2 = "ad_2", _("Address: street 2")
        CITY = "city", _("Address: city")
        STATE = "stat", _("Address: state (two letter version, like IN or NY)")
        COUNTRY = "cntr", _("Address: country")
        ZIP_CODE = "zip", _("Address: zip code")
        PHONE_NUMBER = "phon", _("Phone number")
        ENABLE_RUNNING_BORROW_SAVED_MONEY = "ebsm", _(
            "Enable keeping track of saved money through borrowing"
        )
        FLOATING_COLLECTION = "flot", _("Floating collection")
        FORCE_UNIQUE_CALL_NUMBERS = "fucn", _("Force unique call numbers")
        IGNORED_SEARCH_TERMS = "ist", _("a,an,the")
        ZENODOTUS_URL = "zurl", _("Zenodotus API URL")
        ZENODOTUS_AUTO_UPLOAD = "z_au", _("Enable automatic uploads to Zenodotus")
        ZENODOTUS_AUTO_CHECK_FOR_UPDATES = "z_up", _(
            "Automatically check Zenodotus for record updates"
        )
        DEFAULT_ADDRESS_STATE_OR_REGION = "d_st", _(
            "Default address for new users: state or region (two letter version, like"
            " IN or NY)"
        )
        DEFAULT_ADDRESS_CITY = "d_ct", _("Default address for new users: city")
        DEFAULT_ADDRESS_ZIP_CODE = "d_zc", _("Default address for new users: zip code")
        DEFAULT_ADDRESS_COUNTRY = "d_cy", _("Default address for new users: country")
        DEFAULT_RESULTS_PER_PAGE = "drpp", _("Default number of results per page")
        DEFAULT_MAX_RENEWS = "dmr", _("Default maximum number of renewals")
        DEFAULT_CHECKOUT_DURATION_DAYS = "dcdd", _("Default checkout duration (days)")
        DEFAULT_LOCATION_ID = "d_li", _("Default location ID")
        DEFAULT_RENEWAL_DELAY_DAYS = "drdd", _(
            "Default renewal delay (how long before an item is due that the renewal"
            " button can be pressed) in days"
        )
        DEFAULT_HOLD_EXPIRY_DAYS = "dhed", _(
            "How long to leave a hold on the shelf before it expires"
        )
        NAVBAR_LINK_1_TITLE = "n1t", _("Navbar item 1: title")
        NAVBAR_LINK_1_URL = "n1u", _("Navbar item 1: URL")
        NAVBAR_LINK_2_TITLE = "n2t", _("Navbar item 2: title")
        NAVBAR_LINK_2_URL = "n2u", _("Navbar item 2: URL")
        NAVBAR_LINK_3_TITLE = "n3t", _("Navbar item 3: title")
        NAVBAR_LINK_3_URL = "n3u", _("Navbar item 3: URL")
        ENABLE_OPENLIBRARY_COVER_DOWNLOADS = "eocd", _(
            "Enable automatic downloading of missing cover images from OpenLibrary"
        )
        USE_SHELVING_CART_FOR_CHECK_IN = "uscc", _(
            "When checking in books, have items default to the shelving cart"
        )
        SHELVING_CART_DELAY_HOURS = "scdh", _(
            "When using the shelving cart, how long before items are automatically"
            " marked as available in the stacks (hours)"
        )

    name = models.CharField(max_length=4, choices=options.choices)
    value = models.TextField()
    host = models.ForeignKey(
        Domain, on_delete=models.CASCADE, default=Domain.get_default_pk
    )

    @classmethod
    def get(
        cls, name: str, host: Domain = None, default: int | str = None
    ) -> str | None:
        if not host:
            host = Domain.get_default()
        if result := cls.objects.filter(name=name, host=host).first():
            return result.value
        return default

    def __str__(self):
        return f"{self.host.name}: {self.name}={self.value}"

    @classmethod
    def get_int(cls, *args, **kwargs) -> int | None:
        # Handle settings that might be None without extra boilerplate.
        if result := cls.get(*args, **kwargs):
            return int(result)
        return None

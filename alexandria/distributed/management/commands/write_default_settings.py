from django.core.management.base import BaseCommand

from alexandria.distributed.models import Setting


class Command(BaseCommand):
    help = "Create the default settings used for development."

    def handle(self, *args, **options):
        o = Setting.options
        default_settings = {
            o.NAME: "Neverland Library",
            o.URL: "https://alexandrialibrary.dev",
            o.ADDRESS_1: "123 Neverland Lane",
            o.ADDRESS_2: "",
            o.CITY: "Neverland",
            o.STATE: "IN",
            o.COUNTRY: "USA",
            o.ZIP_CODE: "12345",
            o.PHONE_NUMBER: "1-234-555-6789",
            o.ENABLE_RUNNING_BORROW_SAVED_MONEY: True,
            o.FLOATING_COLLECTION: False,
            o.FORCE_UNIQUE_CALL_NUMBERS: False,
            o.IGNORED_SEARCH_TERMS: "a,an,the",
            o.ZENODOTUS_URL: "https://zenodotus.alexandrialibrary.dev/api/",
            o.ZENODOTUS_AUTO_UPLOAD: True,
            o.ZENODOTUS_AUTO_CHECK_FOR_UPDATES: True,
            o.DEFAULT_ADDRESS_STATE_OR_REGION: "IN",
            o.DEFAULT_ADDRESS_CITY: "Indianapolis",
            o.DEFAULT_ADDRESS_ZIP_CODE: "46227",
            o.DEFAULT_ADDRESS_COUNTRY: "USA",
            o.DEFAULT_RESULTS_PER_PAGE: 25,
            o.DEFAULT_MAX_RENEWS: 5,
            o.DEFAULT_CHECKOUT_DURATION_DAYS: 21,
            o.DEFAULT_LOCATION_ID: 7,
            o.DEFAULT_RENEWAL_DELAY_DAYS: 7,
            o.DEFAULT_HOLD_EXPIRY_DAYS: 3,
            o.NAVBAR_LINK_1_TITLE: "Example!",
            o.NAVBAR_LINK_1_URL: "https://example.com",
            o.NAVBAR_LINK_2_TITLE: "Libby",
            o.NAVBAR_LINK_2_URL: "https://example.com",
            o.NAVBAR_LINK_3_TITLE: "Overdrive",
            o.NAVBAR_LINK_3_URL: "https://example.com",
            o.ENABLE_OPENLIBRARY_COVER_DOWNLOADS: True,
            o.USE_SHELVING_CART_FOR_CHECK_IN: True,
            o.SHELVING_CART_DELAY_HOURS: 1,
        }
        for option in default_settings.items():
            Setting.objects.get_or_create(name=option[0], value=option[1])

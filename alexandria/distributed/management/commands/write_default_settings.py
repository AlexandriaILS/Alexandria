from django.core.management.base import BaseCommand

from alexandria.distributed.models import Setting


class Command(BaseCommand):
    help = "Create the default settings used for development."

    def handle(self, *args, **options):
        default_settings = {
            "name": "Neverland Library",
            "url": "https://alexandrialibrary.dev",
            "address_1": "123 Neverland Lane",
            "address_2": "",
            "city": "Neverland",
            "state": "IN",
            "country": "USA",
            "zip_code": "12345",
            "phone_number": "1-234-555-6789",
            "enable_running_borrow_saved_money": True,
            "floating_collection": False,
            "force_unique_call_numbers": False,
            "ignored_search_terms": "a,an,the",
            "zenodotus_url": "https://zenodotus.alexandrialibrary.dev/api/",
            "zenodotus_auto_upload": True,
            "zenodotus_auto_check_for_updates": True,
            "default_address_state_or_region": "IN",
            "default_address_city": "Indianapolis",
            "default_address_zip_code": "46227",
            "default_address_country": "USA",
            "default_results_per_page": 25,
            "default_max_renews": 5,
            "default_checkout_duration_days": 21,
            "default_location_id": 7,
            "default_renewal_delay_days": 7,
            "default_hold_expiry_days": 3,
            "navbar_link_1_title": "Example!",
            "navbar_link_1_url": "https://example.com",
            "navbar_link_2_title": "Libby",
            "navbar_link_2_url": "https://example.com",
            "navbar_link_3_title": "Overdrive",
            "navbar_link_3_url": "https://example.com",
            "enable_openlibrary_cover_downloads": True,
            "use_shelving_cart_for_check_in": True,
            "shelving_cart_delay_hours": 1,
        }
        for option in default_settings.items():
            Setting.objects.get_or_create(name=option[0], value=option[1])

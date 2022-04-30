from alexandria.settings.base import *  # noqa: F403

ENVIRONMENT = "testing"
DEBUG = True
ALLOWED_HOSTS = ["*"]
DEFAULT_HOSTS = ["testserver"]
# Cave Johnson, Portal 2.
SECRET_KEY = (
    "There's a thousand tests performed every day here in our enrichment spheres."
    " I can't personally oversee every one of them, so these pre-recorded messages'll"
    " cover any questions you might have, and respond to any incidents that may"
    " occur in the course of your science adventure."
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }  # noqa: E231
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "alexandria",
        "USER": "alexandria",
        "PASSWORD": "asdf",
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },  # noqa: E231
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
        "blossom": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
    },
}

SITE_DATA = {
    "default": {
        "name": "Neverland Library",
        "url": "https://alexandrialibrary.dev",
        "logo_url": None,
        "address": "123 Neverland Lane, Neverland, USA, 12345",
        "phone_number": "1-234-555-6789",
        "enable_running_borrow_saved_money": True,
        "floating_collection": False,
        "force_unique_call_numbers": False,
        "ignored_search_terms": ["a", "an", "the"],
        "zenodotus_url": "https://zenodotus.alexandrialibrary.dev/api/",
        "zenodotus_auto_upload": True,
        "default_address_state_or_region": "IN",
        "default_address_city": "Indianapolis",
        "default_address_zip_code": "46227",
        "default_address_country": "USA",
        "default_results_per_page": 25,
        "default_max_renews": 5,
        "default_checkout_duration_days": 21,
        "default_location_id": 1,
        "default_renewal_delay_days": 7,
        "navbar": {
            "link_1_title": "Example!",
            "link_1_url": "https://example.com",
            "link_2_title": "Libby",
            "link_2_url": "https://example.com",
            "link_3_title": "Overdrive",
            "link_3_url": "https://example.com",
        },
        "enable_openlibrary_cover_downloads": False,
    }
}

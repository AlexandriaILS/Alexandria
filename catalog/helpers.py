from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest


def get_results_per_page(request: WSGIRequest) -> int:
    try:
        results_per_page = int(
            request.GET.get("count", settings.DEFAULT_RESULTS_PER_PAGE)
        )
        if results_per_page < 1:
            # accidentally fell over this while testing
            return settings.DEFAULT_RESULTS_PER_PAGE
        else:
            return results_per_page
    except ValueError:
        return settings.DEFAULT_RESULTS_PER_PAGE

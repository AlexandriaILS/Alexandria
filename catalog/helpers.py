from django.core.handlers.wsgi import WSGIRequest


def get_results_per_page(request: WSGIRequest) -> int:
    default: int = request.context['default_results_per_page']
    try:
        results_per_page = int(request.GET.get("count", default))
        if results_per_page < 1:
            # accidentally fell over this while testing
            return default
        else:
            return results_per_page
    except ValueError:
        return default

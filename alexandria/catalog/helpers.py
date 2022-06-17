from alexandria.distributed.models import Setting
from alexandria.utils.type_hints import Request


def get_results_per_page(request: Request) -> int:
    default: int = request.settings.get_int(
        Setting.options.DEFAULT_RESULTS_PER_PAGE, default=25
    )
    try:
        results_per_page = int(request.GET.get("count", default))
        if results_per_page < 1:
            # accidentally fell over this while testing
            return default
        else:
            return results_per_page
    except ValueError:
        return default

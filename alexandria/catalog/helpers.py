from alexandria.utils.type_hints import Request


def get_results_per_page(request: Request) -> int:
    default: int = request.context["default_results_per_page"]
    try:
        results_per_page = int(request.GET.get("count", default))
        if results_per_page < 1:
            # accidentally fell over this while testing
            return default
        else:
            return results_per_page
    except ValueError:
        return default

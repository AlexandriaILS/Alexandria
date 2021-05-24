from django.shortcuts import reverse
from django.http import HttpRequest

def next_or_reverse(request: HttpRequest, view_name: str) -> str:
    # After typoing this too many times, it's now a helper function.
    # noinspection PyTypeChecker
    return request.GET.get("next", reverse(view_name))

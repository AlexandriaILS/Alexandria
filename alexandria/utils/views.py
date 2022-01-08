from django.shortcuts import reverse, redirect, HttpResponseRedirect
from django.http import HttpRequest


def next_or_reverse(request: HttpRequest, view_name: str) -> str:
    # After typoing this too many times, it's now a helper function.
    # noinspection PyTypeChecker
    return request.GET.get("next", reverse(view_name))


def redirect_with_qsps(request: HttpRequest, view_name: str) -> HttpResponseRedirect:
    return redirect(
        reverse(view_name)
        + "?"
        + "&".join([f"{option}={request.GET[option]}" for option in request.GET.keys()])
    )

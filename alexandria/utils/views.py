from alexandria.distributed.configs import get_domains_from_configs

from django.conf import settings
from django.shortcuts import reverse, redirect, HttpResponseRedirect
from django.http import HttpRequest
from django.utils.http import url_has_allowed_host_and_scheme


def next_or_reverse(request: HttpRequest, view_name: str) -> str:
    # After typoing this too many times, it's now a helper function.
    # noinspection PyTypeChecker
    next = request.GET.get("next")
    if next:
        # because we don't use settings.ALLOWED_HOSTS in the normal way, we have
        # to construct what Django is looking for so that we can use this security
        # function.
        hosts = settings.DEFAULT_HOSTS + get_domains_from_configs()
        if url_has_allowed_host_and_scheme(next, hosts):
            return next
        else:
            # DANGER! We got an invalid redirect!
            return reverse(view_name)
    else:
        return reverse(view_name)


def redirect_with_qsps(request: HttpRequest, view_name: str) -> HttpResponseRedirect:
    return redirect(
        reverse(view_name)
        + "?"
        + "&".join([f"{option}={request.GET[option]}" for option in request.GET.keys()])
    )

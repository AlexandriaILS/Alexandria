from typing import Callable

from django.contrib.auth.decorators import REDIRECT_FIELD_NAME, user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse

from alexandria.utils.type_hints import Request


def library_staff_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
) -> Callable:
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def htmx_guard_redirect(redirect_name):
    """
    Decorator for guarding HTMX-only function views.

    If a request comes in to this endpoint that did not originate from HTMX,
    respond with a redirect to the requested endpoint.

    Takes an optional `test` boolean that bypasses the redirect.
    """
    # https://stackoverflow.com/a/9030358
    def _method_wrapper(view_method: Callable) -> Callable:
        def _arguments_wrapper(
            request: Request, *args, **kwargs
        ) -> HttpResponseRedirect | Callable:
            testing = False
            if "test" in kwargs.keys():
                testing = kwargs.pop("test")
            if not request.htmx and not testing:
                return HttpResponseRedirect(reverse(redirect_name))
            return view_method(request, *args, **kwargs)

        return _arguments_wrapper

    return _method_wrapper

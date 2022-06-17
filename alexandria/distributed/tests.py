import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import DisallowedHost
from django.test import RequestFactory
from pytest_django.fixtures import SettingsWrapper
from pytest_mock import MockerFixture

from alexandria.distributed.middleware import (
    ContextUpdateMiddleware,
    HostValidationMiddleware,
)
from alexandria.utils.test_helpers import get_default_domain


def test_valid_host_response(rf: RequestFactory, settings: SettingsWrapper):
    request = rf.get("/")
    request.host = get_default_domain()

    try:
        HostValidationMiddleware(lambda: True).process_request(request)
    except DisallowedHost:
        assert False, "Should allow the default domain."


def test_invalid_host(rf: RequestFactory):
    request = rf.get("/")
    request.get_host = lambda: "example.com"

    with pytest.raises(DisallowedHost):
        HostValidationMiddleware(lambda: True).process_request(request)


def test_context_update_with_no_context(rf: RequestFactory):
    """If no context is present, the request should not be modified."""
    request = rf.get("/")
    assert not hasattr(request, "context")

    ContextUpdateMiddleware(lambda: True).process_request(request)

    # Still shouldn't have that attribute if we didn't start with it
    assert not hasattr(request, "context")


def test_context_update(rf: RequestFactory):
    """If the context exists, we should expand it."""
    request = rf.get("/")
    request.context = {}
    request.user = AnonymousUser()

    ContextUpdateMiddleware(lambda: True).process_request(request)

    assert len(request.context) > 0

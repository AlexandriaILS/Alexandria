import pytest
from django.test import RequestFactory

from alexandria.users.admin import has_superuser_permission
from alexandria.utils.test_helpers import (
    get_default_patron_user,
    get_default_staff_user,
    get_default_underage_patron_user,
    get_superuser,
)


@pytest.mark.parametrize(
    "input,expected",
    [
        (get_superuser, True),
        (get_default_staff_user, False),
        (get_default_underage_patron_user, False),
        (get_default_patron_user, False),
    ],
)
def test_has_superuser_perms(input, expected: bool, rf: RequestFactory):
    request = rf.get("/")
    request.user = input()

    assert has_superuser_permission(request) == expected

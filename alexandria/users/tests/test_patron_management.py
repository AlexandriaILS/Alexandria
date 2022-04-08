from django.shortcuts import reverse
from django.test.client import Client

from alexandria.utils.test_helpers import (
    get_default_patron_user,
    get_default_staff_user,
)


def test_act_as_user(client: Client):
    """Verify that the session is configured correctly when acting as a patron."""
    user = get_default_patron_user()
    staff = get_default_staff_user()

    client.force_login(staff)
    client.get(reverse("act_as_user", args=(user.card_number,)))

    assert client.session.get("acting_as_patron") == user.card_number

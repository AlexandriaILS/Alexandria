from django.test import Client
from django.shortcuts import reverse

from alexandria.catalog.user_accounts.views import my_checkouts, my_holds
from alexandria.utils.tests.helpers import get_test_item, get_default_patron_user


def test_my_checkouts(client: Client):
    """Verify that the My Checkouts page works as expected."""
    item = get_test_item()
    user = get_default_patron_user()
    assert item.checked_out_to is None

    item.check_out_to(user)
    item.refresh_from_db()
    assert item.checked_out_to == user

    client.force_login(user)
    response = client.get(reverse("my_checkouts"))
    assert item in response.context

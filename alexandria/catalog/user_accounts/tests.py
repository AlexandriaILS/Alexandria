from django.test import Client
from django.shortcuts import reverse
import pytest

from alexandria.records.models import Hold
from alexandria.utils.tests.helpers import get_test_item, get_default_patron_user


def test_my_checkouts(client: Client, setup_site):
    """Verify that the My Checkouts page works as expected."""
    item = get_test_item()
    user = get_default_patron_user()
    assert item.checked_out_to is None

    client.force_login(user)
    response = client.get(reverse("my_checkouts"))
    assert len(response.context["checkouts"]) == 0

    item.check_out_to(user)
    item.refresh_from_db()
    assert item.checked_out_to == user

    response = client.get(reverse("my_checkouts"))
    assert item in response.context["checkouts"]


def test_my_holds(client: Client, setup_site):
    """Verify that the My Holds page works as expected."""
    item = get_test_item()
    user = get_default_patron_user()

    client.force_login(user)
    response = client.get(reverse("my_holds"))
    assert len(response.context["holds"]) == 0

    hold = Hold.objects.create(placed_for=user, item=item)

    response = client.get(reverse("my_holds"))
    assert hold in response.context["holds"]


@pytest.mark.skip
def test_my_fees(client: Client, setup_site):
    """Verify that the My Fees page works as expected."""
    ...

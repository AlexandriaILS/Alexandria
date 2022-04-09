from datetime import timedelta

from django.test import Client
from django.utils import timezone

from alexandria.records.models import Item
from alexandria.utils.test_helpers import (
    get_default_branch_location,
    get_default_hold,
    get_default_patron_user,
    get_default_record,
    get_default_staff_user,
    get_default_underage_patron_user,
    get_test_item,
)


def test_renewal(client: Client, mocker):
    item = get_test_item()
    user = get_default_patron_user()

    mocker.patch.object(Item, "can_renew", return_value=True)
    item.check_out_to(user)
    original_due_date = timezone.now() - timedelta(days=1)
    item.due_date = original_due_date
    item.save()

    client.force_login(user)
    resp = client.get(f"/api/items/{item.id}/renew/")
    assert resp.status_code == 200
    item.refresh_from_db()
    assert item.due_date != original_due_date


def test_wrong_patron_cant_renew_materials(client: Client):
    item = get_test_item()
    bad_actor = get_default_patron_user()
    user = get_default_underage_patron_user()

    item.check_out_to(user)
    current_due_date = item.due_date
    client.force_login(bad_actor)
    resp = client.get(f"/api/items/{item.id}/renew/")
    assert resp.status_code == 403
    item.refresh_from_db()
    # shouldn't have renewed item
    assert item.due_date == current_due_date


def test_staff_can_renew_item(client: Client, mocker):
    item = get_test_item()
    user = get_default_patron_user()
    staff = get_default_staff_user()

    mocker.patch.object(Item, "can_renew", return_value=True)
    item.check_out_to(user)
    original_due_date = timezone.now() - timedelta(days=1)
    item.due_date = original_due_date
    item.save()

    # log in as the staff member and renew the patron's material
    client.force_login(staff)
    resp = client.get(f"/api/items/{item.id}/renew/")
    assert resp.status_code == 200
    item.refresh_from_db()
    assert item.due_date != original_due_date


def test_item_not_renewable(client: Client, mocker):
    item = get_test_item()
    user = get_default_patron_user()

    mocker.patch.object(Item, "can_renew", return_value=False)
    item.check_out_to(user)

    client.force_login(user)
    resp = client.get(f"/api/items/{item.id}/renew/")
    assert resp.status_code == 403

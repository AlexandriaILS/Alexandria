from django.test import Client, RequestFactory
from django.utils import timezone
from rest_framework.test import APIClient

from alexandria.api.views import create_hold
from alexandria.records.models import Hold
from alexandria.utils.test_helpers import (
    get_default_branch_location,
    get_default_hold,
    get_default_patron_user,
    get_default_record,
    get_default_staff_user,
    get_default_underage_patron_user,
    get_test_item,
)


def test_create_hold_for_item(client: Client):
    """Verify a hold can be created for a specific item."""
    item = get_test_item()
    location = get_default_branch_location()
    user = get_default_patron_user()
    client.force_login(user)

    assert Hold.objects.count() == 0

    data = {"location_id": location.id}

    resp = client.post(f"/api/items/{item.id}/place_hold/", data=data)
    assert resp.status_code == 201
    assert resp.json()["hold_number"] == 1
    assert resp.json()["name"] == item.type.name

    assert Hold.objects.count() == 1


def test_cannot_create_hold_twice(client: Client):
    """Verify a hold cannot be created twice."""
    item = get_test_item()
    location = get_default_branch_location()
    user = get_default_patron_user()
    client.force_login(user)

    assert Hold.objects.count() == 0

    data = {"location_id": location.id}

    resp = client.post(f"/api/items/{item.id}/place_hold/", data=data)
    assert resp.status_code == 201
    assert Hold.objects.count() == 1

    resp = client.post(f"/api/items/{item.id}/place_hold/", data=data)
    assert resp.status_code == 409
    # make sure we didn't make another hold object
    assert Hold.objects.count() == 1


def test_cannot_create_hold_on_checked_out_item(client: Client):
    """Verify that a user cannot place a hold on an item they currently have."""
    item = get_test_item()
    location = get_default_branch_location()
    user = get_default_patron_user()
    client.force_login(user)

    item.check_out_to(user)

    data = {"location_id": location.id}
    resp = client.post(f"/api/items/{item.id}/place_hold/", data=data)
    assert resp.status_code == 406


def test_create_hold_for_item_without_login(client: Client):
    """Verify a hold cannot be created for an unauthenticated user."""
    item = get_test_item()
    location = get_default_branch_location()

    assert Hold.objects.count() == 0

    data = {"location_id": location.id}

    resp = client.post(f"/api/items/{item.id}/place_hold/", data=data)
    assert resp.status_code == 403
    assert Hold.objects.count() == 0


def test_create_hold_for_record(client: Client):
    """Verify a hold can be created from only a record."""
    record = get_default_record()
    location = get_default_branch_location()
    item = get_test_item(home_location=location)
    user = get_default_patron_user()
    client.force_login(user)

    assert Hold.objects.count() == 0

    data = {"item_type_id": item.type.id, "location_id": location.id}

    resp = client.post(f"/api/records/{record.id}/place_hold/", data=data)
    assert resp.status_code == 201
    assert resp.json()["hold_number"] == 1
    assert resp.json()["name"] == item.type.name
    assert Hold.objects.count() == 1


def test_create_hold_for_record_with_no_items(client: Client):
    """Verify a hold with no items returns an error."""
    record = get_default_record()
    location = get_default_branch_location()
    item = get_test_item(home_location=location)
    user = get_default_patron_user()
    client.force_login(user)

    assert Hold.objects.count() == 0

    data = {"item_type_id": item.type.id, "location_id": location.id}
    item.delete()

    resp = client.post(f"/api/records/{record.id}/place_hold/", data=data)
    assert resp.status_code == 412
    assert Hold.objects.count() == 0


def test_record_available_at_target_location(client: Client):
    """
    Verify that the closest available item will be chosen.

    When a hold for a record is placed, we want to default to sending an
    item that is already at the target location AND is the most recent checkout.
    """
    record = get_default_record()
    location = get_default_branch_location()
    other_location = get_default_branch_location(name="Way Too Far Branch")
    ideal_item = get_test_item(home_location=location, last_checked_out=timezone.now())
    lost_item = get_test_item(
        home_location=location, last_checked_out=timezone.now().replace(year=1970)
    )
    too_far_item = get_test_item(home_location=other_location)
    user = get_default_patron_user()
    client.force_login(user)

    assert ideal_item.type.id == lost_item.type.id == too_far_item.type.id

    data = {"item_type_id": ideal_item.type.id, "location_id": location.id}

    resp = client.post(f"/api/records/{record.id}/place_hold/", data=data)
    assert resp.status_code == 201

    new_hold = Hold.objects.first()
    assert new_hold.item == ideal_item


def test_record_available_at_wrong_location(client: Client):
    """
    Verify that the closest available item will be chosen.

    When the target item is not available at the destination library, grab the one
    from the system that has been checked out the most recently.
    """
    record = get_default_record()
    location = get_default_branch_location()
    other_location = get_default_branch_location(name="Way Too Far Branch")
    ideal_item = get_test_item(
        home_location=other_location, last_checked_out=timezone.now()
    )
    lost_item = get_test_item(
        home_location=other_location, last_checked_out=timezone.now().replace(year=1970)
    )
    user = get_default_patron_user()
    client.force_login(user)

    assert ideal_item.type.id == lost_item.type.id

    data = {"item_type_id": ideal_item.type.id, "location_id": location.id}

    resp = client.post(f"/api/records/{record.id}/place_hold/", data=data)
    assert resp.status_code == 201

    new_hold = Hold.objects.first()
    assert new_hold.item == ideal_item


def test_create_hold_verify_correct_data(rf: RequestFactory):
    item = get_test_item()
    location = get_default_branch_location()
    user = get_default_patron_user()

    request = rf.get("/")
    request.user = user
    request.host = "example.com"
    request.session = {}

    assert Hold.objects.count() == 0

    create_hold(request, item, location, specific_copy=True)

    new_hold = Hold.objects.first()
    assert new_hold.destination == location
    assert new_hold.placed_for == user
    assert new_hold.item == item
    assert new_hold.host == "example.com"


def test_set_hold_for_other_user(rf: RequestFactory):
    """Placing a hold for a patron should not set it for the staff member."""
    item = get_test_item()
    location = get_default_branch_location()
    user = get_default_patron_user()
    staff_member = get_default_staff_user()

    request = rf.get("/")
    request.user = staff_member
    request.host = "example.com"
    request.session = {"acting_as_patron": user.card_number}

    assert Hold.objects.count() == 0

    create_hold(request, item, location, specific_copy=True)

    new_hold = Hold.objects.first()
    assert new_hold.placed_for == user
    assert Hold.objects.filter(placed_for=staff_member).count() == 0


def test_delete_hold(api_client: APIClient):
    """Verify that users can delete their own holds."""
    user = get_default_patron_user()
    new_hold = get_default_hold(placed_for=user)
    api_client.force_authenticate(user)

    assert Hold.objects.count() == 1

    resp = api_client.delete(f"/api/holds/{new_hold.id}/")
    assert resp.status_code == 200

    assert Hold.objects.count() == 0


def test_delete_hold_as_wrong_user(api_client: APIClient):
    """Verify that people cannot delete someone else's hold."""
    user = get_default_patron_user()
    new_hold = get_default_hold(placed_for=user)
    bad_actor = get_default_underage_patron_user()  # darn those teens
    api_client.force_authenticate(bad_actor)

    assert Hold.objects.count() == 1

    resp = api_client.delete(f"/api/holds/{new_hold.id}/")
    assert resp.status_code == 403

    assert Hold.objects.count() == 1


def test_delete_hold_as_staff(api_client: APIClient):
    """Verify that staff can delete holds."""
    user = get_default_patron_user()
    new_hold = get_default_hold(placed_for=user)
    staff = get_default_staff_user()
    api_client.force_authenticate(staff)

    assert Hold.objects.count() == 1

    resp = api_client.delete(f"/api/holds/{new_hold.id}/")
    assert resp.status_code == 200

    assert Hold.objects.count() == 0

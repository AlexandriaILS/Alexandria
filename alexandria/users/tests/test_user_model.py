import pytest
from django.contrib.auth.models import Group
from django.db.models import QuerySet

from alexandria.records.models import ItemType
from alexandria.users.models import AccountType, BranchLocation, User, USLocation
from alexandria.utils.permissions import perm_to_permission
from alexandria.utils.test_helpers import (
    get_default_branch_location,
    get_default_collection,
    get_default_item_type,
    get_default_patron_user,
    get_default_staff_user,
    get_test_item,
)


class TestCreateUser:
    def test_create_user_with_minimum_info(self):
        new_user = User.objects.create_user(
            card_number="aaaa", email="a@a.com", legal_first_name="A"
        )
        assert new_user.email == "a@a.com"
        assert new_user.card_number == "aaaa"
        assert new_user.legal_first_name == "A"
        assert new_user.get_shortened_name() == "A"

    @pytest.mark.parametrize(
        "values",
        [
            (None, "a@a.com", "A"),
            ("aaab", None, "A"),
            ("aaac", "a@a.com", None),
        ],
    )
    def test_create_user_without_required_data(self, values):
        with pytest.raises(ValueError):
            User.objects.create_user(
                card_number=values[0], email=values[1], legal_first_name=values[2]
            )

    def test_create_superuser(self):
        new_user = User.objects.create_superuser(
            card_number="aaaa", email="a@a.com", legal_first_name="A"
        )
        assert new_user.is_staff is True
        assert new_user.is_superuser is True

    def test_create_superuser_fails_with_overridden_flags_1(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                card_number="aaaa", email="a@a.com", legal_first_name="A", is_staff=False
            )

    def test_create_superuser_fails_with_overridden_flags_2(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                card_number="aaaa", email="a@a.com", legal_first_name="A", is_superuser=False
            )


class TestUserFunctions:
    def test_get_branches(self):
        user = get_default_patron_user()
        branch = get_default_branch_location()

        assert user.host == branch.host
        # Can't compare the querysets together for some reason, so we'll approximate
        result = user.get_branches()

        assert len(result) == 1
        assert isinstance(result, QuerySet)
        assert result.first() == branch

    def test_get_branches_in_wrong_host(self):
        user = get_default_patron_user()
        branch = get_default_branch_location(host="AAA")

        assert user.host != branch.host

        result = user.get_branches()
        assert len(result) == 0

    def test_get_serializable_branches(self):
        user = get_default_patron_user()
        location = get_default_branch_location()

        assert user.get_serializable_branches() == [
            {"address__address_1": None, "id": location.id, "name": location.name}
        ]

    def test_get_default_branch(self):
        user = get_default_patron_user()
        branch = get_default_branch_location()

        user.default_branch = branch
        user.save()

        assert user.get_default_branch() == branch

    def test_get_default_branch_without_one_set(self, mocker):
        user = get_default_patron_user()
        branch = get_default_branch_location()

        mocker.patch(
            "alexandria.users.models.load_site_config",
            return_value={"default_location_id": branch.id},
        )

        assert user.get_default_branch() == branch

    def test_get_work_branch_as_patron(self):
        user = get_default_patron_user()
        assert user.get_work_branch() == None

    def test_get_work_branch_as_staff_without_one_set(self, mocker):
        user = get_default_staff_user()
        branch = get_default_branch_location()

        mocker.patch(
            "alexandria.users.models.load_site_config",
            return_value={"default_location_id": branch.id},
        )

        assert user.get_work_branch() == branch

    def test_get_work_branch_as_staff(self):
        user = get_default_staff_user()
        branch = get_default_branch_location()

        user.work_branch = branch
        user.save()

        assert user.get_work_branch() == branch

    def test_get_branches_for_holds(self):
        user = get_default_staff_user()
        branch = get_default_branch_location()
        branch2 = get_default_branch_location(name="AAA")
        branch3 = get_default_branch_location(name="BBB")

        user.default_branch = branch
        user.save()

        result = user.get_branches_for_holds()
        assert len(result.keys()) == 2
        assert result["default"]["name"] == branch.name
        assert result["others"][0] == branch2.get_serialized_short_fields()
        assert result["others"][1] == branch3.get_serialized_short_fields()

    def test_get_shortened_name(self):
        user = get_default_staff_user()
        user.legal_first_name = "Sherlock"
        user.legal_last_name = "Holmes"
        user.save()

        assert user.get_shortened_name() == "Sherlock H"

    def test_shortened_name_with_mononymous_name(self):
        user = get_default_staff_user()
        user.legal_first_name = "Gandalf"
        user.legal_last_name = None
        user.save()

        assert user.get_shortened_name() == "Gandalf"

    def test_get_viewable_patrons(self):
        user = get_default_staff_user()
        assert len(user.get_viewable_patrons()) == 0
        get_default_patron_user()
        assert len(user.get_viewable_patrons()) == 1

    def test_get_viewable_patrons_from_different_hosts(self):
        """Verify that patrons from different hosts are not visible."""
        user = get_default_staff_user()
        patron = get_default_patron_user()
        patron.host = "aaaa"
        patron.save()
        assert len(user.get_viewable_patrons()) == 0

    def test_get_viewable_patrons_without_permission(self):
        perm_str = "users.read_patron_account"
        user = get_default_staff_user()
        get_default_patron_user()
        assert user.has_perm(perm_str)
        user.account_type.user_permissions.remove(perm_to_permission(perm_str))
        user.account_type.save()

        user.refresh_from_db()
        assert not user.has_perm(perm_str)
        # there's a patron here, we just can't see them
        assert user.get_viewable_patrons() == []

        # modify the permissions one more time and refetch
        user.account_type.user_permissions.add(perm_to_permission(perm_str))
        user.account_type.save()
        user.refresh_from_db()
        user = get_default_staff_user(update_permissions=False)
        assert len(user.get_viewable_patrons()) == 1

    def test_get_viewable_staff(self):
        User.objects.get(card_number=1234).delete()  # nuke the default admin account
        user = get_default_staff_user()
        # Staff can't see themselves, but superusers can
        assert len(user.get_viewable_staff()) == 0
        patron = get_default_patron_user()
        patron.account_type = AccountType.objects.get(name="Librarian")
        patron.save()
        assert len(user.get_viewable_staff()) == 1
        # superusers can see themselves
        user.account_type.is_superuser = True
        user.account_type.save()
        assert len(user.get_viewable_staff()) == 2

    def test_get_viewable_staff_from_different_hosts(self):
        """Verify that patrons from different hosts are not visible."""
        User.objects.get(card_number=1234).delete()  # nuke the default admin account
        user = get_default_staff_user()
        patron = get_default_patron_user()
        patron.account_type = AccountType.objects.get(name="Librarian")
        patron.host = "aaaa"
        patron.save()
        assert len(user.get_viewable_staff()) == 0
        user.account_type.is_superuser = True
        user.account_type.save()
        # superusers can see themselves here
        assert len(user.get_viewable_staff()) == 1

    def test_get_viewable_staff_without_permission(self):
        # Django _aggressively_ caches permissions, so even `refresh_from_db` doesn't
        # work. We have to fetch the whole object again in order to clean the cache.
        User.objects.get(card_number=1234).delete()  # nuke the default admin account
        perm_str = "users.read_staff_account"
        user = get_default_staff_user()
        patron = get_default_patron_user()
        patron.account_type = AccountType.objects.get(name="Librarian")
        patron.save()
        assert user.has_perm(perm_str)
        user.account_type.user_permissions.remove(perm_to_permission(perm_str))
        user.account_type.save()

        user.refresh_from_db()
        assert not user.has_perm(perm_str)
        # there's a staff member here, we just can't see them
        assert user.get_viewable_staff() == []

        # modify the permissions one more time and refetch
        user.account_type.user_permissions.add(perm_to_permission(perm_str))
        user.save()
        user = get_default_staff_user(update_permissions=False)
        assert len(user.get_viewable_staff()) == 1

    def test_get_viewable_permissions_groups(self):
        # default: manager permissions
        user = get_default_staff_user()
        manager = Group.objects.get(name="Manager")
        in_charge = Group.objects.get(name="In Charge")
        librarian = Group.objects.get(name="Librarian")
        circ_sup = Group.objects.get(name="Circ Supervisor")
        circ_gen = Group.objects.get(name="Circ General")
        page = Group.objects.get(name="Page")
        assert user.account_type.get_viewable_permissions_groups() == [
            manager,
            in_charge,
            librarian,
            circ_sup,
            circ_gen,
            page,
        ]

        user.account_type = AccountType.objects.get(name="Librarian")
        user.save()
        assert user.account_type.get_viewable_permissions_groups() == [librarian, page]

        user.account_type = AccountType.objects.get(name="Circ Supervisor")
        user.save()
        assert user.account_type.get_viewable_permissions_groups() == [
            in_charge,
            librarian,
            circ_sup,
            circ_gen,
            page,
        ]

        user.account_type = AccountType.objects.get(name="Page")
        user.save()
        assert user.account_type.get_viewable_permissions_groups() == []

    def test_get_viewable_permissions_groups_without_staff(self):
        user = get_default_patron_user()
        assert user.account_type.get_viewable_permissions_groups() == []

    def test_get_all_itemtype_checkout_limits(self):
        user = get_default_patron_user()
        itemtype = get_default_item_type()
        accounttype = AccountType.objects.create(name="Testing")
        accounttype.set_itemtype_checkout_limit(itemtype, 1000)
        user.account_type = accounttype
        user.save()

        assert user.account_type.get_all_itemtype_checkout_limits() == {itemtype: 1000}

    def test_get_all_itemtype_hold_limits(self):
        user = get_default_patron_user()
        itemtype = get_default_item_type()
        accounttype = AccountType.objects.create(name="Testing")
        accounttype.set_itemtype_hold_limit(itemtype, 1000)
        user.account_type = accounttype
        user.save()

        assert user.account_type.get_all_itemtype_hold_limits() == {itemtype: 1000}

    def test_can_checkout_item(self):
        user = get_default_patron_user()
        item = get_test_item()
        # this is a clean item. This should work.
        assert user.can_checkout_item(item)[0]

    def test_can_checkout_item_inactive_item(self):
        user = get_default_patron_user()
        item = get_test_item()

        item.is_active = False
        item.save()

        assert not user.can_checkout_item(item)[0]

    def test_can_checkout_item_noncirculating_item(self):
        user = get_default_patron_user()
        item = get_test_item()

        item.can_circulate = False
        item.save()

        assert not user.can_checkout_item(item)[0]

    def test_can_checkout_item_noncirculating_collection_item(self):
        user = get_default_patron_user()
        collection = get_default_collection()
        item = get_test_item(collection=collection)
        item.collection.can_circulate = False
        item.save()

        assert not user.can_checkout_item(item)[0]

    def test_can_checkout_item_blocked_account(self):
        user = get_default_patron_user()
        item = get_test_item()

        user.account_type.can_checkout_materials = False
        user.save()

        assert not user.can_checkout_item(item)[0]

    def test_can_checkout_item_blocked_itemtype(self):
        user = get_default_patron_user()
        item = get_test_item()

        user.account_type.allowed_item_types.set([])
        user.save()

        assert not user.can_checkout_item(item)[0]

    def test_can_checkout_item_at_limits(self):
        user = get_default_patron_user()
        item = get_test_item()

        user.account_type.set_itemtype_checkout_limit(item.type, 0)
        assert user.account_type.get_itemtype_checkout_limit(item.type) == 0

        assert not user.can_checkout_item(item)[0]

    def test_can_checkout_item_wrong_host(self):
        user = get_default_patron_user()
        item = get_test_item()
        item.host = "asdf.com"
        item.save()

        assert not user.can_checkout_item(item)[0]

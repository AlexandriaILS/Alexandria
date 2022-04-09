import pytest
from django.db.models import QuerySet

from alexandria.users.models import BranchLocation, User, USLocation
from alexandria.utils.test_helpers import (
    get_default_branch_location,
    get_default_patron_user, get_default_staff_user,
)


class TestCreateUser:
    def test_create_user_with_minimum_info(self):
        new_user = User.objects.create_user(
            card_number="aaaa", email="a@a.com", first_name="A"
        )
        assert new_user.email == "a@a.com"
        assert new_user.card_number == "aaaa"
        assert new_user.first_name == "A"
        assert new_user.get_shortened_name() == "A"
        assert new_user.is_staff is False
        assert new_user.is_superuser is False

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
                card_number=values[0], email=values[1], first_name=values[2]
            )

    def test_create_superuser(self):
        new_user = User.objects.create_superuser(
            card_number="aaaa", email="a@a.com", first_name="A"
        )
        assert new_user.is_staff is True
        assert new_user.is_superuser is True

    def test_create_superuser_fails_with_overridden_flags_1(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                card_number="aaaa", email="a@a.com", first_name="A", is_staff=False
            )

    def test_create_superuser_fails_with_overridden_flags_2(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                card_number="aaaa", email="a@a.com", first_name="A", is_superuser=False
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
        get_default_branch_location()

        assert user.get_serializable_branches() == [
            {"address__address_1": None, "id": 5, "name": "Central Library"}
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
        assert result['default']['name'] == branch.name
        assert result['others'][0] == branch2.get_serialized_short_fields()
        assert result['others'][1] == branch3.get_serialized_short_fields()

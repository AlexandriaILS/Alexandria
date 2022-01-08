from typing import Dict

from alexandria.users.models import BranchLocation, User

DEFAULT_STAFF_USER = {
    "card_number": 1234,
    "first_name": "Guy",
    "last_name": "Montag",
    "is_staff": True,
}

DEFAULT_PATRON_USER = {
    "card_number": 2345,
    "first_name": "Guy",
    "last_name": "Montag",
}


DEFAULT_UNDERAGE_PATRON_USER = {
    "card_number": 3456,
    "first_name": "Augustus",
    "last_name": "Gloop",
    "birth_year": 2012,
    "is_minor": True,
}


def get_default_location():
    obj, _ = BranchLocation.objects.get_or_create(name="Central Library")
    return obj


def _get_user(base_data: Dict, **kwargs) -> User:
    user_info = {
        **base_data,
        **{key: kwargs[key] for key in kwargs if key in dir(User)},
    }
    user, _ = User.objects.get_or_create(**user_info)
    return user


def get_default_staff_user(**kwargs):
    return _get_user(DEFAULT_STAFF_USER, **kwargs)


def get_default_patron_user(**kwargs):
    return _get_user(DEFAULT_PATRON_USER, **kwargs)


def get_default_underage_patron_user(**kwargs):
    return _get_user(DEFAULT_UNDERAGE_PATRON_USER, **kwargs)

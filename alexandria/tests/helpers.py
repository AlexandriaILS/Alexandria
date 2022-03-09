from typing import Dict

from alexandria.records.models import Record, Item, ItemType, ItemTypeBase, Hold
from alexandria.users.models import BranchLocation, User, AccountType

DEFAULT_STAFF_USER = {
    "card_number": "1234",
    "first_name": "Guy",
    "last_name": "Montag",
    "is_staff": True,
    "password": "lightitup",
}
DEFAULT_PATRON_USER = {
    "card_number": "2345",
    "first_name": "Fitzwilliam",
    "last_name": "Darcy",
    "password": "misunderst00ddefect",
}
DEFAULT_UNDERAGE_PATRON_USER = {
    "card_number": "3456",
    "first_name": "Augustus",
    "last_name": "Gloop",
    "birth_year": 2012,
    "is_minor": True,
    "password": "chocolateriver4me",
}
DEFAULT_US_LOCATION = {
    "address_1": "123 Main St",
    "address_2": None,
    "city": "Anywhere",
    "state": "ZZ",
    "zip_code": "00000",
}
DEFAULT_BRANCH_LOCATION = {"name": "Central Library"}
DEFAULT_ACCOUNT_TYPE = {"name": "Default"}
DEFAULT_RECORD = {"title": "Test Record"}
DEFAULT_ITEM_TYPE = {"name": "Book"}


def get_default_item_type(**kwargs):
    if not "base" in kwargs:
        kwargs["base"] = ItemTypeBase.objects.get(id=1)
    data = {
        **DEFAULT_ITEM_TYPE,
        **{key: kwargs[key] for key in kwargs if key in dir(ItemType)},
    }
    obj, _ = ItemType.objects.get_or_create(**data)
    return obj


def get_default_record(**kwargs):
    data = {
        **DEFAULT_RECORD,
        **{key: kwargs[key] for key in kwargs if key in dir(Record)},
    }
    obj, _ = Record.objects.get_or_create(**data)
    return obj


def get_test_item(**kwargs):
    DEFAULT_ITEM = {
        "type": get_default_item_type(),
        "record": get_default_record(),
        "is_active": True,
    }
    data = {
        **DEFAULT_ITEM,
        **{key: kwargs[key] for key in kwargs if key in dir(Item)},
    }
    return Item.objects.create(**data)


def get_default_location(**kwargs):
    data = {
        **DEFAULT_BRANCH_LOCATION,
        **{key: kwargs[key] for key in kwargs if key in dir(BranchLocation)},
    }
    obj, _ = BranchLocation.objects.get_or_create(**data)
    return obj


def get_default_accounttype(**kwargs):
    data = {
        **DEFAULT_ACCOUNT_TYPE,
        **{key: kwargs[key] for key in kwargs if key in dir(AccountType)},
    }
    obj, _ = AccountType.objects.get_or_create(**data)
    return obj


def get_default_hold(**kwargs):
    DEFAULT_HOLD = {
        "placed_for": get_default_patron_user(),
        "destination": get_default_location(),
        "item": get_test_item(),
    }
    data = {
        **DEFAULT_HOLD,
        **{key: kwargs[key] for key in kwargs if key in dir(Hold)},
    }
    obj, _ = Hold.objects.get_or_create(**data)


def _get_user(base_data: Dict, **kwargs) -> User:
    user_info = {
        **base_data,
        **{key: kwargs[key] for key in kwargs if key in dir(User)},
    }
    user, _ = User.objects.get_or_create(**user_info)
    user.account_type = get_default_accounttype()
    user.set_password(user_info["password"])
    user.save()
    return user


def get_default_staff_user(**kwargs):
    return _get_user(DEFAULT_STAFF_USER, **kwargs)


def get_default_patron_user(**kwargs):
    return _get_user(DEFAULT_PATRON_USER, **kwargs)


def get_default_underage_patron_user(**kwargs):
    return _get_user(DEFAULT_UNDERAGE_PATRON_USER, **kwargs)

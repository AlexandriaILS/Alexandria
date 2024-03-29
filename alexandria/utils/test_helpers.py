from typing import Dict

from alexandria.distributed.models import Domain
from alexandria.records.models import (
    Collection,
    Hold,
    Item,
    ItemType,
    ItemTypeBase,
    Record,
)
from alexandria.users.models import AccountType, BranchLocation, User

DEFAULT_SUPERUSER = {
    "card_number": "123444",
    "legal_first_name": "Atticus",
    "legal_last_name": "Finch",
    "password": "headhighfistsdown",
}
DEFAULT_STAFF_USER = {
    "card_number": "2345",  # existing Admin user is 1234
    "legal_first_name": "Guy",
    "legal_last_name": "Montag",
    "password": "l1ght1tup",
}
DEFAULT_PATRON_USER = {
    "card_number": "3456",
    "legal_first_name": "Fitzwilliam",
    "legal_last_name": "Darcy",
    "password": "misunderst00ddefect",
}
DEFAULT_UNDERAGE_PATRON_USER = {
    "card_number": "4567",
    "legal_first_name": "Augustus",
    "legal_last_name": "Gloop",
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
DEFAULT_COLLECTION = {"name": "Coolest Books"}
DEFAULT_ACCOUNT_TYPE = {"name": "Default"}
DEFAULT_RECORD = {"title": "Test Record"}
DEFAULT_ITEM_TYPE = {"name": "Book"}
DEFAULT_DOMAIN = {"name": "example.com"}


def get_default_item_type(**kwargs):
    if not "base" in kwargs:
        kwargs["base"] = ItemTypeBase.objects.get(name=ItemTypeBase.LANGUAGE_MATERIAL)
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


def get_default_domain(**kwargs):
    data = {
        **DEFAULT_DOMAIN,
        **{key: kwargs[key] for key in kwargs if key in dir(Domain)},
    }
    obj, _ = Domain.objects.get_or_create(**data)
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


def get_default_branch_location(**kwargs):
    data = {
        **DEFAULT_BRANCH_LOCATION,
        **{key: kwargs[key] for key in kwargs if key in dir(BranchLocation)},
    }
    obj, _ = BranchLocation.objects.get_or_create(**data)
    return obj


def get_default_accounttype(**kwargs):
    allowed_item_types: list[ItemType] = kwargs.pop(
        "allowed_item_types", [get_default_item_type()]
    )
    data = {
        **DEFAULT_ACCOUNT_TYPE,
        **{key: kwargs[key] for key in kwargs if key in dir(AccountType)},
    }
    obj, _ = AccountType.objects.get_or_create(**data)
    obj.allowed_item_types.set(allowed_item_types)
    obj.save()

    return obj


def get_default_collection(**kwargs):
    data = {
        **DEFAULT_COLLECTION,
        **{key: kwargs[key] for key in kwargs if key in dir(Collection)},
    }
    obj, _ = Collection.objects.get_or_create(**data)
    return obj


def get_default_hold(**kwargs):
    DEFAULT_HOLD = {
        "placed_for": get_default_patron_user(),
        "destination": get_default_branch_location(),
        "item": get_test_item(),
    }
    data = {
        **DEFAULT_HOLD,
        **{key: kwargs[key] for key in kwargs if key in dir(Hold)},
    }
    obj, _ = Hold.objects.get_or_create(**data)
    return obj


def _get_user(base_data: Dict, **kwargs) -> User:
    user_info = {
        **base_data,
        **{key: kwargs[key] for key in kwargs if key in dir(User)},
    }
    if "account_type" not in user_info:
        user_info.update({"account_type": get_default_accounttype()})
    if not User.objects.filter(card_number=user_info["card_number"]).exists():
        user = User.objects.create(**user_info)
    else:
        # perform the update in the db without actually getting the object; much faster
        User.objects.filter(card_number=user_info["card_number"]).update(**user_info)
        # now get the updated object
        user = User.objects.get(card_number=user_info["card_number"])

    user.account_type = get_default_accounttype()
    user.set_password(user_info["password"])
    user.save()
    return user


def get_default_staff_user(**kwargs):
    """Set update_permissions as false to just pull the staff user."""
    user = _get_user(DEFAULT_STAFF_USER, **kwargs)
    user.account_type = AccountType.objects.get(name="Manager")
    user.save()
    return user


def get_default_patron_user(**kwargs):
    return _get_user(DEFAULT_PATRON_USER, **kwargs)


def get_default_underage_patron_user(**kwargs):
    return _get_user(DEFAULT_UNDERAGE_PATRON_USER, **kwargs)


def get_superuser(**kwargs):
    user = _get_user(DEFAULT_SUPERUSER, **kwargs)
    user.account_type = AccountType.objects.get(name="Superuser")
    user.save()
    return user

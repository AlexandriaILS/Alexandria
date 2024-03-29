from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, List

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import send_mail
from django.db import models
from django.db.models import QuerySet
from django.forms import Form
from django.template import loader
from django.utils import timezone
from django.utils.translation import gettext as _
from localflavor.us.models import USStateField, USZipCodeField

from alexandria.distributed.models import Domain, Setting
from alexandria.searchablefields.mixins import SearchableFieldMixin
from alexandria.utils.models import TimeStampMixin
from alexandria.utils.permissions import perm_to_permission
from alexandria.utils.type_hints import Manager

if TYPE_CHECKING:
    from alexandria.records.models import CheckoutSession, Item, ItemType

BRANCH_SERIALIZER_SHORT_FIELDS = ["id", "name", "address__address_1"]
CHECKOUT_SUCCESS = _("Checkout successful!")


def get_default_accounttype() -> User:
    model = apps.get_model("users", "AccountType")
    return model.objects.get_or_create(name="Disabled")[0]


class UserManager(DjangoUserManager):
    use_in_migrations = True

    def _create_user(
        self,
        card_number=None,
        email=None,
        password=None,
        legal_first_name=None,
        **extra_fields,
    ) -> User:
        """
        Create and save a user with the given username, email, and password.

        Note: traditionally card numbers are, as the name implies, numbers, but
        there is a possibility that it might not be. Ergo, we don't check for
        whether it's a number or not.
        """
        if not card_number:
            raise ValueError("Card number must be set")
        if not email:
            raise ValueError("Email address must be set")
        if not legal_first_name:
            raise ValueError("First name must be set")
        email = self.normalize_email(email)
        user = self.model(
            card_number=card_number,
            email=email,
            legal_first_name=legal_first_name,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        card_number: str,
        email: str = None,
        password: str = None,
        **extra_fields: dict,
    ) -> User:
        extra_fields["account_type"] = AccountType.objects.get_or_create(
            name="Default"
        )[0]
        return self._create_user(card_number, email, password, **extra_fields)

    def create_superuser(
        self,
        card_number: str,
        email: str = None,
        password: str = None,
        **extra_fields: dict,
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        extra_fields["account_type"] = AccountType.objects.get_or_create(
            name="Superuser", is_staff=True, is_superuser=True
        )[0]
        del extra_fields["is_staff"]
        del extra_fields["is_superuser"]

        return self._create_user(card_number, email, password, **extra_fields)


class USLocation(TimeStampMixin):
    # https://stackoverflow.com/a/7701297
    address_1 = models.CharField(_("Address"), max_length=128)
    address_2 = models.CharField(_("Address cont'd"), max_length=128, blank=True)

    city = models.CharField(_("City"), max_length=64, null=True, blank=True)
    state = USStateField(_("State"), null=True, blank=True)
    zip_code = USZipCodeField(_("Zip Code"), null=True, blank=True)
    host = models.ForeignKey(
        Domain, on_delete=models.CASCADE, default=Domain.get_default_pk
    )

    class Meta:
        verbose_name = "US Location"
        verbose_name_plural = "US Locations"

    def __str__(self) -> str:
        addy = f"{self.address_1}"
        if self.address_2:
            addy += f" {self.address_2}"
        addy += f", {self.city}, {self.state} {self.zip_code}"
        return addy


class BranchLocation(TimeStampMixin):
    name = models.CharField(max_length=150)
    address = models.ForeignKey(
        USLocation, on_delete=models.CASCADE, null=True, blank=True
    )
    checkouts = GenericRelation(
        "records.Item", related_query_name="branch_checked_out_to"
    )
    open_to_public = models.BooleanField(
        _("open to public"),
        default=True,
        help_text=_(
            "Set to false if this building is staff-only or a processing center."
        ),
    )
    host = models.ForeignKey(
        Domain, on_delete=models.CASCADE, default=Domain.get_default_pk
    )

    def __str__(self) -> str:
        if self.address:
            return f"{self.name} - {self.address.address_1}"
        return f"{self.name}"

    def get_serialized_short_fields(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "address__address_1": self.address.address_1 if self.address else None,
        }

    def can_checkout_item(self, *args) -> tuple[bool, str]:
        # This is only called when checking out an item to a branchlocation; as
        # buildings have far less restrictions than patrons, you can always check
        # out something to a branchlocation.
        return True, CHECKOUT_SUCCESS

    def get_display_name(self) -> str:
        return f"{self.name}"

    @property
    def is_user(self) -> bool:
        # used for differentiating between user and branchlocation on shared FKs
        return False

    def get_transport_receipt(self, request) -> str:
        return loader.render_to_string(
            "receipts/transport.html",
            {"branch": self},
            request,
        )


class AccountType(TimeStampMixin, PermissionsMixin):
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    # stored in the format of {itemtype_id (int) : limit (int)}
    _itemtype_checkout_limits = models.JSONField(
        _("itemtype checkout limits"), default=dict
    )
    _itemtype_hold_limits = models.JSONField(_("itemtype hold limits"), default=dict)
    checkout_limit = models.IntegerField(
        _("checkout limit"),
        null=True,
        blank=True,
        default=150,
        help_text=_(
            "How many materials total is this account type allowed to have checked out?"
        ),
    )
    hold_limit = models.IntegerField(
        _("hold limit"),
        null=True,
        blank=True,
        default=50,
        help_text=_("How many active holds is this account type allowed to have?"),
    )
    allowed_item_types: Manager[ItemType] = models.ManyToManyField(
        "records.ItemType",
        help_text=_(
            "This account type will only be allowed to check out the listed item types"
            ' here. If this is empty, all item types will be allowed. Use the "Can'
            ' Checkout Materials" toggle to disable all checkouts.'
        ),
    )
    can_checkout_materials = models.BooleanField(
        default=True,
        help_text=_("Allow this account type to check out materials at all."),
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether users with this role are library staff members."
        ),
    )
    host = models.ForeignKey(
        Domain, on_delete=models.CASCADE, default=Domain.get_default_pk
    )

    class Meta:
        verbose_name = _("account type")
        verbose_name_plural = _("account types")

    def __str__(self) -> str:
        return self.name

    @property
    def is_anonymous(self) -> bool:
        # abstraction to make django happy when looking at permissions.
        return False

    def get_all_itemtype_checkout_limits(self) -> dict[ItemType, int]:
        """
        Retrieve a formatted dict with all the checkout limits by ItemType.

        Warning: this has the possibility to be fairly heavy, so use the other
        helpers to request / set single objects at a time if you can.
        """
        item_type = apps.get_model(app_label="records", model_name="ItemType")
        limits = {}
        # grab all the objects we need in one call and load them into memory
        type_objects = item_type.objects.filter(
            id__in=self._itemtype_checkout_limits.keys(), host=self.host
        )

        for model_id, value in self._itemtype_checkout_limits.items():
            limits[type_objects.get(id=model_id)] = value

        return limits

    def get_all_itemtype_hold_limits(self) -> dict[ItemType, int]:
        """
        Retrieve a formatted dict with all the hold limits by ItemType.

        Same warning as above applies here.
        """
        item_type = apps.get_model(app_label="records", model_name="ItemType")
        limits = {}
        # grab all the objects we need in one call and load them into memory
        type_objects = item_type.objects.filter(
            id__in=self._itemtype_hold_limits.keys()
        )

        for model_id, value in self._itemtype_hold_limits.items():
            limits[type_objects.get(id=model_id)] = value
        return limits

    def get_itemtype_checkout_limit(self, obj: ItemType) -> int:
        """Override how many of a particular item type can we check out at once?"""
        return self._itemtype_checkout_limits.get(
            obj.id, obj.number_of_concurrent_checkouts
        )

    def set_itemtype_checkout_limit(self, obj: ItemType, limit: int) -> None:
        self._itemtype_checkout_limits.update({obj.id: limit})
        self.save()

    def get_itemtype_hold_limit(self, obj: ItemType) -> int:
        """Override how many of this item type can we have on hold at once."""
        return self._itemtype_hold_limits.get(obj.id, obj.number_of_concurrent_holds)

    def set_itemtype_hold_limit(self, obj: ItemType, limit: int) -> None:
        self._itemtype_hold_limits.update({obj.id: limit})
        self.save()

    def update_from_form(self, form) -> None:
        for key in form.cleaned_data.keys():
            if key == "permissions":
                continue
            if hasattr(self, key):
                setattr(self, key, form.cleaned_data[key])
        self.save()

    def get_viewable_permissions_groups(self):
        if not self.is_staff:
            return []

        # these strings are the names of the groups in the db
        superuser = "Superuser"
        manager = "Manager"
        in_charge = "In Charge"
        librarian = "Librarian"
        circ_sup = "Circ Supervisor"
        circ_gen = "Circ General"
        page = "Page"

        # these are the order in which they should appear
        options = [superuser, manager, in_charge, librarian, circ_sup, circ_gen, page]

        tree = {
            superuser: options,  # everything
            manager: [o for o in options if o != superuser],
            in_charge: [in_charge, librarian, page],
            librarian: [librarian, page],
            circ_sup: [circ_sup, in_charge, librarian, circ_gen, page],
            circ_gen: [circ_gen, librarian, page],
            page: [],
        }

        perm_groups = []
        # Because all permissions are available on a singular level, we only use
        # permissions groups to keep track of default lists of permissions, not as
        # something that's assigned wholesale. Therefore, we need to approximate
        # what kinds of groups a user has by comparing the permissions that they
        # currently have assigned to the permissions available for each group.
        # We'll use that list of groups to show the buttons on the Staff Edit page
        # to set those permission group defaults.
        user_permissions = [perm_to_permission(p) for p in self.get_all_permissions()]
        groups = Group.objects.filter(name__in=options)
        for group in groups:
            group_permissions = group.permissions.all()
            if all([el in user_permissions for el in group_permissions]):
                perm_groups += tree[group.name]

        groups = groups.filter(name__in=list(set(perm_groups)))
        sorted_groups = []
        # run through the options list and put everything into the right order
        for group in options:
            sorted_groups.append(groups.filter(name=group).first())

        # clean the list
        return [group for group in sorted_groups if group is not None]


class User(AbstractBaseUser, SearchableFieldMixin, TimeStampMixin):
    # http://www.ala.org/advocacy/privacy/checklists/library-management-systems
    # Even though this should be an integer, there are too many edge cases
    # where it might not be, so we'll store it as a string with the expectation
    # that it's a very large number.

    SEARCHABLE_FIELDS = ["legal_first_name", "legal_last_name", "chosen_first_name"]

    card_number: str = models.CharField(primary_key=True, max_length=50)
    # We only need one address; no need to keep their history.
    address: USLocation = models.ForeignKey(
        USLocation, on_delete=models.CASCADE, null=True, blank=True
    )
    title: str = models.CharField(_("title"), max_length=50, null=True, blank=True)

    # first name is mandatory, last name is optional
    legal_first_name: str = models.CharField(_("legal first name"), max_length=255)
    legal_last_name: str = models.CharField(
        _("legal last name"), max_length=255, null=True, blank=True
    )
    chosen_first_name: str = models.CharField(
        _("chosen first name"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "If filled out, this will be used in place of their legal first name on all"
            " correspondence and throughout Alexandria. Does not actually modify legal"
            " first name."
        ),
    )
    email: str = models.EmailField(_("email address"), blank=True)
    is_minor: bool = models.BooleanField(
        default=False,
        help_text=_(
            "Check if the person this account belongs to is legally considered a minor."
        ),
    )
    birth_year: int = models.IntegerField(
        _("birth year"),
        blank=True,
        null=True,
        help_text=_(
            "If allowed, enter the year of birth for the patron."
            " Helps differentiate between patrons with the same name."
        ),
    )

    notes: str = models.TextField(_("notes"), blank=True, null=True)

    is_active: bool = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined: datetime = models.DateTimeField(_("date joined"), default=timezone.now)

    checkouts: Manager[Item] = GenericRelation(
        "records.Item", related_query_name="user_checked_out_to"
    )
    checkout_session: Manager[CheckoutSession] = GenericRelation(
        "records.CheckoutSession", related_query_name="user_session_target"
    )
    # if context.enable_running_borrow_saved_money is enabled, the prices of each item
    # will be summed and added to this field on every checkout.
    saved_money = models.IntegerField(default=0)
    host = models.ForeignKey(
        Domain, on_delete=models.CASCADE, default=Domain.get_default_pk
    )
    # for setting holds
    default_branch: BranchLocation = models.ForeignKey(
        BranchLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_branch",
    )
    # employees need a default branch to be assigned to
    work_branch: BranchLocation = models.ForeignKey(
        BranchLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_location",
    )

    account_type: AccountType = models.ForeignKey(
        AccountType, on_delete=models.SET(get_default_accounttype)
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "card_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return str(self.card_number)

    def save(self, *args, **kwargs) -> None:
        self.update_searchable_fields()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        permissions = [
            # changed keyword from update -> change to keep with django convention
            ("create_patron_account", _("Can create a patron account")),
            ("read_patron_account", _("Can see patron account data")),
            ("change_patron_account", _("Can change patron account information")),
            ("delete_patron_account", _("Can delete patron accounts")),
            ("edit_user_notes", _("Can edit user notes field")),
            ("create_staff_account", _("Can create a staff account")),
            ("read_staff_account", _("Can see staff account data")),
            ("change_staff_account", _("Can change staff account information")),
            ("delete_staff_account", _("Can delete staff accounts")),
            (
                "generate_financial_reports",
                _("Can generate reports with financial data"),
            ),
            (
                "generate_general_reports",
                _("Can generate reports on anything non-financial"),
            ),
        ]

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_branches(self, get_all: bool = False) -> QuerySet[BranchLocation]:
        args = {"host": self.host}
        if not get_all:
            args |= {"open_to_public": True}

        return BranchLocation.objects.filter(**args).order_by("name")

    def get_serializable_branches(self) -> list:
        return list(self.get_branches().values(*BRANCH_SERIALIZER_SHORT_FIELDS))

    def get_default_branch(self) -> BranchLocation:
        if not self.default_branch:
            # this shouldn't really happen, but we can at least correct for it if it does
            self.default_branch = BranchLocation.objects.get(
                id=Setting.get(Setting.options.DEFAULT_LOCATION_ID, host=self.host),
                host=self.host,
            )
            self.save()
        return self.default_branch

    def get_work_branch(self) -> BranchLocation | None:
        # Return the default working branch for a staff user.
        if not self.account_type.is_staff:
            return None
        if not self.work_branch:
            self.work_branch = BranchLocation.objects.get(
                id=Setting.get(Setting.options.DEFAULT_LOCATION_ID, host=self.host)
            )
            self.save()
        return self.work_branch

    def get_branches_for_holds(
        self,
    ) -> dict[str, BranchLocation | list[BranchLocation]]:
        # Return a dict where the user default is directly available.
        # wrap default in queryset
        default_branch = BranchLocation.objects.filter(id=self.get_default_branch().id)
        branches = self.get_branches().exclude(pk__in=default_branch).order_by("name")
        return {
            "default": default_branch.first().get_serialized_short_fields(),
            "others": [branch.get_serialized_short_fields() for branch in branches],
        }

    def get_branches_for_checkin_checkout(
        self,
    ) -> dict[str, BranchLocation | list[BranchLocation]]:
        default_branch = BranchLocation.objects.filter(id=self.get_default_branch().id)
        branches = (
            self.get_branches(get_all=True)
            .exclude(pk__in=default_branch)
            .order_by("name")
        )
        return {
            "default": default_branch.first().get_serialized_short_fields(),
            "others": [branch.get_serialized_short_fields() for branch in branches],
        }

    def get_system_branches(self) -> QuerySet[BranchLocation]:
        # formats system branches using the `branch_dropdown_with_default_on_top`
        # template.
        return BranchLocation.objects.filter(host=Domain.get_system()).order_by("name")

    def _get_users(self, is_staff: bool) -> QuerySet[User]:
        qs = User.objects.filter(account_type__is_staff=is_staff, host=self.host)
        if not self.account_type.is_superuser:
            # superusers can edit themselves
            qs = qs.exclude(card_number=self)

        return qs.order_by("legal_last_name", "legal_first_name")

    def _abbreviate_name(self, name: str = None) -> str:
        """Take a name and abbreviate it. Defaults to last name."""
        target = name if name else self.legal_last_name
        return "".join([n[0] for n in target.split()])

    def get_first_name(self) -> str:
        return (
            self.chosen_first_name if self.chosen_first_name else self.legal_first_name
        )

    def get_shortened_name(self) -> str:
        """
        Return first name and initial of last name.

        Also accounts for last names with multiple words like "Von Person". Returns just
        the first name if the given account does not have a last name.
        """
        # https://english.stackexchange.com/a/413015
        name = self.get_first_name()

        if self.legal_last_name:
            name += f" {self._abbreviate_name()}"

        return name

    def get_display_name(self) -> str:
        name = self.get_first_name()

        if self.legal_last_name:
            name += f" {self.legal_last_name}"

        return name

    def update_from_form(self, form: Form) -> None:
        """Grab all the form data, split out the address info, and save it all."""
        for key in form.cleaned_data.keys():
            if hasattr(self, key):
                setattr(self, key, form.cleaned_data[key])

        # the rest of these are related to the address FK
        unhandled_keys = [i for i in form.cleaned_data.keys() if i not in dir(self)]
        for key in unhandled_keys:
            if hasattr(self.address, key):
                setattr(self.address, key, form.cleaned_data[key])

        self.address.save()
        self.save()

    def get_viewable_staff(self) -> QuerySet[User] | list:
        # used to populate user management page
        if self.account_type.has_perm("users.read_staff_account"):
            return self._get_users(is_staff=True)
        return []

    def get_viewable_patrons(self) -> QuerySet[User] | list:
        # Similar to self.get_viewable_staff, but for patrons only.
        if self.account_type.has_perm("users.read_patron_account"):
            return self._get_users(is_staff=False)
        return []

    def get_account_types(self) -> QuerySet[AccountType]:
        return AccountType.objects.filter(host=self.host)

    def get_checkouts(self) -> QuerySet[Item]:
        return self.checkouts.all()

    def get_active_checkout_session(self) -> CheckoutSession | None:
        checkout_model = apps.get_model("records.CheckoutSession")
        return checkout_model.objects.filter(session_user=self).first()

    def can_checkout_item(self, item: Item) -> tuple[bool, str]:
        """
        Check to see if the user can check out this particular item.

        The messages contained here are passed directly to the staff front end
        in the event of a failure.
        """
        if item.host != self.host:
            # We know about this item, but it's not part of this system.
            # How did it even get here?
            # TODO: Adjust this check for federated library systems
            return False, _("This item belongs to a different library.")

        if not self.account_type.can_checkout_materials:
            # They aren't allowed to check out anything at all. Abort!
            return False, _("This user is not allowed to check out materials.")

        if not item.is_active or not item.can_circulate:
            # How did they even get this thing?
            return False, _("This item is not allowed to circulate.")

        if item.collection:
            if not item.collection.can_circulate:
                # this is part of a special group. No circulating for you.
                return False, _(
                    "This item is part of a special collection that is not allowed to"
                    " circulate."
                )

        itemtype = item.type

        if itemtype not in self.account_type.allowed_item_types.all():
            # whoops. They can check out some things, but not this thing!
            return False, _("This user is not allowed to check out this type of item.")

        itemtype_count = self.get_checkouts().filter(type=itemtype).count()
        if itemtype_count >= self.account_type.get_itemtype_checkout_limit(itemtype):
            # Sorry, at the limit for what you can check out for this type.
            return False, _(
                "This user cannot check out more of this type of item until they return"
                " some."
            )

        # Guess you're good to go!
        # We don't actually need the message here, only if it fails
        return True, CHECKOUT_SUCCESS

    def get_hold_receipt_header(self):
        """
        Return a formatted header for the hold receipts.

        Example: for Admin von Admin with card number 1234567890123, return vA - 890123
        """
        if self.legal_last_name:
            name = self._abbreviate_name()
        else:
            name = self._abbreviate_name(name=self.get_first_name())

        return f"{name} - {self.card_number[-6:]}"

    ###
    # Abstractions
    ###

    @property
    def is_user(self) -> bool:
        # used for differentiating between user and branchlocation on shared FKs
        return True

    @property
    def is_staff(self) -> bool:
        return self.account_type.is_staff

    @property
    def is_superuser(self) -> bool:
        return self.account_type.is_superuser

    @property
    def groups(self):
        return self.account_type.groups

    @property
    def user_permissions(self):
        return self.account_type.user_permissions

    def has_perm(self, *args, **kwargs) -> bool:
        return self.account_type.has_perm(*args, **kwargs)

    def has_perms(self, *args, **kwargs):
        return self.account_type.has_perms(*args, **kwargs)

    def has_module_perms(self, *args, **kwargs):
        return self.account_type.has_module_perms(*args, **kwargs)

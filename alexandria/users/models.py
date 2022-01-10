from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    Group,
)
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import send_mail
from django.db import models
from django.conf import settings
from django.forms import Form
from django.utils import timezone
from django.utils.translation import gettext as _
from localflavor.us.models import USStateField, USZipCodeField

from alexandria.distributed.configs import load_site_config
from alexandria.searchablefields.mixins import SearchableFieldMixin
from alexandria.utils.permissions import perm_to_permission


class UserManager(DjangoUserManager):
    use_in_migrations = True

    def _create_user(self, card_number, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not card_number:
            raise ValueError("The given card_number must be set")
        email = self.normalize_email(email)
        card_number = int(card_number)
        user = self.model(card_number=card_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, card_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(card_number, email, password, **extra_fields)

    def create_superuser(self, card_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(card_number, email, password, **extra_fields)


class USLocation(models.Model):
    # https://stackoverflow.com/a/7701297
    address_1 = models.CharField(_("Address"), max_length=128)
    address_2 = models.CharField(_("Address cont'd"), max_length=128, blank=True)

    city = models.CharField(_("City"), max_length=64, null=True, blank=True)
    state = USStateField(_("State"), null=True, blank=True)
    zip_code = USZipCodeField(_("Zip Code"), null=True, blank=True)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    class Meta:
        verbose_name = "US Location"
        verbose_name_plural = "US Locations"

    def __str__(self):
        addy = f"{self.address_1}"
        if self.address_2:
            addy += f" {self.address_2}"
        addy += f", {self.city}, {self.state} {self.zip_code}"
        return addy


class BranchLocation(models.Model):
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
        help_text="Set to false if this building is staff-only or a processing center.",
    )
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        if self.address:
            return f"{self.name} - {self.address.address_1}"
        return f"{self.name}"


class User(AbstractBaseUser, PermissionsMixin, SearchableFieldMixin):
    # http://www.ala.org/advocacy/privacy/checklists/library-management-systems
    # Even though this should be an integer, there are too many edge cases
    # where it might not be, so we'll store it as a string with the expectation
    # that it's a very large number.

    SEARCHABLE_FIELDS = ["first_name", "last_name"]

    card_number = models.CharField(primary_key=True, max_length=50)
    # We only need one address; no need to keep their history.
    address = models.ForeignKey(
        USLocation, on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(_("title"), max_length=50, null=True, blank=True)

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True)
    is_minor = models.BooleanField(
        default=False,
        help_text=_(
            "Check if the person this account belongs to is legally considered a minor."
        ),
    )
    birth_year = models.IntegerField(
        _("birth year"),
        blank=True,
        null=True,
        help_text=_(
            "If allowed, enter the year of birth for the patron."
            " Helps differentiate between patrons with the same name."
        ),
    )

    notes = models.TextField(_("notes"), blank=True, null=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user is a library staff member."),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    checkouts = GenericRelation(
        "records.Item", related_query_name="user_checked_out_to"
    )
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)
    # for setting holds
    default_branch = models.ForeignKey(
        BranchLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="default_branch",
    )
    # employees need a default branch to be assigned to
    work_branch = models.ForeignKey(
        BranchLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_location",
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "card_number"
    REQUIRED_FIELDS = []

    SERIALIZER_SHORT_FIELDS = ["id", "name", "address__address_1"]

    objects = UserManager()

    def __str__(self):
        return str(self.card_number)

    def save(self, *args, **kwargs):
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

    def get_branches(self):
        return BranchLocation.objects.filter(
            host=self.host, open_to_public=True
        ).order_by("name")

    def get_serializable_branches(self) -> list:
        return list(self.get_branches().values(*self.SERIALIZER_SHORT_FIELDS))

    def get_default_branch(self):
        if not self.default_branch:
            # this shouldn't really happen, but we can at least correct for it if it does
            self.default_branch = BranchLocation.objects.get(
                id=load_site_config(self.host)["default_location_id"]
            )
            self.save()
        return self.default_branch

    def get_work_branch(self):
        # Return the default working branch for a staff user.
        if not self.is_staff:
            return None
        if not self.work_branch:
            self.work_branch = BranchLocation.objects.get(
                id=load_site_config(self.host)["default_location_id"]
            )
            self.save()
        return self.work_branch

    def get_branches_for_holds(self):
        # Return a dict where the user default is directly available.
        # wrap default in queryset
        default_branch = BranchLocation.objects.filter(id=self.get_default_branch().id)
        branches = self.get_branches().exclude(pk__in=default_branch).order_by("name")
        data = {
            "default": default_branch.values(*self.SERIALIZER_SHORT_FIELDS)[0],
            "others": branches.values(*self.SERIALIZER_SHORT_FIELDS),
        }
        return data

    def _get_users(self, is_staff):
        if self.is_superuser:
            qs = User.objects.filter(is_staff=is_staff)
        else:
            qs = User.objects.filter(
                is_staff=is_staff, host=self.host
            ).exclude(card_number=self)
        return qs.order_by("last_name", "first_name")

    def get_shortened_name(self):
        """
        Return first name and initial of last name.

        Also accounts for last names with multiple words like "Von Person".
        """

        # https://english.stackexchange.com/a/413015
        return (
            f"{self.first_name} {''.join([name[0] for name in self.last_name.split()])}"
        )

    def update_from_form(self, form: Form) -> None:
        """Grab all the form data, split out the address info, and save it all."""
        for key in form.cleaned_data.keys():
            if key == "permissions":
                continue
            if hasattr(self, key):
                setattr(self, key, form.cleaned_data[key])

        # the rest of these are related to the address FK
        unhandled_keys = [i for i in form.cleaned_data.keys() if i not in dir(self)]
        for key in unhandled_keys:
            if hasattr(self.address, key):
                setattr(self.address, key, form.cleaned_data[key])

        self.address.save()
        self.save()

    def get_modifiable_staff(self):
        # used to populate user management page
        if self.has_perm("users.change_staff_account"):
            return self._get_users(is_staff=True)
        return []

    def get_modifiable_patrons(self):
        # Similar to self.get_modifiable_users, but for patrons only.
        if self.has_perm("users.change_patron_account"):
            return self._get_users(is_staff=False)
        return []

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

    def get_checked_out_materials(self):
        return self.checkouts.all()

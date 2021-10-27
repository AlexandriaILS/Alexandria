from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import send_mail
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _
from localflavor.us.models import USStateField, USZipCodeField

from alexandria.configs import load_site_config


class AlexandriaUserManager(UserManager):
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
    state = USStateField(null=True, blank=True)
    zip_code = USZipCodeField(null=True, blank=True)
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
        "catalog.Item", related_query_name="branch_checked_out_to"
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


class AlexandriaUser(AbstractBaseUser, PermissionsMixin):
    # http://www.ala.org/advocacy/privacy/checklists/library-management-systems
    # Even though this should be an integer, there are too many edge cases
    # where it might not be, so we'll store it as a string with the expectation
    # that it's a very large number.
    card_number = models.CharField(primary_key=True, max_length=50)
    # We only need one address, no need to keep their history.
    address = models.ForeignKey(
        USLocation, on_delete=models.CASCADE, null=True, blank=True
    )

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

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user is a library staff member."),
    )

    is_manager = models.BooleanField(
        _("manager status"),
        default=False,
        help_text=_(
            "Designates whether the user is a library manager with additional"
            " permissions."
        ),
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
        "catalog.Item", related_query_name="user_checked_out_to"
    )
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)
    default_branch = models.ForeignKey(
        BranchLocation, on_delete=models.SET_NULL, null=True, blank=True
    )

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "card_number"
    REQUIRED_FIELDS = []

    SERIALIZER_SHORT_FIELDS = ["id", "name", "address__address_1"]

    objects = AlexandriaUserManager()

    def __str__(self):
        return str(self.card_number)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

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
                id=load_site_config(self.host)['default_location_id']
            )
            self.save()
        return self.default_branch

    def get_branches_for_holds(self):
        # Return a dict where the user default is directly available.
        # wrap default in queryset
        default_branch = BranchLocation.objects.filter(id=self.get_default_branch().id)
        branches = self.get_branches().exclude(pk__in=default_branch)
        data = {
            "default": default_branch.values(*self.SERIALIZER_SHORT_FIELDS)[0],
            "others": branches.values(*self.SERIALIZER_SHORT_FIELDS)
        }
        return data

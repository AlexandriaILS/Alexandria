from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from localflavor.us.models import USStateField, USZipCodeField


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

    city = models.CharField(
        _("City"), max_length=64, default=settings.DEFAULT_ADDRESS_CITY
    )
    state = USStateField(default=settings.DEFAULT_ADDRESS_STATE_OR_REGION)
    zip_code = USZipCodeField(default=settings.DEFAULT_ADDRESS_ZIP_CODE)

    class Meta:
        verbose_name = "US Location"
        verbose_name_plural = "US Locations"

    def __str__(self):
        addy = f"{self.address_1}"
        if self.address_2:
            addy += f" {self.address_2}"
        addy += f", {self.city}, {self.state} {self.zip_code}"
        return addy


class AlexandriaUser(AbstractBaseUser, PermissionsMixin):
    # http://www.ala.org/advocacy/privacy/checklists/library-management-systems
    card_number = models.IntegerField(primary_key=True)
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

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "card_number"
    REQUIRED_FIELDS = []

    objects = AlexandriaUserManager()

    def __str__(self):
        return str(self.card_number)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class BranchLocation(models.Model):
    name = models.CharField(max_length=150)
    address = models.ForeignKey(
        USLocation, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        if self.address:
            return f"{self.name} - {self.address.address_1}"
        return f"{self.name}"

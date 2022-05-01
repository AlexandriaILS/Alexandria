import re
import zoneinfo
from datetime import date, timedelta

import pymarc
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType as DjangoContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from taggit.managers import TaggableManager

from alexandria.records import openlibrary
from alexandria.records.mixins import CoverUtilitiesMixin
from alexandria.searchablefields.mixins import SearchableFieldMixin
from alexandria.users.models import BranchLocation, User
from alexandria.utils.models import TimeStampMixin

UTC = zoneinfo.ZoneInfo("UTC")


class Subject(TimeStampMixin, SearchableFieldMixin):
    SEARCHABLE_FIELDS = ["name"]

    # look, sometimes people are more wordy than they need to be, that's all I'm saying
    name = models.CharField(max_length=500)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.update_searchable_fields()
        super().save(*args, **kwargs)


class Collection(TimeStampMixin):
    name = models.CharField(max_length=200)
    home = models.ForeignKey(
        BranchLocation, null=True, blank=True, on_delete=models.CASCADE
    )
    can_circulate = models.BooleanField(default=True)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        return self.name


class BibliographicLevel(models.Model):
    MONOGRAPHIC_COMPONENT_PART = "a"
    SERIAL_COMPONENT_PART = "b"
    COLLECTION = "c"
    SUBUNIT = "d"
    INTEGRATING_RESOURCE = "i"
    MONOGRAPH_ITEM = "m"
    SERIAL = "s"

    LEVEL_OPTIONS = [
        (MONOGRAPHIC_COMPONENT_PART, _("Monographic component part")),
        (SERIAL_COMPONENT_PART, _("Serial component part")),
        (COLLECTION, _("Collection")),
        (SUBUNIT, _("Subunit")),
        (INTEGRATING_RESOURCE, _("Integrating resource")),
        (MONOGRAPH_ITEM, _("Monograph / Item")),
        (SERIAL, _("Serial")),
    ]

    name = models.CharField(max_length=1, choices=LEVEL_OPTIONS)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        return self.get_name_display()


class ItemTypeBase(TimeStampMixin):
    """
    Record type base.

    Used for organizing groups of materials if needed and for populating the
    leader of MARC records when exporting.
    """

    LANGUAGE_MATERIAL = "a"
    NOTATED_MUSIC = "c"
    MANUSCRIPT_NOTATED_MUSIC = "d"
    CARTOGRAPHIC_MATERIAL = "e"
    MANUSCRIPT_CARTOGRAPHIC_MATERIAL = "f"
    PROJECTED_MEDIUM = "g"
    NONMUSICAL_SOUND_RECORDING = "i"
    MUSICAL_SOUND_RECORDING = "j"
    TWO_DIMENSIONAL_NONPROJECTABLE_GRAPHIC = "k"
    COMPUTER_FILE = "m"
    KIT = "o"
    MIXED_MATERIALS = "p"
    THREE_DIMENSIONAL_ARTIFACT = "r"
    MANUSCRIPT_LANGUAGE_MATERIAL = "t"

    TYPE_OPTIONS = [
        (LANGUAGE_MATERIAL, _("Language material")),
        (NOTATED_MUSIC, _("Notated music")),
        (MANUSCRIPT_NOTATED_MUSIC, _("Manuscript notated music")),
        (CARTOGRAPHIC_MATERIAL, _("Cartographic material")),
        (MANUSCRIPT_CARTOGRAPHIC_MATERIAL, _("Manuscript cartographic material")),
        (PROJECTED_MEDIUM, _("Projected medium")),
        (NONMUSICAL_SOUND_RECORDING, _("Nonmusical sound recording")),
        (MUSICAL_SOUND_RECORDING, _("Musical sound recording")),
        (
            TWO_DIMENSIONAL_NONPROJECTABLE_GRAPHIC,
            _("Two-dimensional nonprojectable graphic"),
        ),
        (COMPUTER_FILE, _("Computer file")),
        (KIT, _("Kit")),
        (MIXED_MATERIALS, _("Mixed materials")),
        (
            THREE_DIMENSIONAL_ARTIFACT,
            _("Three dimensional artifact or naturally occurring object"),
        ),
        (MANUSCRIPT_LANGUAGE_MATERIAL, _("Manuscript language material")),
    ]

    name = models.CharField(max_length=1, choices=TYPE_OPTIONS)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        return self.get_name_display()


class ItemType(TimeStampMixin):
    name = models.CharField(max_length=40)
    base = models.ForeignKey(ItemTypeBase, on_delete=models.CASCADE)
    # Movies might be only checkout-able for three days, but books might get 21.
    number_of_days_per_checkout = models.IntegerField(null=True, blank=True)
    # Movies might only have one renew, but books might have five.
    number_of_allowed_renews = models.IntegerField(null=True, blank=True)
    number_of_concurrent_checkouts = models.IntegerField(null=True, blank=True)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)
    icon_name = models.CharField(
        _("icon name"),
        max_length=30,
        null=True,
        blank=True,
        help_text=(
            "The name of the Material Design icon that you'd like to display in the"
            " catalog for this type. https://fonts.google.com/icons?selected=Material+Icons"
        ),
    )
    icon_svg = models.TextField(
        _("icon svg"),
        null=True,
        blank=True,
        help_text=(
            "Don't have a matching option in the Material Design icons? Copy the full"
            " SVG html here to display that instead. WARNING: must be fully formed SVG"
            " element; it will not be saved otherwise. Make sure that your `path`"
            ' tag has `fill="currentColor"` in it so that colors work correctly and'
            " ensure that it displays well as 36px by 36px."
        ),
    )

    def __str__(self):
        return self.name

    def check_icon_svg(self):
        # Because we're storing raw HTML, we should have some basic checks to make sure
        # that we're actually storing an SVG element.
        # https://stackoverflow.com/a/63419911
        SVG_R = r"(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b"
        SVG_RE = re.compile(SVG_R, re.DOTALL)

        return SVG_RE.match(self.icon_svg) is not None

    def save(self, *args, **kwargs):
        if self.icon_svg:
            if not self.check_icon_svg():
                self.icon_svg = None

        super().save(*args, **kwargs)


class Record(TimeStampMixin, SearchableFieldMixin, CoverUtilitiesMixin):
    """
    Information that should not change between different types of the same media.
    For example, an audiobook vs the original text.
    """

    SEARCHABLE_FIELDS = ["title", "authors", "subtitle", "uniform_title"]

    # tag 245a
    # https://www.guinnessworldrecords.com/world-records/358711-longest-title-of-a-book
    title = models.CharField(max_length=27979)
    # This may be multiple people in one string; it's a limitation of the MARC format.
    # Field 245c is used, as it always includes all authors.
    # This field may not have a relevant answer; for example, DVDs don't really have
    # an author. Filling this field out is encouraged, but therefore not required.
    authors = models.CharField(max_length=800, blank=True, null=True)

    # tag 245b
    subtitle = models.CharField(max_length=26021, blank=True, null=True)

    uniform_title = models.CharField(max_length=26021, blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    # Is this part of a series, like a manga or something similar? Maybe a periodical?
    series = models.TextField(blank=True, null=True)

    subjects = models.ManyToManyField(
        Subject, blank=True, verbose_name="list of subjects"
    )

    tags = TaggableManager(blank=True)

    image = models.ImageField(blank=True, null=True)

    type = models.ForeignKey(ItemType, on_delete=models.CASCADE, blank=True, null=True)

    bibliographic_level = models.ForeignKey(
        BibliographicLevel, on_delete=models.CASCADE, blank=True, null=True
    )

    summary = models.TextField(blank=True, null=True)

    zenodotus_id = models.IntegerField(blank=True, null=True)
    zenodotus_record_version = models.IntegerField(blank=True, null=True)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        val = f"{self.title}"
        if self.authors:
            val += f" | {self.authors}"
        if self.type:
            val += f" | {self.type.name}"
        return val

    def save(self, *args, **kwargs):
        self.update_searchable_fields()
        super(Record, self).save(*args, **kwargs)

    def get_available_types(self):
        return set(
            [
                (i.type.name, i.type.id)
                for i in self.item_set.filter(is_active=True)
                if i.type
            ]
        )

    def show_quick_hold_button(self):
        # Only show the quick hold button on standalone items where it makes sense to
        # have a quick hold button.
        if self.bibliographic_level:
            return self.bibliographic_level.name == BibliographicLevel.MONOGRAPH_ITEM

    def get_valid_items(self):
        return self.item_set.filter(is_active=True).order_by("type__name", "-pubyear")

    def get_number_available(self):
        items = self.get_valid_items()
        return len([i for i in items if not i.is_checked_out()])

    def get_number_available_by_type(self):
        items = self.get_valid_items()
        return {
            i.type: len(
                [a for a in items if not a.is_checked_out() and a.type == i.type]
            )
            for i in items
        }


class Item(TimeStampMixin, CoverUtilitiesMixin):
    NEW = "new"
    FINE = "fine"
    VERY_GOOD = "vygd"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

    BASE_CONDITION_OPTIONS = [
        (NEW, "New"),
        (FINE, "Fine"),
        (VERY_GOOD, "Very Good"),
        (GOOD, "Good"),
        (FAIR, "Fair"),
        (POOR, "Poor"),
    ]

    class Meta:
        permissions = [
            ("check_in", _("Can check in materials")),
            ("check_out", _("Can check out materials")),
        ]

    def get_due_date(self):
        return timezone.now() + timedelta(days=self.type.number_of_days_per_checkout)

    # the scanned bar code, usually purchased from an outside vendor
    # Also, ebooks don't have barcodes.
    barcode = models.CharField(_("barcode"), max_length=50, null=True, blank=True)
    # what material is this?
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    # how much was it purchased for?
    price = models.DecimalField(
        _("price"), max_digits=7, decimal_places=2, null=True, blank=True
    )
    condition = models.CharField(
        _("condition"),
        max_length=4,
        choices=BASE_CONDITION_OPTIONS,
        null=True,
        blank=True,
        default=NEW,
    )
    home_location = models.ForeignKey(
        BranchLocation, on_delete=models.CASCADE, null=True, blank=True
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this piece of media is counted as part of the"
            " collection."
        ),
    )
    isbn = models.CharField(_("ISBN"), max_length=13, blank=True, null=True)
    issn = models.CharField(_("ISSN"), max_length=8, blank=True, null=True)
    issn_title = models.TextField(_("issn_title"), blank=True, null=True)
    # it's included in the marc record (sometimes) -- not entirely sure why or what it's
    # for yet.
    marc_location = models.TextField(_("marc_location"), blank=True, null=True)

    # all of the leader information for the marc record -- easier to store and parse
    # this string than it is to spread it out into the database.
    # https://www.loc.gov/marc/bibliographic/bdleader.html
    marc_leader = models.CharField(max_length=50, blank=True, null=True)

    # Allow assigning a piece of media to a user, a location, or really anything
    content_type = models.ForeignKey(
        DjangoContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        limit_choices_to={
            "model__in": (
                "branchlocation",
                "alexandriauser",
            )
        },
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    # Note: do not try to access this directly -- the database doesn't like that.
    # Go through the object on the other side, e.g. request.user.get_checkouts().
    checked_out_to = GenericForeignKey("content_type", "object_id")

    # ebooks don't have call numbers, but pretty much everything else does.
    call_number = models.CharField(
        _("call_number"),
        max_length=100,
        null=True,
        blank=True,
    )

    # How many times has the complete process of checking out and returning happened
    # for this specific item?
    checkout_count = models.IntegerField(_("checkout_count"), default=0)
    # https://www.fdlp.gov/about-fdlp/22-services/929-sudoc-classification-scheme
    # Superintendent of Documents Classification Scheme
    sudoc = models.CharField(_("sudoc"), max_length=30, blank=True, null=True)

    last_checked_out = models.DateTimeField(
        _("last_checked_out"),
        default=timezone.datetime(year=1970, month=1, day=1, tzinfo=UTC),
    )
    # Is this specific item actually allowed to be checked out?
    can_circulate = models.BooleanField(_("can_circulate"), default=True)
    # Is this specific item part of a collection?
    collection = models.ForeignKey(
        Collection, blank=True, null=True, on_delete=models.CASCADE
    )
    notes = models.TextField(_("notes"), blank=True, null=True)
    physical_description = models.CharField(
        _("physical_description"), max_length=500, blank=True, null=True
    )
    publisher = models.CharField(_("publisher"), max_length=500)
    pubyear = models.IntegerField(_("pubyear"), blank=True, null=True)
    edition = models.CharField(_("edition"), max_length=40, blank=True, null=True)
    image = models.ImageField(blank=True, null=True)

    bibliographic_level = models.ForeignKey(
        BibliographicLevel, on_delete=models.CASCADE, blank=True, null=True
    )

    type = models.ForeignKey(ItemType, on_delete=models.CASCADE, blank=True, null=True)

    # These fields are only used when something is checked out to a patron.
    due_date = models.DateField(
        _("due_date"), default=timezone.datetime(year=1970, month=1, day=1)
    )
    renewal_count = models.IntegerField(default=0)
    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def _convert_isbn10_to_isbn13(self) -> str:
        # this process is so ridiculous.
        # https://isbn-information.com/convert-isbn-10-to-isbn-13.html
        isbn = self.isbn
        # drop the old check digit off the end
        isbn = str(isbn)[:-1]
        # bookland!
        isbn = "978" + isbn
        # seriously why
        check_digit = (
            sum(
                [
                    int(integer) if position % 2 == 0 else int(integer) * 3
                    for position, integer in enumerate(str(isbn))
                ]
            )
            % 10
        )
        if check_digit != 0:
            check_digit = 10 - check_digit
        # append the new check digit
        isbn = str(isbn) + str(check_digit)
        return isbn

    @property
    def isbn_13(self) -> str:
        if len(self.isbn) == 13:
            return self.isbn

        return self._convert_isbn10_to_isbn13()

    def _load_leader(self) -> pymarc.Leader:
        return pymarc.Leader(self.marc_leader)

    def export_marc(self):
        # TODO
        ...

    def check_out_to(self, target):
        if not any(
            [isinstance(target, get_user_model()), isinstance(target, BranchLocation)]
        ):
            raise Exception(
                f"Cannot check out to {target}! Must be instance of User or"
                f" BranchLocation."
            )

        self.last_checked_out = timezone.now()
        self.checked_out_to = target
        self.due_date = self.calculate_due_date()
        self.save()

    def is_available(self) -> bool:
        return not any([self.is_checked_out(), self.is_checked_out_to_system()])

    def is_checked_out(self) -> bool:
        return isinstance(self.checked_out_to, get_user_model())

    def is_checked_out_to_system(self) -> bool:
        if hasattr(self.checked_out_to, "host"):
            return self.checked_out_to.host == settings.DEFAULT_SYSTEM_HOST_KEY

    def calculate_due_date(self, start_date: date = None) -> date:
        # This function does not set the due date because it's used to show
        # hypotheticals on the frontend. Save the output of this function to
        # self.due_date to actually set the due date.
        if not start_date:
            start_date = timezone.now().date()
        checkout_renew_days = (
            self.type.number_of_days_per_checkout
            or settings.SITE_DATA[self.host].get("default_checkout_duration_days")
        )
        return start_date + timedelta(days=checkout_renew_days)

    def calculate_renewal_due_date(self) -> date:
        return self.calculate_due_date(start_date=self.due_date)

    def get_due_date_color_class(self) -> str:
        # Return a bootstrap theme color based on how much time is left until the
        # item is due.
        now = timezone.now().date()
        if self.due_date < now:
            # that sucker's overdue
            return "danger text-light"  # red
        if self.due_date < now + timedelta(days=3):
            return "warning text-dark"  # orange
        return "secondary"  # grey

    def can_renew(self):
        # easy to access general "hey is this possible" function.
        return all(
            [
                self.within_renewal_period(),
                self.has_available_renewals(),
                not self.is_on_hold(),
            ]
        )

    def within_renewal_period(self):
        day_delay = settings.SITE_DATA[self.host].get("default_renewal_delay_days")
        now = timezone.now().date()
        return self.due_date < now + timedelta(days=day_delay)

    def has_available_renewals(self):
        if not self.renewal_count:
            self.renewal_count = 0
        return self.renewal_count < self.get_max_renewal_count()

    def get_renewal_availability_date(self):
        # For when the renewal button turns on. Controlled by the delay
        # in the configs for the library.
        day_delay = settings.SITE_DATA[self.host].get("default_renewal_delay_days")
        return self.due_date - timedelta(days=day_delay)

    def get_max_renewal_count(self):
        return self.type.number_of_allowed_renews or settings.SITE_DATA[self.host].get(
            "default_max_renews"
        )

    def is_on_hold(self):
        return Hold.objects.filter(item=self).count() > 0

    def __str__(self):
        string = f"{self.record.title} | {self.record.authors}"
        if self.call_number:
            string += f" | {self.call_number}"
        if self.type:
            string += f" | {self.type.name}"
        return string


class Hold(TimeStampMixin):
    date_created = models.DateTimeField(default=timezone.now)
    placed_for = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(_("notes"), blank=True, null=True)
    # TODO: Add data cleanup to remove expired holds / migrate to primary location
    destination = models.ForeignKey(
        BranchLocation, on_delete=models.SET_NULL, null=True
    )

    item = models.ForeignKey(Item, null=True, blank=True, on_delete=models.CASCADE)

    # used to see whether we can recalculate a hold in the event that a hold
    # is placed on an item but someone tries to check out the item
    # before it can be pulled
    specific_copy = models.BooleanField(default=False)
    # todo: make this flag only available for managers
    force_next_available = models.BooleanField(
        default=False,
        help_text=(
            "Very rarely, certain holds need to be completed ahead of others. Setting"
            " this makes this hold be processed next, no matter where it is in the queue."
            " If there are multiple holds with this flag, then they will be processed in"
            " order of oldest first."
        ),
    )

    host = models.CharField(max_length=100, default=settings.DEFAULT_HOST_KEY)

    def __str__(self):
        return f"{self.item} heading to {self.destination}"

    def get_hold_queue_number(self):
        # todo: add handling for a specific host
        open_holds = Hold.objects.filter(
            item=self.item,
        ).order_by("-date_created")
        return (*open_holds,).index(self) + 1

    def is_ready_for_pickup(self):
        return self.item.checked_out_to == BranchLocation.objects.get(
            name="Ready for Pickup"
        )

    def get_status_for_patron(self):
        if self.is_ready_for_pickup():
            return _("Ready for pickup!")
        else:
            return _("In Progress")

    def get_status_color_class(self):
        if self.is_ready_for_pickup():
            return "success text-light"
        else:
            return "secondary text-light"

    def get_status_for_staff(self):
        ...

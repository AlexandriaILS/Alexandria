from datetime import timedelta

import pymarc
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType as DjangoContentType
from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone
from taggit.managers import TaggableManager
import requests

from catalog import openlibrary
from users.models import BranchLocation


class Subject(models.Model):
    name = models.CharField(max_length=100)
    host = models.CharField(max_length=100, default="default")

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=200)
    home = models.ForeignKey(
        BranchLocation, null=True, blank=True, on_delete=models.CASCADE
    )
    can_circulate = models.BooleanField(default=True)
    host = models.CharField(max_length=100, default="default")

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
    host = models.CharField(max_length=100, default="default")

    def __str__(self):
        return self.get_name_display()


class ItemTypeBase(models.Model):
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
    host = models.CharField(max_length=100, default="default")

    def __str__(self):
        return self.get_name_display()


class ItemType(models.Model):
    name = models.CharField(max_length=40)
    base = models.ForeignKey(ItemTypeBase, on_delete=models.CASCADE)
    # Movies might be only checkout-able for three days, but books might get 21.
    number_of_days_per_checkout = models.IntegerField(null=True, blank=True)
    # Movies might only have one renew, but books might have five.
    number_of_allowed_renews = models.IntegerField(null=True, blank=True)
    host = models.CharField(max_length=100, default="default")

    def __str__(self):
        return self.name


class Record(models.Model):
    """
    Information that should not change between different types of the same media.
    For example, an audiobook vs the original text.
    """

    # tag 245a
    title = models.CharField(max_length=26021)  # thanks, Yethindra
    # This may be multiple people in one string; it's a limitation of the MARC format.
    # Field 245c is used, as it always includes all authors.
    # This field may not have a relevant answer; for example, DVDs don't really have
    # an author. Filling this field out is encouraged, but therefore not required.
    authors = models.CharField(max_length=500, blank=True, null=True)

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
    host = models.CharField(max_length=100, default="default")

    def __str__(self):
        val = f"{self.title}"
        if self.authors:
            val += f" | {self.authors}"
        if self.type:
            val += f" | {self.type.name}"
        return val

    def save(self, *args, **kwargs):
        if self.type:
            if self.type.base.name == ItemTypeBase.LANGUAGE_MATERIAL:
                try:
                    openlibrary.download_cover(self)
                except requests.exceptions.HTTPError:
                    pass
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
        return self.item_set.filter(is_active=True).order_by("-pubyear")


class Item(models.Model):
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
    # date updated when material is checked in
    last_checked_out = models.DateTimeField(
        _("last_checked_out"), blank=None, null=True
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
    host = models.CharField(max_length=100, default="default")

    def save(self, *args, **kwargs):
        if self.type:
            if self.type.base.name == ItemTypeBase.LANGUAGE_MATERIAL:
                try:
                    openlibrary.download_cover(self)
                except requests.exceptions.HTTPError:
                    pass
        super(Item, self).save(*args, **kwargs)

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

    def is_checked_out(self):
        return isinstance(self.checked_out_to, get_user_model())

    def __str__(self):
        string = f"{self.record.title} | {self.record.authors}"
        if self.call_number:
            string += f" | {self.call_number}"
        if self.type:
            string += f" | {self.type.name}"
        return string

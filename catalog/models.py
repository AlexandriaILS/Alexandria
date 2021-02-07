from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType as DjangoContentType
import pymarc

from users.models import BranchLocation


class Subject(models.Model):
    name = models.CharField(max_length=100)


class Record(models.Model):
    """
    Information that should not change between different types of the same media.
    For example, a DVD release vs the original text.
    """

    # tag 245a
    title = models.CharField(max_length=26021)  # thanks, Yethindra
    # This may be multiple people in one string; it's a limitation of the MARC format.
    # Field 245c is used, as it always includes all authors.
    authors = models.CharField(max_length=500)

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


class Collection(models.Model):
    name = models.CharField(max_length=200)
    home = models.ForeignKey(
        BranchLocation, null=True, blank=True, on_delete=models.CASCADE
    )
    can_circulate = models.BooleanField(default=True)


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

    RECORD_TYPE_MAP = {
        "a": (_("Language material"), _("Book / Text")),
        "c": (_("Notated music"), _("Sheet music")),
        "d": (_("Manuscript notated music"), _("Handwritten sheet music")),
        "e": (_("Cartographic material"), _("Map")),
        "f": (_("Manuscript cartographic material"), _("Hand-drawn map")),
        "g": (_("Projected medium"), _("Video / film / slides / etc.")),
        "i": (
            _("Nonmusical sound recording"),
            _("Spoken word / sound effect recorded audio"),
        ),
        "j": (_("Musical sound recording"), _("Music recording")),
        "k": (
            _("Two-dimensional nonprojectable graphic"),
            _("Pictures / charts / graphics"),
        ),
        "m": (_("Computer file"), _("Software / dataset / online service")),
        "o": (_("Kit"), _("Kit of assorted materials")),
        "p": (_("Mixed materials"), _("Mixed material")),
        "r": (
            _("Three-dimensional artifact or naturally occurring object"),
            _("3D object / sculpture / toy / etc."),
        ),
        "t": (_("Manuscript language material"), _("Handwritten book")),
    }

    BIBLIOGRAPHIC_LEVEL_MAP = {
        "a": (_("Monographic component part"), _("Standalone item from a series")),
        "b": (_("Serial component part"), _("Part of a series")),
        "c": (_("Collection"), _("Collection")),
        "d": (_("Subunit"), _("Sub-unit of a collection or series")),
        "i": (
            _("Integrating resource"),
            _("Potentially ephemeral item; loose-leaf paper / website"),
        ),
        "m": (_("Monograph/Item"), _("Standalone item")),
        "s": (_("Serial"), _("Periodical")),
    }

    # the scanned bar code, usually purchased from an outside vendor
    barcode = models.CharField(_("barcode"), max_length=50)
    # what material is this?
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    # how much was it purchased for?
    price = models.DecimalField(_("price"), max_digits=7, decimal_places=2)
    condition = models.CharField(
        _("condition"),
        max_length=4,
        choices=BASE_CONDITION_OPTIONS,
        null=True,
        blank=True,
        default=NEW,
    )
    home_location = models.ForeignKey(
        BranchLocation,
        on_delete=models.CASCADE,
        null=settings.FLOATING_COLLECTION,
        blank=settings.FLOATING_COLLECTION,
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
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
    content_type = models.ForeignKey(DjangoContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    checked_out_to = GenericForeignKey("content_type", "object_id")

    call_number = models.CharField(
        _("call_number"), max_length=100, unique=settings.FORCE_UNIQUE_CALL_NUMBERS
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
    def type(self, human_readable: bool = False) -> str:
        return self.RECORD_TYPE_MAP[self._load_leader().type_of_record][
            1 if human_readable else 0
        ]

    @type.setter
    def type(self, value: str) -> None:
        leader = self._load_leader()
        leader.type_of_record = value
        self.marc_leader = leader.leader

    @property
    def bibliographic_level(self, human_readable: bool = False):
        return self.BIBLIOGRAPHIC_LEVEL_MAP[self._load_leader().bibliographic_level][
            1 if human_readable else 0
        ]

    @bibliographic_level.setter
    def bibliographic_level(self, value):
        leader = self._load_leader()
        leader.bibliographic_level = value
        self.marc_leader = leader.leader

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

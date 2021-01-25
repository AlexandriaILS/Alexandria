from django.db import models
from taggit.managers import TaggableManager


class ContentType(models.Model):
    # https://www.ifla.org/files/assets/cataloguing/isbd/area-0_2009.pdf
    # content forms
    DATASET = "datas"
    IMAGE = "img"
    MOVEMENT = "mvemt"
    MUSIC = "music"
    OBJECT = "objct"
    PROGRAM = "progm"
    SOUNDS = "sound"
    SPOKEN_WORD = "spknw"
    TEXT = "text"
    MULTIPLE_CONTENT_FORMS = "mcf"
    OTHER_CONTENT_FORM = "ocf"

    BASE_CONTENT_FORMS = [
        (DATASET, "Dataset (digital content intended for processing)"),
        (IMAGE, "Image"),
        (MOVEMENT, "Movement (content expressed through motion, i.e. dance)"),
        (MUSIC, "Music"),
        (OBJECT, "Object (a physical, 3D object)"),
        (PROGRAM, "Program (software)"),
        (SOUNDS, "Sounds (sound effects, animal noises, etc.)"),
        (SPOKEN_WORD, "Spoken Word"),
        (TEXT, "Text"),
        (MULTIPLE_CONTENT_FORMS, "Multiple Content Forms (three or more terms apply)"),
        (OTHER_CONTENT_FORM, "Other Content Form"),
    ]

    # content qualifications
    CARTOGRAPHIC = "carto"
    NOTATED = "notat"
    PERFORMED = "perfo"

    BASE_CONTENT_QUALIFICATIONS = [
        (CARTOGRAPHIC, "Cartographic"),
        (NOTATED, "Notated"),
        (PERFORMED, "Performed"),
    ]

    # specification of motion -- image only
    MOVING = "mvg"
    STILL = "still"

    BASE_MOTION_TYPES = [
        (MOVING, "Moving"),
        (STILL, "Still"),
    ]

    # specification of dimensionality - image only
    TWO_DIMENSIONAL = "2d"
    THREE_DIMENSIONAL = "3d"

    BASE_DIMENSIONAL_TYPES = [
        (TWO_DIMENSIONAL, "2-Dimensional"),
        (THREE_DIMENSIONAL, "3-Dimensional"),
    ]

    # sensory specification
    AURAL = "aural"
    GUSTATORY = "gusta"
    OLFACTORY = "olfac"
    TACTILE = "tacti"
    VISUAL = "visua"

    BASE_SENSORY_TYPES = [
        (AURAL, "Aural"),
        (GUSTATORY, "Gustatory"),
        (OLFACTORY, "Olfactory"),
        (TACTILE, "Tactile"),
        (VISUAL, "Visual"),
    ]

    # media types
    UNMEDIATED = "unmed"
    AUDIO = "audio"
    ELECTRONIC = "elect"
    MICROFORM = "micfm"
    MICROSCOPIC = "micsp"
    PROJECTED = "proje"
    STEREOGRAPHIC = "stero"
    VIDEO = "video"
    MULTIPLE_MEDIA = "multm"
    OTHER_MEDIA = "othmd"

    BASE_MEDIA_TYPES = [
        (UNMEDIATED, "Unmediated"),
        (AUDIO, "Audio"),
        (ELECTRONIC, "Electronic"),
        (MICROFORM, "Microform"),
        (MICROSCOPIC, "Microscopic"),
        (PROJECTED, "Projected"),
        (STEREOGRAPHIC, "Stereographic"),
        (VIDEO, "Video"),
        (MULTIPLE_MEDIA, "Multiple Media"),
        (OTHER_MEDIA, "Other Media"),
    ]

    content_form = models.CharField(
        max_length=5,
        choices=BASE_CONTENT_FORMS,
        null=True,
        blank=True,
        default=TEXT,
        help_text=(
            "What is this media? Select 'Multiple Media' if three or more types describe"
            " this media."
        ),
    )
    content_qualification = models.CharField(
        max_length=5,
        choices=BASE_CONTENT_QUALIFICATIONS,
        null=True,
        blank=True,
        help_text="Optional",
    )
    sensory_type = models.CharField(
        max_length=5,
        choices=BASE_SENSORY_TYPES,
        null=True,
        blank=True,
        help_text="Optional",
    )
    media_type = models.CharField(
        max_length=5,
        choices=BASE_MEDIA_TYPES,
        null=True,
        blank=True,
        default=UNMEDIATED,
        help_text="Optional",
    )
    dimensionality = models.CharField(
        max_length=5,
        choices=BASE_DIMENSIONAL_TYPES,
        null=True,
        blank=True,
        help_text="Optional -- image only",
    )
    motion_type = models.CharField(
        max_length=5,
        choices=BASE_MOTION_TYPES,
        null=True,
        blank=True,
        help_text="Optional -- image only",
    )


class ContentTypeManager(models.Model):
    # Sometimes we can have mixed types like "Object + Image (olfactory)"
    # Having a type manager allows us to easily and transparently handle
    # arbitrarily complex type combinations, as anything above two types
    # should be listed as "multiple media".
    primary = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="primary_content_type"
    )
    secondary = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="secondary_content_type",
    )

    def __str__(self):
        return (
            f"{self.primary}"
            if not self.secondary
            else f"{self.primary} + {self.secondary}"
        )


class ISBDRecord(models.Model):
    # https://en.wikipedia.org/wiki/International_Standard_Bibliographic_Description
    # https://www.ifla.org/files/assets/cataloguing/isbd/isbd-examples_2013.pdf
    # Area 0 is moved to the Media model, as we can have different types of media
    # for the same content.

    # Area 1
    title = models.TextField()
    title_proper = models.TextField(null=True, blank=True)
    title_parallel = models.TextField(null=True, blank=True)
    title_information = models.TextField(null=True, blank=True)
    # who made this thing that we're writing a record about?
    title_statement_of_responsibility = models.TextField()

    # Area 2
    # 7th ed.
    edition = models.TextField(null=True, blank=True)

    # Area 3
    specific_info = models.TextField(null=True, blank=True)

    # Area 4
    # Chicago : University of Chicago Press, 2007
    publisher = models.TextField(null=True, blank=True)

    # Area 5
    material_description = models.TextField(null=True, blank=True)

    # Area 6
    # is this part of a series? Let's write that here.
    series = models.TextField(null=True, blank=True)

    # Area 7
    notes = models.TextField(null=True, blank=True)

    # Area 8
    # ISBN, ISSN, etc.
    resource_identifier = models.TextField(null=True, blank=True)

    tags = TaggableManager(blank=True)

    def parse_isbd_record(self, record):
        pass

    @property
    def isbn_13(self):
        return "123"

    @property
    def isbn_10(self):
        return "123"

    @property
    def isbn(self):
        return self.isbn_13

    @property
    def loc_code(self):
        return "123"

    @property
    def publish_date(self):
        return "123"

    @property
    def author(self):
        return self.title_statement_of_responsibility


class Media(models.Model):
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

    # is this a book? A CD? A book AND a CD?
    type = models.ManyToManyField(ContentTypeManager, related_name="content_type")
    # the scanned bar code, usually purchased from an outside vendor
    barcode = models.CharField(max_length=50)
    # what material is this?
    record = models.ForeignKey(ISBDRecord, on_delete=models.CASCADE)
    # how much was it purchased for?
    price = models.DecimalField(max_digits=7, decimal_places=2)
    condition = models.CharField(
        max_length=4, choices=BASE_CONDITION_OPTIONS, null=True, blank=True, default=NEW
    )

import random
import string
import sys
from typing import Dict

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from alexandria.configs import init_site_data
from catalog.models import (
    Record,
    Subject,
    BibliographicLevel,
    Item,
    ItemType,
    ItemTypeBase,
)
from catalog.zenodotus_utils import slash_join
from users.models import BranchLocation
from utils.images import get_and_save_image


BOOK_OPTIONS = ["Audiobook (CD)", "Book", "Audiobook (Cassette)", "Ebook"]
BRANCH_LOCATIONS = [
    "Crickhollow",
    "Frogmorton",
    "Gamwitch",
    "Hobbiton",
    "Little Delving",
    "Michel Delving",
    "Overhill",
    "Rushey",
    "Tuckborough",
    "Willowbottom",
    "Woodhall",
]
PUBLISHERS = [
    "AntarcticBird Spork Building",
    "Hatchet",
    "HarpoonCollegiate",
    "Macmillions",
    "Simone & Shoosting",
    "IDG Books (RIP)",
    "CowFjord University Press",
]
SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg"'
    ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    ' version="1.1"'
    ' id="mdi-cassette"'
    ' width="36"'
    ' height="36"'
    ' viewBox="2 2 20 20">'
    "<path"
    ' fill="currentColor"'
    ' d="M4,5A2,2 0 0,0 2,7V17A2,2 0 0,0 4,19H6L7,17H17L18,19H20A2,2 0 0,0 22,17V7A2,'
    "2 0 0,0 20,5H4M6.5,10A1.5,1.5 0 0,1 8,11.5A1.5,1.5 0 0,1 6.5,13A1.5,1.5 0 0,1 5,"
    "11.5A1.5,1.5 0 0,1 6.5,10M9,10H15V13H9V10M17.5,10A1.5,1.5 0 0,1 19,11.5A1.5,"
    '1.5 0 0,1 17.5,13A1.5,1.5 0 0,1 16,11.5A1.5,1.5 0 0,1 17.5,10Z" />'
    "</svg>"
)

sites = init_site_data()


def build_record(item: Dict) -> Record:
    subject_list = [
        Subject.objects.get_or_create(name=subj)[0]
        for subj in [
            requests.get(
                slash_join(
                    sites[settings.DEFAULT_HOST_KEY]["zenodotus_url"], "subject", id
                )
            )
            .json()
            .get("name")
            for id in item["subjects"]
        ]
    ]
    bib_reverse = dict((v, k) for k, v in BibliographicLevel.LEVEL_OPTIONS)
    bib_resp = (
        requests.get(
            slash_join(
                sites[settings.DEFAULT_HOST_KEY]["zenodotus_url"],
                "bibliographiclevel",
                item["bibliographic_level"],
            )
        )
        .json()
        .get("name")
    )
    if bib_resp:
        bibliographic_level = BibliographicLevel.objects.get(name=bib_reverse[bib_resp])
    else:
        bibliographic_level = None

    itemtype_response = requests.get(
        slash_join(
            sites[settings.DEFAULT_HOST_KEY]["zenodotus_url"], "itemtype", item["type"]
        )
    ).json()
    itemtypebase_response = (
        requests.get(
            slash_join(
                sites[settings.DEFAULT_HOST_KEY]["zenodotus_url"],
                "itemtypebase",
                itemtype_response["base"],
            )
        )
        .json()
        .get("name")
    )
    itemtypebase_reverse = dict((v, k) for k, v in ItemTypeBase.TYPE_OPTIONS)
    itemtypebase = ItemTypeBase.objects.get(
        name=itemtypebase_reverse[itemtypebase_response]
    )
    itemtype, _ = ItemType.objects.get_or_create(
        name=itemtype_response["name"], base=itemtypebase
    )

    new_record = Record.objects.create(
        title=item["title"],
        authors=item["authors"],
        subtitle=item["subtitle"],
        uniform_title=item["uniform_title"],
        notes=item["notes"],
        series=item["series"],
        type=itemtype,
        bibliographic_level=bibliographic_level,
    )
    for subj in subject_list:
        new_record.subjects.add(subj)

    for tag in item["tags"]:
        new_record.tags.add(tag)

    if item["image"]:
        new_record = get_and_save_image(item["image"], new_record)

    new_record.save()
    return new_record


def generate_LOC_call_number(pubyear=None):
    # Format: Section / item_ID / Cutter 1 (optional) / Cutter 2 (optional) / pubyear
    section = "".join(
        [random.choice(string.ascii_uppercase) for _ in range(random.randint(1, 2))]
    )
    item_ID = str(random.randint(1, 3000))
    if random.random() < 0.7:
        item_ID += "." + str(random.randint(2, 9))
    cutters = [
        random.choice(string.ascii_uppercase) + str(random.randint(1, 99))
        for _ in range(random.randint(0, 2))
    ]
    call_number = f"{section}{item_ID}"
    if len(cutters) == 2:
        call_number += f".{cutters[0]} {cutters[1]}"
    if len(cutters) == 1:
        call_number += f".{cutters[0]}"
    call_number += f" {str(pubyear) if pubyear else '{}'}"
    return call_number


def generate_fake_item(record: Record, count: int) -> None:
    if record.type.base.name == ItemTypeBase.LANGUAGE_MATERIAL:
        # it's a book.
        options = ItemType.objects.filter(name__in=BOOK_OPTIONS)
    else:
        options = [record.type]

    type_dict = {}

    for opt in options:
        type_dict[opt] = generate_LOC_call_number()

    for i in range(count):
        pubyear = random.randrange(1945, 2021)
        item_type = random.choice(list(type_dict.keys()))
        call_number = type_dict[item_type].format(pubyear)
        Item.objects.create(
            barcode=random.getrandbits(50),
            record=record,
            price=random.randrange(12, 35) + (random.randrange(0, 100) / 100),
            home_location=random.choice(
                BranchLocation.objects.filter(name__in=BRANCH_LOCATIONS)
            ),
            is_active=True,
            call_number=call_number,
            publisher=random.choice(PUBLISHERS),
            pubyear=pubyear,
            bibliographic_level=record.bibliographic_level,
            type=item_type,
        )


class Command(BaseCommand):
    help = (
        "Download records from Zenodotus & automatically create matching randomized"
        " items. Not for production systems."
    )

    def handle(self, *args, **options):
        if Record.objects.count() > 0:
            answer = input(
                self.style.WARNING(
                    "WAIT! There is already data in the db. Are you sure you want to run"
                    " this? [y/N] "
                )
            )
            if not answer.lower().startswith("y"):
                self.stdout.write(self.style.ERROR("Exiting!"))
                sys.exit(0)

        for branch in [
            "Crickhollow",
            "Frogmorton",
            "Gamwitch",
            "Hobbiton",
            "Little Delving",
            "Michel Delving",
            "Overhill",
            "Rushey",
            "Tuckborough",
            "Willowbottom",
            "Woodhall",
        ]:
            BranchLocation.objects.get_or_create(name=branch)

        base = ItemTypeBase.objects.get(name=ItemTypeBase.LANGUAGE_MATERIAL)
        # ["Audiobook (CD)", "Book", "Audiobook (Cassette)", "Ebook"]
        ItemType.objects.get_or_create(
            name="Audiobook (CD)", base=base, icon_name="album"
        )
        ItemType.objects.get_or_create(
            name="Ebook", base=base, icon_name="tablet_android"
        )
        ItemType.objects.get_or_create(name="Book", base=base, icon_name="auto_stories")
        ItemType.objects.get_or_create(
            name="Audiobook (Cassette)", base=base, icon_svg=SVG
        )

        available_records = requests.get(
            slash_join(sites[settings.DEFAULT_HOST_KEY]["zenodotus_url"], "record")
        ).json()
        # returns a list of dicts
        for item in available_records:
            if not Record.objects.filter(title=item["title"]).first():
                self.stdout.write(
                    self.style.HTTP_INFO(f"Processing {item['title']}...")
                )
                new_record = build_record(item)

                count = random.randrange(7, 20)
                self.stdout.write(self.style.HTTP_INFO(f"Creating item(s)..."))
                generate_fake_item(new_record, count)
                self.stdout.write(self.style.SUCCESS(f"Items added!"))
        self.stdout.write(self.style.SUCCESS(f"Import finished!"))

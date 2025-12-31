import random
import string
import sys
from typing import Dict

import requests
from django.core.management.base import BaseCommand

from alexandria.distributed.models import Setting
from alexandria.records.models import (
    BibliographicLevel,
    Item,
    ItemType,
    ItemTypeBase,
    Record,
    Subject,
)
from alexandria.records.zenodotus_utils import slash_join
from alexandria.users.models import BranchLocation
from alexandria.utils.images import get_and_save_image

BOOK_OPTIONS = ["Audiobook (CD)", "Book", "Audiobook (Cassette)", "Ebook"]
PUBLISHERS = [
    "AntarcticBird Spork Building",
    "Hatchet",
    "HarpoonCollegiate",
    "Macmillions",
    "Simone & Shoosting",
    "IDG Books (RIP)",
    "CowFjord University Press",
]


def build_record(item: Dict) -> Record:
    subject_list = [
        Subject.objects.get_or_create(name=subj)[0]
        for subj in [
            requests.get(slash_join(Setting.get("zenodotus_url"), "subject", id))
            .json()
            .get("name")
            for id in item["subjects"]
        ]
    ]
    bib_reverse = dict((v, k) for k, v in BibliographicLevel.LEVEL_OPTIONS)
    bib_resp = (
        requests.get(
            slash_join(
                Setting.get(Setting.options.ZENODOTUS_URL),
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
        slash_join(Setting.get(Setting.options.ZENODOTUS_URL), "itemtype", item["type"])
    ).json()
    itemtypebase_response = (
        requests.get(
            slash_join(
                Setting.get(Setting.options.ZENODOTUS_URL),
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
        new_record = get_and_save_image.enqueue(item["image"], new_record)

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

    locations = BranchLocation.objects.filter(open_to_public=True)

    for i in range(count):
        pubyear = random.randrange(1945, 2021)
        item_type = random.choice(list(type_dict.keys()))
        call_number = type_dict[item_type].format(pubyear)
        Item.objects.create(
            barcode=random.getrandbits(50),
            record=record,
            price=random.randrange(12, 35) + (random.randrange(0, 100) / 100),
            home_location=random.choice(locations),
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

        available_records = requests.get(
            slash_join(Setting.get(Setting.options.ZENODOTUS_URL), "record")
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

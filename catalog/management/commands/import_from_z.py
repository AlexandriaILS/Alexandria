import random
import sys
from typing import Dict

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from utils.images import get_and_save_image
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


def build_record(item: Dict) -> Record:
    subject_list = [
        Subject.objects.get_or_create(name=subj)[0]
        for subj in [
            requests.get(slash_join(settings.ZENODOTUS_URL, "subject", id))
            .json()
            .get("name")
            for id in item["subjects"]
        ]
    ]
    bib_reverse = dict((v, k) for k, v in BibliographicLevel.LEVEL_OPTIONS)
    bib_resp = (
        requests.get(
            slash_join(
                settings.ZENODOTUS_URL,
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
        slash_join(settings.ZENODOTUS_URL, "itemtype", item["type"])
    ).json()
    itemtypebase_response = (
        requests.get(
            slash_join(
                settings.ZENODOTUS_URL, "itemtypebase", itemtype_response["base"]
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


def generate_fake_item(record: Record):
    if record.type.base.name == ItemTypeBase.LANGUAGE_MATERIAL:
        base = ItemTypeBase.objects.get(name=ItemTypeBase.LANGUAGE_MATERIAL)
        # it's a book.
        options = [
            ItemType.objects.get_or_create(name="Audiobook (CD)", base=base)[0],
            ItemType.objects.get_or_create(name="Book", base=base)[0],
            ItemType.objects.get_or_create(name="Audiobook (Cassette)", base=base)[0],
            ItemType.objects.get_or_create(name="Ebook", base=base)[0],
        ]
    else:
        options = [record.type]

    Item.objects.create(
        barcode=random.getrandbits(50),
        record=record,
        price=random.randrange(12, 35) + (random.randrange(0, 100) / 100),
        home_location=random.choice(BranchLocation.objects.all()),
        is_active=True,
        call_number=random.getrandbits(32),
        publisher=random.choice(
            [
                "AntarcticBird Spork Building",
                "Hatchet",
                "HarpoonCollegiate",
                "Macmillions",
                "Simone & Shoosting",
                "IDG Books (RIP)",
                "CowFjord University Press",
            ]
        ),
        pubyear=random.randrange(1945, 2021),
        bibliographic_level=record.bibliographic_level,
        type=random.choice(options),
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

        available_records = requests.get(
            slash_join(settings.ZENODOTUS_URL, "record")
        ).json()
        # returns a list of dicts
        for item in available_records:
            if not Record.objects.filter(title=item["title"]).first():
                self.stdout.write(
                    self.style.HTTP_INFO(f"Processing {item['title']}...")
                )
                new_record = build_record(item)

                count = random.randrange(1, 45)
                self.stdout.write(self.style.HTTP_INFO(f"Creating {count} item(s)..."))
                for _ in range(count):
                    generate_fake_item(new_record)
                self.stdout.write(self.style.SUCCESS(f"Items added!"))
        self.stdout.write(self.style.SUCCESS(f"Import finished!"))

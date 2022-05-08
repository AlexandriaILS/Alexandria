import json
import random

from django.core.management.base import BaseCommand
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, track

from alexandria.catalog.management.commands.import_from_z import (
    PUBLISHERS,
    generate_LOC_call_number,
)
from alexandria.records.models import (
    BibliographicLevel,
    Item,
    ItemType,
    Record,
    Subject,
)
from alexandria.users.models import BranchLocation
from alexandria.utils.gutenberg import decompressBytesToString


class Command(BaseCommand):
    help = "Imports data from Project Gutenberg for testing data."

    def handle(self, *args, **options):
        with open("raw_gutenberg_data", "rb") as f:
            data = json.loads(decompressBytesToString(f.read()))

        subjects = []
        for obj in data["results"]:
            subjects += obj["subjects"]

        subjects = list(set(subjects))

        if Subject.objects.count() == 0:
            Subject.objects.bulk_create([Subject(name=x) for x in subjects])
            self.stdout.write(self.style.NOTICE(f"Created {len(subjects)} subjects."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Subjects already in db, not writing more.")
            )

        itemtype_book = ItemType.objects.get(name="Book")
        monograph = BibliographicLevel.objects.get(name="m")

        if Record.objects.count() == 0:
            record_objs = []
            for obj in track(
                data["results"], description="[green]Generating records..."
            ):
                record_objs.append(
                    Record(
                        title=obj["title"],
                        authors=", ".join(obj["authors"]).encode("utf-8").decode(),
                        notes=f"project_gutenberg_id:{obj['id']}",
                        type=itemtype_book,
                        bibliographic_level=monograph,
                    )
                )

            Record.objects.bulk_create(record_objs)

            record_db_objects = list(Record.objects.all())
            subject_links = []
            subjects = {s.name: s.id for s in Subject.objects.all()}

            for index, obj in enumerate(
                track(data["results"], description="[green]Generating subject links...")
            ):
                subject_links += [
                    Record.subjects.through(
                        subject_id=sub_id, record_id=record_db_objects[index].id
                    )
                    for sub_id in [subjects[s] for s in obj["subjects"]]
                ]

            Record.subjects.through.objects.bulk_create(subject_links)

        else:
            self.stdout.write(
                self.style.NOTICE(f"Records already in db, not writing more.")
            )

        if Item.objects.count() == 0:
            locations = BranchLocation.objects.filter(open_to_public=True)
            records = Record.objects.all()
            items = []
            for r in track(records, description="[green]Creating items..."):
                # maybe we have a few copies
                for _ in range(random.randrange(1, 4)):
                    pubyear = random.randrange(1850, 2021)
                    items.append(
                        Item(
                            barcode=random.getrandbits(50),
                            record=r,
                            price=random.randrange(12, 35)
                            + (random.randrange(0, 100) / 100),
                            home_location=random.choice(locations),
                            is_active=True,
                            call_number=generate_LOC_call_number(pubyear),
                            publisher=random.choice(PUBLISHERS),
                            pubyear=pubyear,
                            bibliographic_level=r.bibliographic_level,
                            type=itemtype_book,
                        )
                    )
            Item.objects.bulk_create(items)
        else:
            self.stdout.write(
                self.style.NOTICE(f"Items already in db, not writing more.")
            )

        self.stdout.write(self.style.SUCCESS("Loaded in data!"))
        self.stdout.write(
            "Run ./manage.py get_gutenberg_images if you want to populate images."
        )

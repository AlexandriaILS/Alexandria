import os
import random
import sqlite3

from django.core.management.base import BaseCommand
from rich.progress import track

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

DB_FILE = "ol_dump.sqlite3"
stop_importing_at = 4000000


class Command(BaseCommand):
    help = "Import data from the ol_dump.sqlite3 file."

    def handle(self, *args, **options):
        #####
        # todo: There is a memory leak somewhere in here that I can't find. It always
        #  dies around the 9 million record mark, so limiting it to 4MM seems to be
        #  a safe limit. I'd like to be able to import the whole 23MM, though.
        #####
        if not os.path.exists(DB_FILE):
            raise Exception(
                "Cannot find ol_dump.sqlite3 -- is it present in the same directory"
                " as manage.py? Have you run `python manage.py create_ol_dump` or"
                " gotten a prebuilt dump file?"
            )

        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()

        self.stdout.write(self.style.NOTICE(f"Starting on subjects..."))
        if Subject.objects.count() == 0:
            subjects: list[tuple[str]] = cur.execute(
                "select * from subjects"
            ).fetchall()
            # there are some corrupt subjects that are _gigantic_; strip them out.
            subjects: list[str] = [obj[0] for obj in subjects if len(obj[0]) < 500]
            Subject.objects.bulk_create([Subject(name=x) for x in subjects])
            self.stdout.write(self.style.NOTICE(f"Created {len(subjects)} subjects."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Subjects already in db, not writing more.")
            )

        itemtype_book = ItemType.objects.get(name="Book")
        monograph = BibliographicLevel.objects.get(name="m")

        if Record.objects.count() == 0:
            subject_objects = Subject.objects.all().values("name", "id")
            subject_dict = {s["name"]: s["id"] for s in subject_objects}
            authors: list[tuple[str, str]] = cur.execute(
                "select * from authors"
            ).fetchall()
            # author key: author name
            authors: dict[str, str] = {a[1]: a[0] for a in authors}

            batch_size = 5000
            offset = 0
            self.stdout.write("Starting loading of records...")
            while True:
                if offset % 100000 == 0:
                    self.stdout.write(f"Starting batch offset {offset}")
                if offset > stop_importing_at:
                    self.stdout.write("Reached stopping point!")
                    break

                work_batch = cur.execute(
                    "select * from works limit ? offset ?", (batch_size, offset)
                ).fetchall()
                if not work_batch:
                    break

                record_objs = []

                for obj in work_batch:
                    if not obj[1]:
                        # no authors. How did it get in here?
                        continue
                    presplit_authors = [a for a in obj[1].split("|") if a is not None]
                    prebuilt_authors = ", ".join(
                        authors.get(i, "Unknown") for i in presplit_authors
                    )
                    prebuilt_authors = (
                        prebuilt_authors[:780] + "..."
                        if len(prebuilt_authors) > 799
                        else prebuilt_authors
                    )
                    record_objs.append(
                        Record(
                            title=obj[0],
                            authors=prebuilt_authors,
                            type=itemtype_book,
                            bibliographic_level=monograph,
                        )
                    )

                new_records = Record.objects.bulk_create(record_objs)
                subject_links = []
                for index, obj in enumerate(work_batch):
                    if obj[2] is None:
                        continue
                    for s in obj[2].split("|"):
                        new_id = subject_dict.get(s)
                        if new_id:
                            subject_links.append(
                                Record.subjects.through(
                                    subject_id=new_id, record_id=new_records[index].id
                                )
                            )

                Record.subjects.through.objects.bulk_create(
                    subject_links, ignore_conflicts=True
                )

                offset += batch_size

        locations = BranchLocation.objects.filter(open_to_public=True)
        records = Record.objects.filter(item__isnull=True)
        items = []
        count = 0
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
            if count % 1000 == 0:
                # flush to database and make more
                Item.objects.bulk_create(items)
                items = []
            count += 1

        self.stdout.write(self.style.SUCCESS("Loaded in data!"))
        self.stdout.write(
            "Run ./manage.py get_gutenberg_images if you want to populate images."
        )

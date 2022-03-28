import json
import random

from django.core.management.base import BaseCommand

from alexandria.catalog.management.commands.import_from_z import generate_LOC_call_number, PUBLISHERS
from alexandria.records.models import Subject, Record, ItemType, BibliographicLevel, Item
from alexandria.users.models import BranchLocation
from alexandria.utils.gutenberg import decompressBytesToString


class Command(BaseCommand):
    help = "Imports data from Project Gutenberg for testing data."

    def handle(self, *args, **options):
        with open('raw_gutenberg_data', 'rb') as f:
            data = json.loads(decompressBytesToString(f.read()))

        subjects = []
        for obj in data['results']:
            subjects += obj['subjects']

        subjects = list(set(subjects))

        if Subject.objects.count() == 0:
            Subject.objects.bulk_create([Subject(name=x) for x in subjects])
            self.stdout.write(self.style.SUCCESS(f"Created {len(subjects)} subjects!"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Subjects already in db, not writing more."))

        itemtype_book = ItemType.objects.get(name='Book')
        monograph = BibliographicLevel.objects.get(name='m')

        if Record.objects.count() == 0:
            self.stdout.write("Creating records...")
            count = 0
            total = len(data['results'])
            for obj in data['results']:
                if count % 1000 == 0:
                    self.stdout.write(f"Created {count}/{total}...")
                new_record = Record.objects.create(
                    title=obj['title'],
                    authors=', '.join(obj['authors']).encode('utf-8').decode(),
                    notes=f"project_gutenberg_id:{obj['id']}",
                    type=itemtype_book,
                    bibliographic_level=monograph,
                )
                new_record.subjects.set(Subject.objects.filter(name__in=obj['subjects']))
                count += 1
        else:
            self.stdout.write(self.style.SUCCESS(f"Records already in db, not writing more."))

        if Item.objects.count() == 0:
            locations = BranchLocation.objects.filter(open_to_public=True)
            records = Record.objects.all()
            record_count = Record.objects.count()
            items = []
            counter = 0
            for r in records:
                if counter % 500 == 0:
                    self.stdout.write(f"Processed {counter}/{record_count}...")
                # maybe we have a few copies
                for _ in range(random.randrange(1, 4)):
                    pubyear = random.randrange(1850, 2021)
                    items.append(Item(
                        barcode=random.getrandbits(50),
                        record=r,
                        price=random.randrange(12, 35) + (random.randrange(0, 100) / 100),
                        home_location=random.choice(locations),
                        is_active=True,
                        call_number=generate_LOC_call_number(pubyear),
                        publisher=random.choice(PUBLISHERS),
                        pubyear=pubyear,
                        bibliographic_level=r.bibliographic_level,
                        type=itemtype_book,
                    ))
                counter += 1
            Item.objects.bulk_create(items)
        else:
            self.stdout.write(self.style.SUCCESS(f"Items already in db, not writing more."))

        self.stdout.write(self.style.SUCCESS("Loaded in data!"))
        self.stdout.write("Run ./manage.py get_gutenberg_images if you want to populate images.")

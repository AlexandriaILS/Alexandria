import time

from django.core.management.base import BaseCommand

from alexandria.records.models import Record
from alexandria.utils.images import get_and_save_image


class Command(BaseCommand):
    help = "Creates all of the permissions groups"

    def handle(self, *args, **options):
        records = Record.objects.filter(notes__contains="project_gutenberg_id")
        url = "https://www.gutenberg.org/cache/epub/{0}/pg{0}.cover.medium.jpg"
        counter = 0
        total = records.count()
        for book in records:
            if counter % 500 == 0:
                self.stdout.write(f"Completed {counter}/{total} images...")
            time.sleep(0.1)
            try:
                get_and_save_image(url.format(book.notes.split(":")[1]), book)
                book.save()
            except:
                self.stdout.write(f"Error on {book.id} -- continuing.")
            counter += 1

        self.stdout.write(self.style.SUCCESS("Images saved!"))

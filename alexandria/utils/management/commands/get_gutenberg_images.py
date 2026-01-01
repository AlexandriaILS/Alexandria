import time

from django.core.management.base import BaseCommand
from rich.progress import track

from alexandria.records.models import Record
from alexandria.utils.images import get_and_save_image


class Command(BaseCommand):
    help = "Creates all of the permissions groups"

    def handle(self, *args, **options):
        records = Record.objects.filter(notes__contains="project_gutenberg_id")
        url = "https://www.gutenberg.org/cache/epub/{0}/pg{0}.cover.medium.jpg"

        for book in track(records, description="Getting images..."):
            time.sleep(0.1)
            try:
                get_and_save_image.enqueue(url.format(book.notes.split(":")[1]), record_id=book.id)
            except:
                self.stdout.write(f"Error on {book.id} -- continuing.")

        self.stdout.write(self.style.SUCCESS("Images saved!"))

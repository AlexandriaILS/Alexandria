from django.core.management.base import BaseCommand

from catalog.models import Record
from catalog.zenodotus_utils import upload


class Command(BaseCommand):
    help = "Upload records to Zenodotus!"

    def handle(self, *args, **options):
        for item in Record.objects.all():
            self.stdout.write(self.style.HTTP_INFO(f"Processing {item}..."))
            try:
                if upload(item):
                    self.stdout.write(self.style.SUCCESS(f"Record added!"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Record already present."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Something went wrong: {e}"))

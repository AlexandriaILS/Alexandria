from django.core.management.base import BaseCommand
from rich.progress import track

from alexandria.records.models import Record, Subject
from alexandria.users.models import User


class Command(BaseCommand):
    help = "Force update of all searchable fields by re-saving all relevant records."

    def handle(self, *args, **options):
        models_to_update = [Record, Subject, User]

        for model in models_to_update:
            count = model.objects.count()

            # Using iterator() with a chunk size for memory efficiency
            for instance in track(
                model.objects.all().iterator(chunk_size=1000),
                description=f"Updating {model.__name__}...",
                total=count,
            ):
                instance.save()

            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated all {model.__name__}s.")
            )

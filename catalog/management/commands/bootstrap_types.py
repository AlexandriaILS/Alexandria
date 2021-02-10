from django.core.management.base import BaseCommand
from catalog.models import ItemTypeBase


class Command(BaseCommand):
    help = "Creates the base types"

    def handle(self, *args, **options):

        count = 0

        for t in ItemTypeBase.TYPE_OPTIONS:
            item, created = ItemTypeBase.objects.get_or_create(name=t[0])
            if created:
                count += 1

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("No changes made; all objects present.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Created {count} missing base types.")
            )

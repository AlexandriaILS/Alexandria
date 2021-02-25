from django.core.management.base import BaseCommand
from catalog.models import ItemTypeBase, BibliographicLevel


class Command(BaseCommand):
    help = "Creates the base types"

    def handle(self, *args, **options):

        items = [
            (ItemTypeBase, ItemTypeBase.TYPE_OPTIONS),
            (BibliographicLevel, BibliographicLevel.LEVEL_OPTIONS),
        ]

        for model, options in items:
            count = 0
            for i in options:
                item, created = model.objects.get_or_create(name=i[0])
                if created:
                    count += 1

            if count == 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"No changes made; all objects present for {str(model)}."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {count} missing base types in {str(model)}"
                    )
                )

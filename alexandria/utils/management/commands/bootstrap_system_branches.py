from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates the base types"

    def handle(self, *args, **options):
        from alexandria.users.models import BranchLocation

        items = ["In Transit", "Ready for Pickup", "Mending", "Discarded", "ILL"]
        # TODO: add support for Interlibrary Loan
        count = 0
        for option in items:
            item, created = BranchLocation.objects.get_or_create(
                name=option, open_to_public=False, host=settings.DEFAULT_SYSTEM_HOST_KEY
            )
            if created:
                count += 1

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"No changes made; all objects present for {str(BranchLocation)}."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Created {count} missing system branches!")
            )

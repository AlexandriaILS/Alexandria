from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Creates the base types"

    def handle(self, *args, **options):
        from alexandria.users.models import BranchLocation

        items = ["in_transit", "ready_for_pickup", "mending", "discarded"]
        count = 0
        for option in items:
            item, created = BranchLocation.objects.get_or_create(
                name=option, host=settings.DEFAULT_SYSTEM_HOST_KEY
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

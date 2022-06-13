from django.core.management.base import BaseCommand

from alexandria.distributed.models import Domain


class Command(BaseCommand):
    help = "Creates the base types"

    def handle(self, *args, **options):
        from alexandria.users.models import BranchLocation

        items = [
            "In Transit",
            "Ready for Pickup",
            "Mending",
            "Discarded",
            "ILL",
            "Shelving Cart",
        ]
        # TODO: add support for Interlibrary Loan
        count = 0
        for option in items:
            item, created = BranchLocation.objects.get_or_create(
                name=option, open_to_public=False, host=Domain.get_system()
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

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from alexandria.catalog.management.commands import bootstrap_system_branches
from alexandria.catalog.management.commands import bootstrap_types
from alexandria.users.management.commands import create_permissions_groups

from alexandria.users.models import USLocation


class Command(BaseCommand):
    help = "Creates everything needed for the site to be functional."

    def handle(self, *args, **options):
        bootstrap_types.Command().handle()
        bootstrap_system_branches.Command().handle()
        create_permissions_groups.Command().handle()

        location, created = USLocation.objects.get_or_create(
            address_1="123 Sesame St.",
            city="Kaufman Astoria Studios",
            state="NY",
            zip_code="11106",
        )
        user, created = get_user_model().objects.get_or_create(
            card_number="1234",
            is_staff=True,
            is_superuser=True,
            first_name="Admin",
            last_name="von Admin",
            address=location
        )
        if created:
            user.set_password("asdf")
            user.save()

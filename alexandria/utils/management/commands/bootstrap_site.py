from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from alexandria.users.models import AccountType, USLocation
from alexandria.utils.management.commands import (
    bootstrap_system_branches,
    bootstrap_types,
    create_permissions_groups,
)


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
            email="adminvonadmin@example.com",
            birth_year=1900,
            account_type=AccountType.objects.get(name="Superuser"),
            title="Admin Extraordinaire",
            legal_first_name="Admin",
            legal_last_name="von Admin",
            address=location,
            notes="It's the admin.",
        )
        if created:
            user.set_password("asdf")
            user.save()

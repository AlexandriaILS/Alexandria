from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from catalog.management.commands import bootstrap_types


class Command(BaseCommand):
    help = "Creates everything needed for the site to be functional."

    def handle(self, *args, **options):
        bootstrap_types.Command().handle()
        user, created = get_user_model().objects.get_or_create(
            card_number=1234,
            is_staff=True,
            is_superuser=True,
            first_name="Admin",
            last_name="von Admin",
        )
        if created:
            user.set_password("asdf")
            user.save()

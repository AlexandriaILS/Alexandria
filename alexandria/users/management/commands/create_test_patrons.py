import random
import string
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from alexandria.users.models import User, USLocation, BranchLocation


class Command(BaseCommand):
    help = "Creates X (int) number of patrons for tests."

    def add_arguments(self, parser):
        parser.add_argument("count", type=int)

    def handle(self, *args, **options):
        count = options["count"]
        try:
            from mimesis import Person
            from mimesis import Address
        except ImportError:
            raise CommandError("Cannot proceed; missing dev dependencies.")

        person = Person()
        address = Address()

        for _ in range(count):
            location = USLocation.objects.create(
                address_1=address.address(),
                city=address.city(),
                state=address.state(),
                zip_code=address.zip_code(),
            )
            AGE = person.age(minimum=0)
            newbie = User.objects.create(
                card_number="".join([random.choice(string.digits) for _ in range(14)]),
                address=location,
                first_name=person.first_name(),
                last_name=person.last_name(),
                email=person.email(),
                birth_year=datetime.now().year - AGE,
                is_minor=True if AGE < 18 else False,
                is_staff=False,
                default_branch=random.choice(
                    list(
                        BranchLocation.objects.filter(
                            open_to_public=True, host=settings.DEFAULT_HOST_KEY
                        )
                    )
                ),
            )
            newbie.set_password("asdf")
            newbie.save()

        self.stdout.write(self.style.SUCCESS(f"Created {str(count)} new patrons!"))

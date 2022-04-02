import random
import string
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from alexandria.users.models import User, USLocation, BranchLocation
from alexandria.utils import us_state_to_abbrev

try:
    from mimesis import Person
    from mimesis import Address
except ImportError:
    raise CommandError("Cannot proceed; missing dev dependencies.")


class Command(BaseCommand):
    help = "Creates X (int) number of patrons for tests."

    def add_arguments(self, parser):
        parser.add_argument("count", type=int)

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(f"Creating new patrons. This may take a minute or two.")

        person = Person()
        address = Address()

        addresses = []
        people = []

        valid_branches = BranchLocation.objects.filter(
            open_to_public=True, host=settings.DEFAULT_HOST_KEY
        )

        self.stdout.write("Generating locations...")

        for x in range(count):
            addresses.append(
                USLocation(
                    address_1=address.address(),
                    city=address.city(),
                    state=us_state_to_abbrev[address.state()],
                    zip_code=address.zip_code(),
                )
            )
        USLocation.objects.bulk_create(addresses)

        self.stdout.write("Generating patrons...")
        for x in range(count):
            age = person.age(minimum=0)

            people.append(
                User(
                    card_number="".join(
                        [random.choice(string.digits) for _ in range(14)]
                    ),
                    address=USLocation.objects.get(
                        id=x + 2
                    ),  # account for zero and the admin address
                    first_name=person.first_name(),
                    last_name=person.last_name(),
                    email=person.email(),
                    birth_year=datetime.now().year - age,
                    is_minor=True if age < 18 else False,
                    is_staff=False,
                    default_branch=random.choice(valid_branches),
                )
            )

        User.objects.bulk_create(people)

        self.stdout.write(self.style.SUCCESS(f"Created {str(count)} new patrons!"))

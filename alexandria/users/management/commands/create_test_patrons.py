import random
import string
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from rich.progress import track

from alexandria.distributed.models import Domain
from alexandria.users.models import AccountType, BranchLocation, User, USLocation
from alexandria.utils import us_state_to_abbrev

try:
    from mimesis import Address, Person
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
            open_to_public=True, host=Domain.get_default()
        )

        for x in track(range(count), description="[green]Generating locations..."):
            addresses.append(
                USLocation(
                    address_1=address.address(),
                    city=address.city(),
                    state=us_state_to_abbrev[address.state()],
                    zip_code=address.zip_code(),
                )
            )
        USLocation.objects.bulk_create(addresses)

        patron = AccountType.objects.create(name="Patron")
        underage = AccountType.objects.create(
            name="Patron (under 18)",
            checkout_limit=10,
            hold_limit=25,
        )

        for x in track(range(count), description="[green]Generating patrons..."):
            age = person.age(minimum=0)

            people.append(
                User(
                    card_number="".join(
                        [random.choice(string.digits) for _ in range(14)]
                    ),
                    address=USLocation.objects.get(
                        id=x + 2
                    ),  # account for zero and the admin address
                    legal_first_name=person.first_name(),
                    legal_last_name=person.last_name(),
                    account_type=underage if age < 18 else patron,
                    email=person.email(),
                    birth_year=datetime.now().year - age,
                    is_minor=True if age < 18 else False,
                    default_branch=random.choice(valid_branches),
                )
            )

        User.objects.bulk_create(people)

        self.stdout.write(self.style.NOTICE(f"Created {str(count)} new patrons."))

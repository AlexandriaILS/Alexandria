import random
import string

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from alexandria.users.models import AccountType, BranchLocation, User, USLocation
from alexandria.utils import us_state_to_abbrev


class Command(BaseCommand):
    help = "Creates X (int) number of staff members with varying permissions for tests."

    def add_arguments(self, parser):
        parser.add_argument("count", type=int)

    def handle(self, *args, **options):
        count = options["count"]
        try:
            from mimesis import Address, Person
        except ImportError:
            raise CommandError("Cannot proceed; missing dev dependencies.")

        person = Person()
        address = Address()

        # get a better distribution of options up in here
        position = ["Manager", "In Charge", "Circ Supervisor"]
        position += ["Librarian"] * 5
        position += ["Circ General", "Page"] * 2

        valid_branches = list(
            BranchLocation.objects.filter(
                open_to_public=True, host=settings.DEFAULT_HOST_KEY
            )
        )

        for _ in range(count):
            location = USLocation.objects.create(
                address_1=address.address(),
                city=address.city(),
                state=us_state_to_abbrev[address.state()],
                zip_code=address.zip_code(),
            )
            title = random.choice(position)
            newbie = User.objects.create(
                card_number="".join([random.choice(string.digits) for _ in range(14)]),
                address=location,
                title=title,
                account_type=AccountType.objects.get(name=title),
                first_name=person.first_name(),
                last_name=person.last_name(),
                email=person.email(),
                birth_year=2021 - person.age(minimum=20),
                default_branch=random.choice(valid_branches),
                work_branch=random.choice(valid_branches),
            )
            newbie.set_password("asdf")
            newbie.save()

        self.stdout.write(
            self.style.SUCCESS(f"Created {str(count)} new staff members!")
        )

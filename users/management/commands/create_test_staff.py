import random
import string

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from users.models import AlexandriaUser, USLocation, BranchLocation



class Command(BaseCommand):
    help = 'Creates X (int) number of staff members with varying permissions for tests.'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        count = options['count']
        try:
            from mimesis import Person
            from mimesis import Address
        except ImportError:
            raise CommandError("Cannot proceed; missing dev dependencies.")

        person = Person()
        address = Address()

        # get a better distribution of options up in here
        position = ['Manager', 'In Charge', 'Circ Supervisor']
        position += ['Librarian'] * 5
        position += ['Circ General', 'Page'] * 2

        for _ in range(count):
            location = USLocation.objects.create(
                address_1=address.address(),
                city=address.city(),
                state=address.state(),
                zip_code=address.zip_code()
            )
            title = random.choice(position)
            perms = Group.objects.get(name=title)
            newbie = AlexandriaUser.objects.create(
                card_number=''.join([random.choice(string.digits) for i in range(14)]),
                address=location,
                title=title,
                first_name=person.first_name(),
                last_name=person.last_name(),
                email=person.email(),
                birth_year=2021 - person.age(minimum=20),
                is_staff=True,
                default_branch=random.choice(
                    list(BranchLocation.objects.filter(open_to_public=True, host=settings.DEFAULT_HOST_KEY)))
            )
            newbie.groups.add(perms)
            newbie.save()

        self.stdout.write(self.style.SUCCESS(f"Created {str(count)} new staff members!"))

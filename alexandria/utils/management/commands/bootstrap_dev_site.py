from django.core.management.base import BaseCommand
from mimesis.providers import Address

from alexandria.distributed.management.commands import write_default_settings
from alexandria.records.models import ItemType, ItemTypeBase
from alexandria.users.management.commands import create_test_patrons, create_test_staff
from alexandria.users.models import BranchLocation, USLocation
from alexandria.utils import us_state_to_abbrev
from alexandria.utils.management.commands import (
    bootstrap_site,
    force_searchable_fields,
    import_gutenberg_titles,
)

BRANCH_LOCATIONS = [
    "Crickhollow",
    "Frogmorton",
    "Gamwitch",
    "Hobbiton",
    "Little Delving",
    "Michel Delving",
    "Overhill",
    "Rushey",
    "Tuckborough",
    "Willowbottom",
    "Woodhall",
]

CASSETTE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg"'
    ' xmlns:xlink="http://www.w3.org/1999/xlink"'
    ' version="1.1"'
    ' id="mdi-cassette"'
    ' width="36"'
    ' height="36"'
    ' viewBox="2 2 20 20">'
    "<path"
    ' fill="currentColor"'
    ' d="M4,5A2,2 0 0,0 2,7V17A2,2 0 0,0 4,19H6L7,17H17L18,19H20A2,2 0 0,0 22,17V7A2,'
    "2 0 0,0 20,5H4M6.5,10A1.5,1.5 0 0,1 8,11.5A1.5,1.5 0 0,1 6.5,13A1.5,1.5 0 0,1 5,"
    "11.5A1.5,1.5 0 0,1 6.5,10M9,10H15V13H9V10M17.5,10A1.5,1.5 0 0,1 19,11.5A1.5,"
    '1.5 0 0,1 17.5,13A1.5,1.5 0 0,1 16,11.5A1.5,1.5 0 0,1 17.5,10Z" />'
    "</svg>"
)


def create_test_locations_and_types():
    address = Address()
    for branch in [
        "Crickhollow",
        "Frogmorton",
        "Gamwitch",
        "Hobbiton",
        "Little Delving",
        "Michel Delving",
        "Overhill",
        "Rushey",
        "Tuckborough",
        "Willowbottom",
        "Woodhall",
    ]:
        location = USLocation.objects.create(
            address_1=address.address(),
            city=address.city(),
            state=us_state_to_abbrev[address.state()],
            zip_code=address.zip_code(),
        )
        BranchLocation.objects.get_or_create(name=branch, address=location)

    base = ItemTypeBase.objects.get(name=ItemTypeBase.LANGUAGE_MATERIAL)
    ItemType.objects.get_or_create(name="Audiobook (CD)", base=base, icon_name="album")
    ItemType.objects.get_or_create(name="eBook", base=base, icon_name="tablet_android")
    ItemType.objects.get_or_create(name="Book", base=base, icon_name="auto_stories")
    ItemType.objects.get_or_create(
        name="Audiobook (Cassette)", base=base, icon_svg=CASSETTE_SVG
    )


class Command(BaseCommand):
    help = "Builds the site so that it can be worked on."

    def handle(self, *args, **options):
        # First instantiate the site as normal
        bootstrap_site.Command().handle()
        write_default_settings.Command().handle()
        create_test_locations_and_types()
        # Domain.objects.get_or_create(name="127.0.0.1:8000")
        # roughly 1 librarian for every 600 cardholders
        self.stdout.write("Creating a metric ton of patrons...")
        create_test_patrons.Command().handle(count=12000)
        self.stdout.write("Creating some staff...")
        create_test_staff.Command().handle(count=20)
        self.stdout.write("Building the library...")
        import_gutenberg_titles.Command().handle()
        self.stdout.write("Populating search data...")
        force_searchable_fields.Command().handle()

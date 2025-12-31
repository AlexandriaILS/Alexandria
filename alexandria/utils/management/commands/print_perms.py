from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand
from rich import print
from rich.panel import Panel

from alexandria.utils.permissions import permission_to_perm


class Command(BaseCommand):
    help = "Print the full canonical name of the permissions in Alexandria."

    def handle(self, *args, **options):
        all_perms = Permission.objects.all()

        # We could just print them all out but that's less fun. Let's organize
        # them into sections with Rich.
        categorizations = {}
        for permission in all_perms:
            model = permission.content_type.app_label
            if model in categorizations:
                categorizations[model].append(permission_to_perm(permission))
            else:
                categorizations[model] = [permission_to_perm(permission)]

        for model, perms in categorizations.items():
            print(Panel.fit("\n".join(perms), title=model, title_align="left"))

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates all of the permissions groups"

    def handle(self, *args, **options):
        superuser, _ = Group.objects.get_or_create(name="Superuser")
        manager, _ = Group.objects.get_or_create(name="Manager")
        incharge, _ = Group.objects.get_or_create(name="In Charge")
        librarian, _ = Group.objects.get_or_create(name="Librarian")
        circ_sup, _ = Group.objects.get_or_create(name="Circ Supervisor")
        circ_general, _ = Group.objects.get_or_create(name="Circ General")
        page, _ = Group.objects.get_or_create(name="Page")

        superuser.permissions.set(Permission.objects.all())
        superuser.save()

        manager.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "add_bibliographiclevel",
                    "change_bibliographiclevel",
                    "delete_bibliographiclevel",
                    "view_bibliographiclevel",
                    "add_collection",
                    "change_collection",
                    "delete_collection",
                    "view_collection",
                    "add_item",
                    "change_item",
                    "check_in",
                    "check_out",
                    "delete_item",
                    "view_item",
                    "add_itemtype",
                    "change_itemtype",
                    "delete_itemtype",
                    "view_itemtype",
                    "add_itemtypebase",
                    "change_itemtypebase",
                    "delete_itemtypebase",
                    "view_itemtypebase",
                    "add_record",
                    "change_record",
                    "delete_record",
                    "view_record",
                    "add_subject",
                    "change_subject",
                    "delete_subject",
                    "view_subject",
                    "add_hold",
                    "change_hold",
                    "delete_hold",
                    "view_hold",
                    "add_tag",
                    "change_tag",
                    "delete_tag",
                    "view_tag",
                    "add_taggeditem",
                    "change_taggeditem",
                    "delete_taggeditem",
                    "view_taggeditem",
                    "create_patron_account",
                    "create_staff_account",
                    "delete_patron_account",
                    "delete_staff_account",
                    "edit_user_notes",
                    "generate_financial_reports",
                    "generate_general_reports",
                    "read_patron_account",
                    "read_staff_account",
                    "update_patron_account",
                    "update_staff_account",
                    "add_branchlocation",
                    "change_branchlocation",
                    "delete_branchlocation",
                    "view_branchlocation",
                    "add_uslocation",
                    "change_uslocation",
                    "delete_uslocation",
                    "view_uslocation",
                ]
            )
        )

        incharge.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "view_bibliographiclevel",
                    "add_collection",
                    "change_collection",
                    "delete_collection",
                    "view_collection",
                    "add_item",
                    "change_item",
                    "check_in",
                    "check_out",
                    "delete_item",
                    "view_item",
                    "add_itemtype",
                    "change_itemtype",
                    "delete_itemtype",
                    "view_itemtype",
                    "add_record",
                    "change_record",
                    "delete_record",
                    "view_record",
                    "add_subject",
                    "change_subject",
                    "delete_subject",
                    "view_subject",
                    "add_hold",
                    "change_hold",
                    "delete_hold",
                    "view_hold",
                    "add_tag",
                    "change_tag",
                    "delete_tag",
                    "view_tag",
                    "add_taggeditem",
                    "change_taggeditem",
                    "delete_taggeditem",
                    "view_taggeditem",
                    "create_patron_account",
                    "delete_patron_account",
                    "edit_user_notes",
                    "generate_general_reports",
                    "read_patron_account",
                    "read_staff_account",
                    "update_patron_account",
                    "view_branchlocation",
                    "add_uslocation",
                    "change_uslocation",
                    "delete_uslocation",
                    "view_uslocation",
                ]
            )
        )

        librarian.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "view_bibliographiclevel",
                    "add_collection",
                    "change_collection",
                    "delete_collection",
                    "view_collection",
                    "add_item",
                    "change_item",
                    "check_in",
                    "check_out",
                    "delete_item",
                    "view_item",
                    "add_itemtype",
                    "change_itemtype",
                    "delete_itemtype",
                    "view_itemtype",
                    "add_record",
                    "change_record",
                    "delete_record",
                    "view_record",
                    "add_subject",
                    "change_subject",
                    "delete_subject",
                    "view_subject",
                    "add_hold",
                    "change_hold",
                    "delete_hold",
                    "view_hold",
                    "add_tag",
                    "change_tag",
                    "delete_tag",
                    "view_tag",
                    "add_taggeditem",
                    "change_taggeditem",
                    "delete_taggeditem",
                    "view_taggeditem",
                    "create_patron_account",
                    "delete_patron_account",
                    "edit_user_notes",
                    "read_patron_account",
                    "read_staff_account",
                    "update_patron_account",
                    "view_branchlocation",
                    "add_uslocation",
                    "change_uslocation",
                    "delete_uslocation",
                    "view_uslocation",
                ]
            )
        )

        circ_sup.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "view_bibliographiclevel",
                    "add_collection",
                    "change_collection",
                    "delete_collection",
                    "view_collection",
                    "add_item",
                    "change_item",
                    "check_in",
                    "check_out",
                    "delete_item",
                    "view_item",
                    "add_itemtype",
                    "change_itemtype",
                    "delete_itemtype",
                    "view_itemtype",
                    "add_itemtypebase",
                    "add_record",
                    "change_record",
                    "delete_record",
                    "view_record",
                    "add_subject",
                    "change_subject",
                    "delete_subject",
                    "view_subject",
                    "add_hold",
                    "change_hold",
                    "delete_hold",
                    "view_hold",
                    "add_tag",
                    "change_tag",
                    "delete_tag",
                    "view_tag",
                    "add_taggeditem",
                    "change_taggeditem",
                    "delete_taggeditem",
                    "view_taggeditem",
                    "create_patron_account",
                    "create_staff_account",
                    "delete_patron_account",
                    "delete_staff_account",
                    "edit_user_notes",
                    "generate_financial_reports",
                    "read_patron_account",
                    "read_staff_account",
                    "update_patron_account",
                    "update_staff_account",
                    "view_branchlocation",
                    "add_uslocation",
                    "change_uslocation",
                    "delete_uslocation",
                    "view_uslocation",
                ]
            )
        )

        circ_general.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "view_bibliographiclevel",
                    "add_collection",
                    "change_collection",
                    "delete_collection",
                    "view_collection",
                    "add_item",
                    "change_item",
                    "check_in",
                    "check_out",
                    "delete_item",
                    "view_item",
                    "add_itemtype",
                    "change_itemtype",
                    "delete_itemtype",
                    "view_itemtype",
                    "add_itemtypebase",
                    "add_record",
                    "change_record",
                    "delete_record",
                    "view_record",
                    "add_subject",
                    "change_subject",
                    "delete_subject",
                    "view_subject",
                    "add_hold",
                    "change_hold",
                    "delete_hold",
                    "view_hold",
                    "add_tag",
                    "change_tag",
                    "delete_tag",
                    "view_tag",
                    "add_taggeditem",
                    "change_taggeditem",
                    "delete_taggeditem",
                    "view_taggeditem",
                    "create_patron_account",
                    "delete_patron_account",
                    "edit_user_notes",
                    "read_patron_account",
                    "read_staff_account",
                    "update_patron_account",
                    "update_staff_account",
                    "view_branchlocation",
                    "add_uslocation",
                    "change_uslocation",
                    "delete_uslocation",
                    "view_uslocation",
                ]
            )
        )

        page.permissions.set(
            Permission.objects.filter(
                codename__in=[
                    "view_bibliographiclevel",
                    "view_collection",
                    "check_in",
                    "check_out",
                    "view_item",
                    "view_itemtype",
                    "view_record",
                    "view_subject",
                    "view_tag",
                    "view_branchlocation",
                ]
            )
        )

        self.stdout.write(self.style.SUCCESS("Updated default permissions groups!"))

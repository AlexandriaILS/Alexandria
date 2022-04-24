from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from alexandria.users.models import AccountType


class Command(BaseCommand):
    help = "Creates all of the permissions groups"

    def handle(self, *args, **options):
        superuser, _ = AccountType.objects.get_or_create(
            name="Superuser", is_superuser=True, is_staff=True
        )
        manager, _ = AccountType.objects.get_or_create(name="Manager", is_staff=True)
        incharge, _ = AccountType.objects.get_or_create(name="In Charge", is_staff=True)
        librarian, _ = AccountType.objects.get_or_create(
            name="Librarian", is_staff=True
        )
        circ_sup, _ = AccountType.objects.get_or_create(
            name="Circ Supervisor", is_staff=True
        )
        circ_general, _ = AccountType.objects.get_or_create(
            name="Circ General", is_staff=True
        )
        page, _ = AccountType.objects.get_or_create(name="Page", is_staff=True)

        superuser_group, _ = Group.objects.get_or_create(name="Superuser")
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        incharge_group, _ = Group.objects.get_or_create(name="In Charge")
        librarian_group, _ = Group.objects.get_or_create(name="Librarian")
        circ_sup_group, _ = Group.objects.get_or_create(name="Circ Supervisor")
        circ_general_group, _ = Group.objects.get_or_create(name="Circ General")
        page_group, _ = Group.objects.get_or_create(name="Page")

        superuser.user_permissions.set(Permission.objects.all())
        superuser_group.permissions.set(Permission.objects.all())
        superuser.save()

        manager_perms = Permission.objects.filter(
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
                "add_accounttype",
                "change_accounttype",
                "delete_accounttype",
                "view_accounttype",
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
                "change_patron_account",
                "change_staff_account",
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
        manager.user_permissions.set(manager_perms)
        manager_group.permissions.set(manager_perms)
        manager.save()
        manager_group.save()

        incharge_perms = Permission.objects.filter(
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
                "change_patron_account",
                "view_branchlocation",
                "add_uslocation",
                "change_uslocation",
                "delete_uslocation",
                "view_uslocation",
            ]
        )
        incharge.user_permissions.set(incharge_perms)
        incharge_group.permissions.set(incharge_perms)
        incharge.save()
        incharge_group.save()

        librarian_perms = Permission.objects.filter(
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
                "change_patron_account",
                "view_branchlocation",
                "add_uslocation",
                "change_uslocation",
                "delete_uslocation",
                "view_uslocation",
            ]
        )
        librarian.user_permissions.set(librarian_perms)
        librarian_group.permissions.set(librarian_perms)
        librarian.save()
        librarian_group.save()

        circ_sup_perms = Permission.objects.filter(
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
                "change_patron_account",
                "change_staff_account",
                "view_branchlocation",
                "add_uslocation",
                "change_uslocation",
                "delete_uslocation",
                "view_uslocation",
            ]
        )
        circ_sup.user_permissions.set(circ_sup_perms)
        circ_sup_group.permissions.set(circ_sup_perms)
        circ_sup.save()
        circ_sup_group.save()

        circ_general_perms = Permission.objects.filter(
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
                "change_patron_account",
                "change_staff_account",
                "view_branchlocation",
                "add_uslocation",
                "change_uslocation",
                "delete_uslocation",
                "view_uslocation",
            ]
        )
        circ_general.user_permissions.set(circ_general_perms)
        circ_general_group.permissions.set(circ_general_perms)
        circ_general.save()
        circ_general_group.save()

        page_perms = Permission.objects.filter(
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
        page.user_permissions.set(page_perms)
        page_group.permissions.set(page_perms)
        page.save()
        page_group.save()

        self.stdout.write(self.style.SUCCESS("Updated default permissions groups!"))

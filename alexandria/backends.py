from django.apps import apps
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


class Authentication(ModelBackend):
    def _get_group_permissions(self, user_obj):
        user_groups_field = apps.get_model("users.accounttype")._meta.get_field(
            "groups"
        )
        user_groups_query = "group__%s" % user_groups_field.related_query_name()
        return Permission.objects.filter(**{user_groups_query: user_obj})

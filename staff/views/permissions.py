from django.utils.translation import ugettext as _
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from users.models import AlexandriaUser


class PermissionsView(PermissionRequiredMixin, View):
    permission_required = "users.change_staff_account"

    def get(self, request: WSGIRequest, user_id: int) -> HttpResponse:
        if request.user.is_superuser:
            target_user = get_object_or_404(AlexandriaUser, card_number=user_id)
        else:
            if user_id == request.user.card_number:
                messages.error(request, _("Sorry, you can't edit your own account."))
                raise Http404
            target_user = get_object_or_404(
                AlexandriaUser, card_number=user_id, host=request.host
            )
        return render(request, "staff/permissions.html", {"target_user": target_user})

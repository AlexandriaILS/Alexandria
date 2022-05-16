from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _

from alexandria.api.views import EXPIRED_SESSION, NO_ACTIVE_SESSION
from alexandria.records.models import CheckoutSession, Item
from alexandria.users.models import BranchLocation, User
from alexandria.utils.decorators import htmx_guard_redirect
from alexandria.utils.type_hints import Request


@permission_required("records.check_in")
def check_in(request: Request) -> HttpResponse:
    ...


@permission_required("records.check_out")
def check_out(request: Request) -> HttpResponse:
    return render(request, "staff/checkout.html", {"title": _("Check Out")})


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_htmx(request: Request) -> HttpResponse:
    # If a staff member is currently checking out someone and the page reloads or
    # something, give them the session that they were using.
    # Otherwise, create a new session and pass that back.
    if checkout_session := request.user.get_active_checkout_session():
        if checkout_session.session_target is not None:
            # todo: also check for expired session
            return render(
                request,
                "fragments/check_out.partial",
                {"checkout_session": checkout_session},
            )
        else:
            checkout_session.delete()

    CheckoutSession.objects.create(session_user=request.user)
    return render(request, "fragments/check_out_new_session.partial")


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_set_target_htmx(request: Request) -> HttpResponse:
    # After a new checkout session has been created, we need to identify
    # who we are checking things out to. Checkout targets can be users
    # or they can be branchlocations.
    session = request.user.get_active_checkout_session()

    if not session:
        return JsonResponse(
            data={
                "message": _(
                    "There is no checkout session currently active."
                    " Please refresh the page."
                )
            },
            status=NO_ACTIVE_SESSION,
        )

    # By default, a session is valid for 24 hours. Don't leave the browser tab open
    # for more than a day.
    if session.is_expired():
        session.delete()
        return JsonResponse(
            data={
                "message": _(
                    "The checkout session has expired. Please refresh the page."
                )
            },
            status=EXPIRED_SESSION,
        )

    patron_id = request.POST.get("card_number")
    building_id = request.POST.get("branch_select")
    system_building_id = request.POST.get("system_branch_select")

    if patron_id:
        target = User.objects.filter(card_number=patron_id, host=request.host).first()
    elif building_id:
        target = BranchLocation.objects.filter(
            id=building_id, host=request.host
        ).first()
    else:
        target = BranchLocation.objects.filter(
            id=system_building_id, host=settings.DEFAULT_SYSTEM_HOST_KEY
        ).first()

    if not target:
        return JsonResponse(data={"message": _("Invalid ID.")}, status=404)

    session.session_target = target
    session.save()

    return check_out_htmx(request)


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_additional_options_htmx(request: Request) -> HttpResponse:
    return render(request, "fragments/check_out_building_status.partial")


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_item_htmx(request: Request) -> HttpResponse:
    session: CheckoutSession = request.user.get_active_checkout_session()
    if not session:
        return JsonResponse(
            data={
                "message": _("There is no checkout session currently active."),
            },
            status=NO_ACTIVE_SESSION,
        )

    # By default, a session is valid for 24 hours. Don't leave the browser tab open
    # for more than a day.
    if session.is_expired():
        session.delete()
        return JsonResponse(
            data={"message": _("The checkout session has expired.")},
            status=EXPIRED_SESSION,
        )

    item_id = request.POST.get("item_id")

    if not item_id:
        return JsonResponse(
            data={"message": _("Missing item ID... please try again.")}, status=400
        )

    item = Item.objects.filter(host=request.host, barcode=item_id).first()
    if not item:
        return JsonResponse(
            data={"message": _("No item found with that ID.")}, status=400
        )

    # The session target is either a user or a branchlocation
    check, message = session.session_target.can_checkout_item(item)

    if not check:
        JsonResponse(data={"message": message}, status=400)

    if session.items.filter(barcode=item_id).exists():
        return JsonResponse(
            data={"message": _("That item is already in the list.")}, status=400
        )

    # We got this far, so we can actually do the checkout thing now.
    session.items.add(item)
    return render(
        request, "fragments/check_out_item_list.partial", {"items": session.items.all()}
    )


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_session_finish_htmx(request: Request) -> HttpResponse:
    session: CheckoutSession = request.user.get_active_checkout_session()
    if not session:
        return JsonResponse(
            data={
                "message": _("There is no checkout session currently active."),
            },
            status=NO_ACTIVE_SESSION,
        )

    for item in session.items.all():
        item.check_out_to(session.session_target)

    # TODO: Receipt here?
    session.delete()
    messages.success(request, _("All done!"))
    return check_out_htmx(request)


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_session_cancel_htmx(request: Request) -> HttpResponse:
    session: CheckoutSession = request.user.get_active_checkout_session()
    if session:
        # delete the session if it exists, just continue on if it doesn't.
        session.delete()

    messages.info(request, _("Check out session has been cancelled."))

    return check_out_htmx(request)

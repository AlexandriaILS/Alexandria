from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext as _

from alexandria.api.views import EXPIRED_SESSION, NO_ACTIVE_SESSION
from alexandria.distributed.models import Domain
from alexandria.records.models import CheckoutSession, Hold, Item
from alexandria.records.views.checkout_utils import create_toast, Toasts
from alexandria.users.models import BranchLocation, User
from alexandria.utils.decorators import htmx_guard_redirect
from alexandria.utils.type_hints import Request


@permission_required("records.check_out")
def check_out(request: Request) -> HttpResponse:
    return render(request, "staff/checkout.html", {"title": _("Check Out")})


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_htmx(request: Request, receipt: str = None) -> HttpResponse:
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
    # if we get a receipt, that means that we just finished a session. Show the
    # new session page along with the command to print the old session's receipt.
    context = {"receipt": receipt} if receipt else {}
    return render(request, "fragments/check_out_new_session.partial", context)


def session_validity_check(
    session: CheckoutSession, session_check_only=False
) -> JsonResponse | None:
    if not session:
        return create_toast(Toasts.NO_ACTIVE_CHECKOUT_SESSION, status=NO_ACTIVE_SESSION)

    # By default, a session is valid for 24 hours. Don't leave the browser tab open
    # for more than a day.
    if not session_check_only:
        if session.is_expired():
            session.delete()
            return create_toast(Toasts.EXPIRED_CHECKOUT_SESSION, status=EXPIRED_SESSION)


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_set_target_htmx(request: Request) -> HttpResponse:
    # After a new checkout session has been created, we need to identify
    # who we are checking things out to. Checkout targets can be users
    # or they can be branchlocations.
    session = request.user.get_active_checkout_session()
    if resp := session_validity_check(session):
        return resp

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
            id=system_building_id, host=Domain.get_system()
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
    if resp := session_validity_check(session):
        return resp

    item_id = request.POST.get("item_id")

    if not item_id:
        return create_toast(Toasts.MISSING_ITEM_ID)

    item = Item.objects.filter(host=request.host, barcode=item_id).first()
    if not item:
        return create_toast(Toasts.NO_ITEM_FOUND)

    # The session target is either a user or a branchlocation
    check, message = session.session_target.can_checkout_item(item)

    if not check:
        JsonResponse(data={"message": message}, status=400)

    if session.items.filter(barcode=item_id).exists():
        return create_toast(Toasts.ITEM_ALREADY_PRESENT)

    # We got this far, so we can actually do the checkout thing now.
    session.items.add(item)
    return render(
        request, "fragments/check_out_item_list.partial", {"items": session.items.all()}
    )


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_session_finish_htmx(request: Request) -> HttpResponse:
    session: CheckoutSession = request.user.get_active_checkout_session()
    if resp := session_validity_check(session, session_check_only=True):
        return resp

    add_money = (
        session.session_target.is_user
        and request.settings.enable_running_borrow_saved_money
    )
    user_money_saved = session.session_target.saved_money if add_money else 0

    for item in session.items.all():
        item.check_out_to(session.session_target)
        if add_money:
            user_money_saved += item.price

    if add_money:
        # we don't really have to worry about race conditions here because one
        # person won't be checking out all over the place at the same time
        session.session_target.saved_money = user_money_saved
        session.session_target.save()

    receipt = session.get_receipt(request)
    session.delete()
    messages.success(request, _("All done!"))
    return check_out_htmx(request, receipt=receipt)


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_remove_item_htmx(request: Request, item_id: str) -> HttpResponse:
    session: CheckoutSession = request.user.get_active_checkout_session()
    if resp := session_validity_check(session, session_check_only=True):
        return resp

    item = Item.objects.filter(host=request.host, barcode=item_id).first()

    session.items.remove(item)
    return render(
        request, "fragments/check_out_item_list.partial", {"items": session.items.all()}
    )


@permission_required("records.check_out")
@htmx_guard_redirect("check_out")
def check_out_session_cancel_htmx(request: Request) -> HttpResponse:
    session: CheckoutSession = request.user.get_active_checkout_session()
    if session:
        # delete the session if it exists, just continue on if it doesn't.
        session.delete()

    messages.info(request, _("Check out session has been cancelled."))

    return check_out_htmx(request)


@permission_required("records.check_in")
def check_in(request: Request) -> HttpResponse:
    return render(request, "staff/checkin.html", {"title": _("Check In")})


@permission_required("records.check_in")
@htmx_guard_redirect("check_in")
def check_in_htmx(request: Request) -> HttpResponse | JsonResponse:
    branch_id = request.POST.get("branch_select")
    # Make sure the building exists and that we have access to it.
    # Obviously this should never get hit because it's a dropdown but never
    # underestimate users
    branch = BranchLocation.objects.filter(id=branch_id, host=request.host).first()
    if not branch:
        return JsonResponse(
            data={
                "message": _(
                    "How did you select that??"
                    " Pick a building you have access to, please!"
                )
            },
            status=400,
        )
    # can't serialize the object; tack the ID onto the session for later
    request.session["checkin_building_id"] = branch_id
    return render(request, "fragments/check_in.partial", {"branch_name": branch.name})


@permission_required("records.check_in")
def check_in_session_finish(request: Request) -> HttpResponseRedirect:
    del request.session["checkin_building_id"]
    return HttpResponseRedirect(reverse("check_in"))


@permission_required("records.check_in")
@htmx_guard_redirect("check_in")
def check_in_item_htmx(request: Request) -> HttpResponse:
    item_id = request.POST.get("item_id")

    if not item_id:
        return create_toast(Toasts.MISSING_ITEM_ID)

    item = Item.objects.filter(host=request.host, barcode=item_id).first()
    if not item:
        return create_toast(Toasts.NO_ITEM_FOUND)

    # Process:
    #
    # * See if it's part of a requested hold
    #   * check out to In Transit
    #   * print hold receipt
    #   * end
    # * Verify floating collection status
    #   * if floating collection, end
    #   * if not floating collection:
    #     * if current checkin location == item.home_location, end
    #     * else checkout to In Transit, print receipt, end
    # * Otherwise, check in the item (by making it not checked out to anyone)

    context = {"item": item, "bg_style": "success"}
    current_location = BranchLocation.objects.get(
        id=request.session["checkin_building_id"]
    )

    hold = Hold.objects.filter(item=item).order_by("created_at").first()
    needs_transport = False

    if hold:
        if hold.destination != current_location:
            needs_transport = True
            context |= {"redirect_to": hold.destination}
        else:
            # it's not going anywhere, so pass that info to the template
            context |= {"is_hold": True}
    else:
        if (
            item.home_location != current_location
            and not request.settings.floating_collection
        ):
            needs_transport = True
            context |= {"redirect_to": item.home_location}

    if needs_transport:
        context |= {
            "receipt": context["redirect_to"].get_transport_receipt(request),
            "bg_style": "info",
        }
        item.check_out_to(BranchLocation.objects.get(name="In Transit"))
    elif hold:
        # holds should only be processed when they have arrived at their destination
        context |= {"receipt": hold.get_receipt(request), "bg_style": "warning"}
        item.check_out_to(BranchLocation.objects.get(name="Ready for Pickup"))
    else:
        if request.settings.use_shelving_cart:
            item.check_out_to(BranchLocation.objects.get(name="Shelving Cart"))
        else:
            item.checked_out_to = None
            item.save()

    return render(request, "fragments/check_in_single_item.partial", context)

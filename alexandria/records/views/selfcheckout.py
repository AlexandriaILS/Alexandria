"""
This should be everything you need to build a cheap self-check-out station.
Ideally this should only require a raspberry pi and a scanner, this should
have the following functionality:

* single page (primarily, login doesn't count)
* requires staff login to start (don't want people checking out arbitrary materials at home)
* offers print ability for receipts
* offers email receipt
"""
from typing import Optional

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status

from alexandria.records.models import CheckoutSession, Item
from alexandria.records.views.checkout_utils import create_toast, Toasts
from alexandria.users.models import User
from alexandria.utils.decorators import htmx_guard_redirect
from alexandria.utils.type_hints import Request


def get_user_and_selfcheck_session(
    request: Request, user_id: str = None
) -> tuple[Optional[User], Optional[CheckoutSession]]:
    # TODO: clean this up
    if not user_id:
        user_id = (
            request.POST.get("user_id")  # selfcheck after starting
            or request.POST.get("card_number")  # first selfcheck page
            or request.GET.get("user_id")  # selfcheck remove item button
        )
    user = User.objects.filter(host=request.host, card_number=user_id).first()
    if not user:
        return None, None
    return user, user.get_active_checkout_session()


def index(request):
    return render(
        request, "selfcheckout/selfcheck_start.html", {"hide_back_button": True}
    )


@htmx_guard_redirect("self_check_out")
def get_user_card_htmx(request, show_error=False):
    return render(
        request, "selfcheckout/get_card.partial", {"show_card_error": show_error}
    )


@htmx_guard_redirect("self_check_out")
def start_selfcheck_session_htmx(request):
    # Check that the card number submitted is valid and return an error if it
    # isn't. We aren't using request.user for any of this because request.user
    # is the staff member who logged into the self-checkout machines.
    user, existing_session = get_user_and_selfcheck_session(request)
    if not user:
        return get_user_card_htmx(request, show_error=True)

    if existing_session:
        # we don't care about a dead session here. They start at a selfcheck
        # machine & they end at the same machine. If they pop up somewhere, we
        # should assume technical difficulty and restart the process.
        existing_session.delete()

    # create a session by the user for the user
    CheckoutSession.objects.create(session_user=user, session_target=user)
    return render(
        request, "selfcheckout/selfcheck_main.partial", {"user_id": user.card_number}
    )


@htmx_guard_redirect("self_check_out")
def selfcheck_item_htmx(request):
    # Now that we've got a session, the user standing at the self-check would
    # like to check out an item. We need to:
    #
    # 1: make sure they have an active session
    #    - since the active user ID is stored in the html and submitted as part
    #      of the form, we need to make sure that it hasn't been tampered with.
    # 2: get the active session
    # 3: add items to session
    # 4: return an updated list of items for the current transaction
    user, existing_session = get_user_and_selfcheck_session(request)
    if not existing_session:
        # Something went wrong; maybe the session expired or someone is
        # trying to tamper. Either way, we should abort now.
        return render(
            request,
            "selfcheckout/get_card.partial",
            {"show_invalid_session_error": True},
        )

    if existing_session.is_expired():
        existing_session.delete()
        return render(
            request,
            "selfcheckout/get_card.partial",
            {"show_invalid_session_error": True},
        )

    item_id = request.POST.get("item_id")
    item = Item.objects.filter(host=request.host, barcode=item_id).first()
    if not item:
        return create_toast(Toasts.NO_ITEM_FOUND)

    if existing_session.items.contains(item):
        return create_toast(Toasts.ITEM_ALREADY_PRESENT)

    existing_session.items.add(item)

    return render(
        request,
        "selfcheckout/selfcheck_main.partial",
        {
            "user_id": user.card_number,
            "items": existing_session.items.all(),
        },
    )


@htmx_guard_redirect("self_check_out")
def selfcheck_remove_item_htmx(request: Request, item_id: str) -> HttpResponse:
    user, existing_session = get_user_and_selfcheck_session(request)
    if not existing_session:
        return create_toast(
            Toasts.EXPIRED_CHECKOUT_SESSION, status=status.HTTP_423_LOCKED
        )

    item = Item.objects.filter(host=request.host, barcode=item_id).first()

    existing_session.items.remove(item)
    return render(
        request,
        "partials/selfcheck_item_list.partial",
        {"items": existing_session.items.all()},
    )


@htmx_guard_redirect("self_check_out")
def selfcheckout_finish_htmx(request: Request, user_id: str) -> HttpResponse:
    user, session = get_user_and_selfcheck_session(request, user_id)

    add_money = request.settings.enable_running_borrow_saved_money
    user_money_saved = session.session_target.saved_money if add_money else 0

    for item in session.items.all():
        item.check_out_to(session.session_target)
        if add_money:
            user_money_saved += item.price

    if add_money:
        session.session_target.saved_money = user_money_saved
        session.session_target.save()

    receipt = session.get_receipt(request)
    session.delete()
    return render(request, "partials/selfcheck_end.partial", {"receipt": receipt})

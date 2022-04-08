from django.shortcuts import reverse
from django.test import Client

from alexandria.utils.test_helpers import DEFAULT_PATRON_USER, get_default_patron_user


def test_login(client: Client):
    user = get_default_patron_user()

    result = client.get(reverse("login"))
    assert result.status_code == 200

    result = client.post(
        reverse("login"),
        data={
            "card_number": user.card_number,
            "password": DEFAULT_PATRON_USER["password"],
            "csrf_token": result.context["csrf_token"],
        },
    )
    assert result.status_code == 302
    assert result.url == reverse("homepage")


def test_bad_login(client: Client):
    user = get_default_patron_user()

    result = client.get(reverse("login"))
    assert result.status_code == 200

    result = client.post(
        reverse("login"),
        data={
            "card_number": user.card_number,
            "password": "definitely not the right password",
            "csrf_token": result.context["csrf_token"],
        },
    )

    assert result.status_code == 302
    assert reverse("login") in result.url

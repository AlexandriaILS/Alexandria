from alexandria.users.models import User


def add_patron_acted_as(request, data) -> dict:
    """If we're currently acting as a patron, add them to the context."""
    if id_number := request.session.get("acting_as_patron"):
        if target_user := User.objects.filter(card_number=id_number, host=request.host).first():
            data['acting_as_patron_obj'] = target_user

    return data

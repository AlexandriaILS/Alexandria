from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    # https://stackoverflow.com/a/30875830
    # tl;dr: when using sessions, DRF normally applies CSRF to POST requests.
    # Because we aren't doing that (just AJAX from the site) then we intentionally
    # kill the CSRF check by making it return immediately.

    def enforce_csrf(self, request):
        return

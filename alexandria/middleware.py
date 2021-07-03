import sys
from better_exceptions import excepthook

from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import DisallowedHost
from alexandria.configs import sites


DEFAULT_HOSTS = ["localhost:8000", "alexandrialibrary.dev"]


class HostValidationMiddleware(MiddlewareMixin):
    # Verify that the host that is currently requesting the site is actually
    # supposed to be here, then attach the relevant configs for this request
    # to the object.
    def process_request(self, request):
        host = request.get_host()
        if host in DEFAULT_HOSTS:
            request.context = sites["DEFAULT"]
            request.host = "default"
        elif host_data := sites.get(host):
            request.context = host_data
            request.host = host
            for key in sites["DEFAULT"].keys():
                # make sure that any missing fields are populated with the defaults
                if not request.context.get(key):
                    request.context[key] = sites["DEFAULT"][key]
        else:
            raise DisallowedHost

# For debug purposes only. Link to local_settings by adding
# `blossom.middleware.BetterExceptionsMiddleware`
# to the top of the middleware stack.
class BetterExceptionsMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        excepthook(exception.__class__, exception, sys.exc_info()[2])
        return None

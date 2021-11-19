import sys
from better_exceptions import excepthook

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.exceptions import DisallowedHost
from alexandria.configs import load_site_config
from utils.context import build_context


class HostValidationMiddleware(MiddlewareMixin):
    # Verify that the host that is currently requesting the site is actually
    # supposed to be here, then attach the relevant configs for this request
    # to the object.
    def process_request(self, request):
        host = request.get_host()
        if host_data := load_site_config(host):
            request.context = host_data
            request.host = (
                host
                if host not in settings.DEFAULT_HOSTS
                else settings.DEFAULT_HOST_KEY
            )
        else:
            raise DisallowedHost(f"Detected host: {host}")


class ContextUpdateMiddleware(MiddlewareMixin):
    # this has to take place later in the request cycle, so it's separated into
    # its own middleware.
    def process_request(self, request):
        if not hasattr(request, "context"):
            return
        else:
            request.context.update(build_context(request=request))

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

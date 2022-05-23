from django.conf import settings
from django.core.exceptions import DisallowedHost
from django.utils.deprecation import MiddlewareMixin

from alexandria.distributed.configs import load_site_config, get_site_host_key
from alexandria.utils.context import build_context


class HostValidationMiddleware(MiddlewareMixin):
    # Verify that the host that is currently requesting the site is actually
    # supposed to be here, then attach the relevant configs for this request
    # to the object.
    def process_request(self, request):
        host = request.get_host()
        host_key = get_site_host_key(host)
        if host_data := load_site_config(host_key):
            request.context = host_data
            request.host = (
                host_key
                if host_key not in settings.DEFAULT_HOSTS
                else settings.DEFAULT_HOST_KEY
            )
        else:
            raise DisallowedHost(f"Invalid host: {host}, key {host_key}")


class ContextUpdateMiddleware(MiddlewareMixin):
    # this has to take place later in the request cycle, so it's separated into
    # its own middleware.
    def process_request(self, request):
        if not hasattr(request, "context"):
            return
        else:
            request.context.update(build_context(request=request))

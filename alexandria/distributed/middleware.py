from django.conf import settings
from django.core.exceptions import DisallowedHost
from django.utils.deprecation import MiddlewareMixin

from alexandria.distributed.configs import load_site_config
from alexandria.utils.context import build_context


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
            raise DisallowedHost(f"Invalid host: {host}")


class ContextUpdateMiddleware(MiddlewareMixin):
    # this has to take place later in the request cycle, so it's separated into
    # its own middleware.
    def process_request(self, request):
        if not hasattr(request, "context"):
            return
        else:
            request.context.update(build_context(request=request))

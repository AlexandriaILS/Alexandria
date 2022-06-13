from django.conf import settings
from django.core.exceptions import DisallowedHost
from django.utils.deprecation import MiddlewareMixin

from alexandria.distributed.configs import load_site_config, get_site_host_key
from alexandria.distributed.models import Domain, SettingsContainer
from alexandria.utils.context import build_context


class HostValidationMiddleware(MiddlewareMixin):
    # Verify that the host that is currently requesting the site is actually
    # supposed to be here, then attach the relevant configs for this request
    # to the object.
    def process_request(self, request):
        host = request.get_host()
        host_key = get_site_host_key(host)
        if known_host := Domain.objects.filter(name=host_key).first():
            request.settings = SettingsContainer(host=known_host)
            request.context = {}
            request.host = (
                known_host
                if host_key not in settings.DEFAULT_HOSTS
                else Domain.get_default()
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

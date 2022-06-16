from django.contrib import admin

from alexandria.distributed.models import Domain, Setting

admin.site.register(Domain)
admin.site.register(Setting)

"""alexandria URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin.views.decorators import staff_member_required
from decorator_include import decorator_include

from alexandria.catalog.urls import urlpatterns as catalog_urls
from alexandria.records.urls import urlpatterns as records_urls
from alexandria.users.urls import urlpatterns as user_urls

# handler400 = 'alexandria.errors.bad_request'
# handler403 = 'alexandria.errors.permission_denied'
# handler404 = 'alexandria.errors.not_found'
handler500 = "alexandria.errors.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("staff/", decorator_include(staff_member_required, "alexandria.users.urls")),
    path('__debug__/', include('debug_toolbar.urls')),
]

urlpatterns += catalog_urls
urlpatterns += records_urls

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path, include
from staff.views import catalog
from staff.views import general
from staff.views import permissions
from staff.printing.urls import urlpatterns as printing_urls

urlpatterns = [
    path("", general.index, name="staff_index"),
    path("search/", general.staff_search, name="staff_search"),
    path("printing/", include(printing_urls)),
    path("edit/<int:item_id>/", catalog.ItemEdit.as_view(), name="item_edit"),
    path("add_from_loc/", catalog.add_from_loc, name="add_from_loc"),
    path(
        "add_marc_from_loc/",
        catalog.import_marc_record_from_loc,
        name="add_marc_from_loc",
    ),
    path("staff_management/", general.staff_management, name="staff_management"),
    path("patron_management/", general.patron_management, name="patron_management"),
    path(
        "staff_edit/<int:user_id>/",
        general.EditStaffUser.as_view(),
        name="edit_staff_user",
    ),
    # path(
    #     "patron_edit/<int:user_id>/",
    #     general.EditPatronUser.as_view(),
    #     name="edit_staff_user",
    # ),
    path(
        "permissions/",
        permissions.PermissionsView.as_view(),
        name="modify_staff_permissions",
    ),
]

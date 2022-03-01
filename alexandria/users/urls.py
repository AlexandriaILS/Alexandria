from django.urls import path, include
from alexandria.records.views import catalog
from alexandria.users.views import general, patron_management, staff_management
from alexandria.catalog.printing.urls import urlpatterns as printing_urls

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
    path(
        "staff_management/", staff_management.staff_management, name="staff_management"
    ),
    path(
        "patron_management/",
        patron_management.patron_management,
        name="patron_management",
    ),
    path(
        "staff_edit/<str:user_id>/",
        staff_management.EditStaffUser.as_view(),
        name="edit_staff_user",
    ),
    path("patron_create/", patron_management.create_patron, name="create_patron"),
    path(
        "patron_edit/<str:user_id>/",
        patron_management.EditPatronUser.as_view(),
        name="edit_patron",
    ),
    path(
        "user_view/<str:user_id>/",
        patron_management.view_patron_account,
        name="view_user",
    ),
    path(
        "act_as_user/<str:user_id>/", patron_management.act_as_user, name="act_as_user"
    ),
    path(
        "end_act_as_user/", patron_management.end_act_as_user, name="end_act_as_user"
    ),
    # path(
    #     "patron_edit/<int:user_id>/",
    #     general.EditPatronUser.as_view(),
    #     name="edit_staff_user",
    # ),
]

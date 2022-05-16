from django.urls import include, path

from alexandria.catalog.printing.urls import urlpatterns as printing_urls
from alexandria.records.views import catalog, checkin_checkout
from alexandria.users.views import general, patron_management, staff_management

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
        "account_type/",
        staff_management.account_type_management,
        name="account_type_management",
    ),
    path(
        "account_type/<str:account_type_id>/",
        staff_management.EditAccountType.as_view(),
        name="edit_account_type",
    ),
    path(
        "act_as_user/<str:user_id>/", patron_management.act_as_user, name="act_as_user"
    ),
    path("end_act_as_user/", patron_management.end_act_as_user, name="end_act_as_user"),
    path("check_in/", checkin_checkout.check_in, name="check_in"),
    path("check_out/", checkin_checkout.check_out, name="check_out"),
    path("check_out_htmx/", checkin_checkout.check_out_htmx, name="check_out_htmx"),
    path(
        "check_out_additional_options_htmx/",
        checkin_checkout.check_out_additional_options_htmx,
        name="check_out_additional_options_htmx",
    ),
    path(
        "check_out_set_target_htmx/",
        checkin_checkout.check_out_set_target_htmx,
        name="check_out_set_target_htmx",
    ),
    path(
        "check_out_item_htmx/",
        checkin_checkout.check_out_item_htmx,
        name="check_out_item_htmx",
    ),
    path(
        "check_out_session_cancel_htmx/",
        checkin_checkout.check_out_session_cancel_htmx,
        name="check_out_session_cancel_htmx",
    ),
    path(
        "check_out_session_finish_htmx/",
        checkin_checkout.check_out_session_finish_htmx,
        name="check_out_session_finish_htmx",
    ),
    # path(
    #     "patron_edit/<int:user_id>/",
    #     general.EditPatronUser.as_view(),
    #     name="edit_staff_user",
    # ),
]

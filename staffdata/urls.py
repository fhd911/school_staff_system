from django.urls import path
from . import views

app_name = "staffdata"

urlpatterns = [
    # =========================
    # لوحة المشرف والسجلات
    # =========================
    path("", views.dashboard_view, name="dashboard"),
    path("records/", views.records_list_view, name="records_list"),

    path("principals/add/", views.principal_create_view, name="principal_add"),
    path(
        "principals/<int:pk>/request-correction/",
        views.principal_correction_request_view,
        name="principal_request_correction",
    ),

    path("vice/add/", views.vice_create_view, name="vice_add"),
    path(
        "vice/<int:pk>/request-correction/",
        views.vice_correction_request_view,
        name="vice_request_correction",
    ),

    path(
        "corrections/my/",
        views.my_correction_requests_view,
        name="my_correction_requests",
    ),

    # =========================
    # الإدارة العامة
    # =========================
    path("management/overview/", views.admin_overview_view, name="admin_overview"),

    # استعراض السجلات
    path(
        "management/principals/",
        views.admin_principals_list_view,
        name="admin_principals_list",
    ),
    path(
        "management/vices/",
        views.admin_vices_list_view,
        name="admin_vices_list",
    ),

    # استعراض المشرفين ومدخلاتهم
    path(
        "management/supervisors/",
        views.admin_supervisors_list_view,
        name="admin_supervisors_list",
    ),
    path(
        "management/supervisors/import/",
        views.admin_import_supervisors_view,
        name="admin_import_supervisors",
    ),
    path(
        "management/supervisors/template/",
        views.admin_download_supervisors_template_view,
        name="admin_download_supervisors_template",
    ),
    path(
        "management/supervisors/<int:supervisor_id>/",
        views.admin_supervisor_detail_view,
        name="admin_supervisor_detail",
    ),
    path(
        "management/supervisors/<int:supervisor_id>/edit/",
        views.admin_supervisor_update_view,
        name="admin_supervisor_update",
    ),
    path(
        "management/supervisors/<int:supervisor_id>/reset-account/",
        views.admin_reset_supervisor_account_view,
        name="admin_reset_supervisor_account",
    ),

    # طلبات التصحيح
    path(
        "management/corrections/",
        views.admin_correction_requests_view,
        name="admin_correction_requests",
    ),
    path(
        "management/corrections/<int:pk>/review/",
        views.admin_correction_request_review_view,
        name="admin_correction_request_review",
    ),

    # التصدير
    path(
        "management/export/principals/",
        views.admin_export_principals_csv,
        name="admin_export_principals_csv",
    ),
    path(
        "management/export/vice/",
        views.admin_export_vice_csv,
        name="admin_export_vice_csv",
    ),
    path(
        "management/export/performance-zip/",
        views.admin_download_performance_zip,
        name="admin_download_performance_zip",
    ),
]
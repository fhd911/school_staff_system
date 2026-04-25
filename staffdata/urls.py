from django.urls import path
from . import views

app_name = "staffdata"

urlpatterns = [
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

    path("corrections/my/", views.my_correction_requests_view, name="my_correction_requests"),

    path("management/overview/", views.admin_overview_view, name="admin_overview"),

    path(
        "management/data-quality/duplicates/",
        views.admin_duplicates_view,
        name="admin_duplicates",
    ),
    path(
        "management/data-quality/duplicates/<str:record_type>/<int:pk>/edit/",
        views.admin_duplicate_edit_record_view,
        name="admin_duplicate_edit_record",
    ),

    path("management/backup/", views.admin_backup_center_view, name="admin_backup_center"),
    path("management/backup/excel/", views.admin_backup_excel_view, name="admin_backup_excel"),
    path("management/backup/json/", views.admin_backup_json_view, name="admin_backup_json"),
    path("management/backup/media/", views.admin_backup_media_zip_view, name="admin_backup_media_zip"),
    path("management/backup/zip/", views.admin_backup_zip_view, name="admin_backup_zip"),
    path(
        "management/data-quality/duplicates/<str:record_type>/<int:pk>/deactivate/",
        views.admin_duplicate_deactivate_record_view,
        name="admin_duplicate_deactivate_record",
    ),

    path("management/entry-window/", views.admin_entry_window_settings_view, name="admin_entry_window_settings"),
    path("management/entry-window/toggle/", views.admin_entry_window_toggle_view, name="admin_entry_window_toggle"),

    path("management/principals/", views.admin_principals_list_view, name="admin_principals_list"),
    path("management/vices/", views.admin_vices_list_view, name="admin_vices_list"),

    path("management/supervisors/", views.admin_supervisors_list_view, name="admin_supervisors_list"),
    path("management/supervisors/import/", views.admin_import_supervisors_view, name="admin_import_supervisors"),
    path("management/supervisors/template/", views.admin_download_supervisors_template_view, name="admin_download_supervisors_template"),
    path("management/supervisors/<int:supervisor_id>/", views.admin_supervisor_detail_view, name="admin_supervisor_detail"),
    path("management/supervisors/<int:supervisor_id>/edit/", views.admin_supervisor_update_view, name="admin_supervisor_update"),
    path("management/supervisors/<int:supervisor_id>/reset-account/", views.admin_reset_supervisor_account_view, name="admin_reset_supervisor_account"),

    path("management/corrections/", views.admin_correction_requests_view, name="admin_correction_requests"),
    path("management/corrections/<int:pk>/review/", views.admin_correction_request_review_view, name="admin_correction_request_review"),


    path("management/export/final/", views.admin_final_export_gate_view, name="admin_final_export_gate"),
    path(
        "management/export/final/download/<str:export_type>/",
        views.admin_final_export_download_view,
        name="admin_final_export_download",
    ),
    path("management/export/supervisors/", views.admin_export_supervisors_xlsx, name="admin_export_supervisors_xlsx"),
    path("management/export/principals/", views.admin_export_principals_csv, name="admin_export_principals_csv"),
    path("management/export/vice/", views.admin_export_vice_csv, name="admin_export_vice_csv"),

    path("management/performance-download/", views.admin_download_performance_center_view, name="admin_download_performance_center"),
    path("management/export/performance-zip/", views.admin_download_performance_zip, name="admin_download_performance_zip"),
]

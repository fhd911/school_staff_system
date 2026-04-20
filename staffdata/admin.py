from django.contrib import admin

from .models import (
    AccountResetRequest,
    CorrectionRequest,
    DataEntryWindow,
    PrincipalRecord,
    VicePrincipalRecord,
)


@admin.register(PrincipalRecord)
class PrincipalRecordAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "national_id",
        "school_name",
        "sector",
        "stage",
        "school_gender",
        "role",
        "supervisor",
        "is_active",
        "created_at",
    )
    search_fields = (
        "full_name",
        "national_id",
        "mobile",
        "school_name",
        "sector",
        "supervisor__full_name",
        "supervisor__national_id",
    )
    list_filter = (
        "stage",
        "school_gender",
        "role",
        "is_active",
        "sector",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("supervisor",)
    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        ("بيانات المشرف", {
            "fields": ("supervisor",),
        }),
        ("بيانات السجل", {
            "fields": (
                "full_name",
                "national_id",
                "mobile",
                "school_name",
                "sector",
                "stage",
                "school_gender",
                "role",
                "performance_file",
                "notes",
                "is_active",
            ),
        }),
        ("بيانات النظام", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(VicePrincipalRecord)
class VicePrincipalRecordAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "national_id",
        "school_name",
        "sector",
        "stage",
        "school_gender",
        "role",
        "supervisor",
        "is_active",
        "created_at",
    )
    search_fields = (
        "full_name",
        "national_id",
        "mobile",
        "school_name",
        "sector",
        "supervisor__full_name",
        "supervisor__national_id",
    )
    list_filter = (
        "stage",
        "school_gender",
        "role",
        "is_active",
        "sector",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("supervisor",)
    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        ("بيانات المشرف", {
            "fields": ("supervisor",),
        }),
        ("بيانات السجل", {
            "fields": (
                "full_name",
                "national_id",
                "mobile",
                "school_name",
                "sector",
                "stage",
                "school_gender",
                "role",
                "notes",
                "is_active",
            ),
        }),
        ("بيانات النظام", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(CorrectionRequest)
class CorrectionRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "target_type",
        "supervisor",
        "requested_full_name",
        "status",
        "reviewed_by",
        "created_at",
    )
    search_fields = (
        "requested_full_name",
        "requested_national_id",
        "requested_mobile",
        "requested_school_name",
        "requested_sector",
        "supervisor__full_name",
        "supervisor__national_id",
    )
    list_filter = (
        "target_type",
        "status",
        "requested_stage",
        "requested_school_gender",
        "created_at",
        "reviewed_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "reviewed_at",
    )
    autocomplete_fields = (
        "supervisor",
        "principal_record",
        "vice_record",
        "reviewed_by",
    )
    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        ("الارتباط", {
            "fields": (
                "supervisor",
                "target_type",
                "principal_record",
                "vice_record",
            ),
        }),
        ("سبب الطلب", {
            "fields": ("reason",),
        }),
        ("البيانات المقترحة", {
            "fields": (
                "requested_full_name",
                "requested_national_id",
                "requested_mobile",
                "requested_school_name",
                "requested_sector",
                "requested_stage",
                "requested_school_gender",
                "requested_role",
                "requested_notes",
                "requested_performance_file",
            ),
        }),
        ("المعالجة الإدارية", {
            "fields": (
                "status",
                "admin_note",
                "reviewed_by",
                "reviewed_at",
            ),
        }),
        ("بيانات النظام", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(AccountResetRequest)
class AccountResetRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "supervisor",
        "status",
        "processed_by",
        "processed_at",
        "created_at",
    )
    search_fields = (
        "supervisor__full_name",
        "supervisor__national_id",
        "notes",
    )
    list_filter = (
        "status",
        "created_at",
        "processed_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    autocomplete_fields = (
        "supervisor",
        "processed_by",
    )
    list_per_page = 30
    date_hierarchy = "created_at"

    fieldsets = (
        ("الطلب", {
            "fields": (
                "supervisor",
                "status",
                "notes",
            ),
        }),
        ("المعالجة", {
            "fields": (
                "processed_by",
                "processed_at",
            ),
        }),
        ("بيانات النظام", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(DataEntryWindow)
class DataEntryWindowAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "starts_at",
        "ends_at",
        "is_active",
        "allow_add",
        "allow_edit",
        "allow_delete",
        "status_label",
        "is_open_now",
    )
    search_fields = ("title", "notes")
    list_filter = (
        "is_active",
        "allow_add",
        "allow_edit",
        "allow_delete",
        "starts_at",
        "ends_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "status_label",
        "is_open_now",
        "remaining_days",
        "remaining_hours",
        "remaining_seconds",
    )
    list_per_page = 30
    date_hierarchy = "starts_at"

    fieldsets = (
        ("بيانات الفترة", {
            "fields": (
                "title",
                "starts_at",
                "ends_at",
                "is_active",
            ),
        }),
        ("صلاحيات الفترة", {
            "fields": (
                "allow_add",
                "allow_edit",
                "allow_delete",
            ),
        }),
        ("الحالة الحالية", {
            "fields": (
                "status_label",
                "is_open_now",
                "remaining_days",
                "remaining_hours",
                "remaining_seconds",
            ),
        }),
        ("ملاحظات", {
            "fields": ("notes",),
        }),
        ("بيانات النظام", {
            "fields": ("created_at", "updated_at"),
        }),
    )
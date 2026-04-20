from django.contrib import admin

from .models import Supervisor


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "national_id",
        "mobile",
        "email",
        "is_active",
        "can_add_records",
        "can_edit_records",
        "can_delete_records",
        "is_activated",
        "last_login_at",
        "created_at",
    )
    search_fields = (
        "full_name",
        "national_id",
        "mobile",
        "email",
    )
    list_filter = (
        "is_active",
        "is_activated",
        "can_add_records",
        "can_edit_records",
        "can_delete_records",
        "created_at",
        "last_login_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "password_set_at",
        "last_login_at",
    )
    list_per_page = 30
    ordering = ("full_name",)

    fieldsets = (
        ("بيانات المشرف", {
            "fields": (
                "full_name",
                "national_id",
                "mobile",
                "email",
                "is_active",
            ),
        }),
        ("صلاحيات السجلات", {
            "fields": (
                "can_add_records",
                "can_edit_records",
                "can_delete_records",
            ),
        }),
        ("الحساب والتفعيل", {
            "fields": (
                "is_activated",
                "password",
                "password_set_at",
                "last_login_at",
            ),
        }),
        ("بيانات النظام", {
            "fields": (
                "created_at",
                "updated_at",
            ),
        }),
    )
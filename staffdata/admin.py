from django.contrib import admin

from .models import PrincipalRecord, VicePrincipalRecord


@admin.register(PrincipalRecord)
class PrincipalRecordAdmin(admin.ModelAdmin):
    list_display = ("full_name", "national_id", "school_name", "sector", "stage", "role", "supervisor", "created_at")
    search_fields = ("full_name", "national_id", "school_name", "sector")
    list_filter = ("stage", "school_gender", "role", "is_active")


@admin.register(VicePrincipalRecord)
class VicePrincipalRecordAdmin(admin.ModelAdmin):
    list_display = ("full_name", "national_id", "school_name", "sector", "stage", "role", "supervisor", "created_at")
    search_fields = ("full_name", "national_id", "school_name", "sector")
    list_filter = ("stage", "school_gender", "role", "is_active")
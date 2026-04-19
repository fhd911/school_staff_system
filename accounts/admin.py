from django.contrib import admin

from .models import Supervisor


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "national_id", "mobile", "email", "is_active", "created_at")
    search_fields = ("full_name", "national_id", "mobile", "email")
    list_filter = ("is_active",)
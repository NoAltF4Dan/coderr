from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Zusätzliche Felder", {
            "fields": ("type", "location", "tel", "description", "working_hours"),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Zusätzliche Felder", {
            "fields": ("type",),
        }),
    )
    list_display = ("id", "username", "email", "type", "is_active", "is_staff")
    list_display_links = ("id", "username")
    search_fields = ("username", "email")

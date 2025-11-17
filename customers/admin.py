from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_email", "created_at")
    search_fields = ("id", "name", "external_ref", "contact_email", "contact_person")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")

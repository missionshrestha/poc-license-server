from django.contrib import admin

from .models import License, LicenseTemplate


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = (
        "license_id",
        "customer",
        "product",
        "edition",
        "license_type",
        "valid_from",
        "valid_until",
        "status",
        "issued_at",
    )
    search_fields = (
        "license_id",
        "customer__name",
        "customer__id",
        "product__code",
        "edition__code",
    )
    list_filter = ("license_type", "status", "product", "edition")
    readonly_fields = ("payload", "signature", "created_at", "updated_at")


@admin.register(LicenseTemplate)
class LicenseTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "product",
        "edition",
        "license_type",
        "duration_days",
        "created_at",
    )
    search_fields = ("id", "name", "product__code", "edition__code")
    list_filter = ("product", "edition", "license_type")
    readonly_fields = ("created_at", "updated_at")

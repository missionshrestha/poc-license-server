from django.contrib import admin

from .models import KeyMetadata


@admin.register(KeyMetadata)
class KeyMetadataAdmin(admin.ModelAdmin):
    list_display = ("key_id", "alg", "is_active", "created_at", "retired_at")
    search_fields = ("key_id", "description")
    list_filter = ("alg", "is_active")
    readonly_fields = ("created_at",)

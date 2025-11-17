from django.contrib import admin

from .models import Product, Edition, FeatureDefinition


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active", "created_at")
    search_fields = ("id", "code", "name")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "code", "name", "is_active", "created_at")
    search_fields = ("id", "code", "name", "product__code")
    list_filter = ("product", "is_active")
    readonly_fields = ("created_at", "updated_at")


@admin.register(FeatureDefinition)
class FeatureDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "key", "feature_type", "is_deprecated", "created_at")
    search_fields = ("id", "product__code", "key", "name")
    list_filter = ("product", "feature_type", "is_deprecated")
    readonly_fields = ("created_at", "updated_at")

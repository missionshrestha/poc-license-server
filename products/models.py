from django.db import models


class Product(models.Model):
    """
    Licensed product, e.g. 'data-pipeline-app'.
    """

    id = models.CharField(
        max_length=64,
        primary_key=True,
        help_text="Internal product identifier (e.g., 'prod-data-pipeline').",
    )
    code = models.CharField(
        max_length=64,
        unique=True,
        help_text="Short code used in license payload (e.g., 'data-pipeline-app').",
    )
    name = models.CharField(
        max_length=255,
        help_text="Human-readable product name.",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of the product.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this product is currently sold/licensed.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:  
        return f"{self.code} - {self.name}"


class Edition(models.Model):
    """
    Edition/SKU of a product, e.g. 'community', 'standard', 'enterprise'.
    """

    id = models.CharField(
        max_length=64,
        primary_key=True,
        help_text="Internal edition identifier (e.g., 'ed-standard').",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="editions",
    )
    code = models.CharField(
        max_length=64,
        help_text="Edition code as appears in license payload (e.g., 'standard').",
    )
    name = models.CharField(
        max_length=255,
        help_text="Human-readable edition name.",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of this edition.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this edition is currently offered.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "code")
        ordering = ["product__code", "code"]

    def __str__(self) -> str:  
        return f"{self.product.code}:{self.code}"


class FeatureDefinition(models.Model):
    """
    Optional catalog of features to avoid typos in feature flags.
    Not strictly required for POC but useful for consistency.
    """

    FEATURE_TYPE_CHOICES = [
        ("boolean", "Boolean"),
        ("integer_limit", "Integer limit"),
        ("string", "String"),
        ("json", "JSON"),
    ]

    id = models.CharField(
        max_length=64,
        primary_key=True,
        help_text="Internal feature identifier (e.g., 'feat-adv-export').",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="features",
    )
    key = models.CharField(
        max_length=128,
        help_text="Feature key used in license payload (e.g., 'advanced_export').",
    )
    name = models.CharField(
        max_length=255,
        help_text="Human-readable feature name.",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of what this feature enables.",
    )
    feature_type = models.CharField(
        max_length=32,
        choices=FEATURE_TYPE_CHOICES,
        default="boolean",
    )
    default_value = models.JSONField(
        blank=True,
        null=True,
        help_text="Optional default value if not explicitly set in license.",
    )
    is_deprecated = models.BooleanField(
        default=False,
        help_text="Mark true when this feature is no longer used.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "key")
        ordering = ["product__code", "key"]

    def __str__(self) -> str:  
        return f"{self.product.code}:{self.key}"

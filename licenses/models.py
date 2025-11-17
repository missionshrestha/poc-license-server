from django.conf import settings
from django.db import models

from customers.models import Customer
from products.models import Product, Edition


class License(models.Model):
    """
    An issued license instance (immutable snapshot of what was signed).
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("revoked", "Revoked"),
        ("superseded", "Superseded"),
        ("expired", "Expired (record only)"),
    ]

    id = models.CharField(
        max_length=64,
        primary_key=True,
        help_text="Internal DB identifier for the license record.",
    )
    license_id = models.CharField(
        max_length=128,
        unique=True,
        help_text="License identifier as appears in payload (typically a UUID).",
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="licenses",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="licenses",
    )
    edition = models.ForeignKey(
        Edition,
        on_delete=models.PROTECT,
        related_name="licenses",
    )

    license_type = models.CharField(
        max_length=32,
        help_text="trial | subscription | perpetual",
    )

    valid_from = models.DateTimeField(
        help_text="UTC datetime from which this license is considered valid.",
    )
    valid_until = models.DateTimeField(
        help_text="UTC datetime after which this license is considered expired.",
    )

    # Meta from license meta section
    meta_version = models.IntegerField(
        default=1,
        help_text="Version of the license meta format.",
    )
    meta_alg = models.CharField(
        max_length=32,
        default="Ed25519",
        help_text="Signature algorithm used to sign the payload.",
    )
    meta_key_id = models.CharField(
        max_length=64,
        help_text="Refers to KeyMetadata.key_id used for signing.",
    )

    # The exact payload object that was signed, stored as JSON.
    payload = models.JSONField(
        help_text="Canonical payload object used for signing.",
    )

    # The signature over the canonical payload, base64-url encoded.
    signature = models.TextField(
        help_text="Base64-url encoded signature over the canonical payload.",
    )

    issued_at = models.DateTimeField(
        help_text="UTC timestamp from payload.issuer.issued_at.",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issued_licenses",
        help_text="Admin/operator user who issued this license.",
    )

    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Admin-visible logical status; offline clients ignore this.",
    )

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about revocation, contract terms, etc.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  
        return f"{self.license_id} ({self.customer.name} / {self.product.code}:{self.edition.code})"


class LicenseTemplate(models.Model):
    """
    Optional template for issuing licenses with consistent defaults.
    """

    LICENSE_TYPE_CHOICES = [
        ("trial", "Trial"),
        ("subscription", "Subscription"),
        ("perpetual", "Perpetual"),
    ]

    id = models.CharField(
        max_length=64,
        primary_key=True,
        help_text="Internal template identifier (e.g., 'tmpl-ent-annual').",
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Human-readable template name (e.g., 'Enterprise Annual Default').",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="license_templates",
    )
    edition = models.ForeignKey(
        Edition,
        on_delete=models.PROTECT,
        related_name="license_templates",
    )
    license_type = models.CharField(
        max_length=32,
        choices=LICENSE_TYPE_CHOICES,
        help_text="Default license type for this template.",
    )

    duration_days = models.IntegerField(
        blank=True,
        null=True,
        help_text="Default duration in days (e.g., 14 for trials). Optional.",
    )

    default_features = models.JSONField(
        blank=True,
        null=True,
        help_text="Default features object to merge into payload.features.",
    )
    default_usage_limits = models.JSONField(
        blank=True,
        null=True,
        help_text="Default usage_limits object to merge into payload.usage_limits.",
    )

    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional notes about when/how to use this template.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product__code", "edition__code", "name"]

    def __str__(self) -> str:  
        return f"{self.name} ({self.product.code}:{self.edition.code})"

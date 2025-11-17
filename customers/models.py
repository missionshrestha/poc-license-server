from django.db import models


class Customer(models.Model):
    """
    Represents a legal/organizational entity that owns licenses.
    """

    id = models.CharField(
        max_length=64,
        primary_key=True,
        help_text="Internal customer identifier (e.g., 'cust-1001').",
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Human-readable name of the customer.",
    )
    external_ref = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional CRM / billing reference (e.g., Stripe or HubSpot ID).",
    )
    contact_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Primary contact email for licensing notifications.",
    )
    contact_person = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Primary contact person.",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Free-form notes about contract terms, etc.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  
        return f"{self.name} ({self.id})"

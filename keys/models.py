from django.db import models


class KeyMetadata(models.Model):
    """
    Metadata for each signing key pair.

    NOTE: This does NOT store the private key material, only logical info
    such as key_id and algorithm. The actual private key lives on disk or KMS.
    """

    id = models.CharField(
        max_length=64,
        primary_key=True,
        help_text="Internal key metadata ID (e.g., 'key-main-v1').",
    )
    key_id = models.CharField(
        max_length=64,
        unique=True,
        help_text="Key identifier used in license meta.key_id (e.g., 'main-v1').",
    )
    alg = models.CharField(
        max_length=32,
        help_text="Signature algorithm (e.g., 'Ed25519').",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of where/how this key is used.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this key should be used for issuing new licenses.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    retired_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when key stopped being used for new licenses.",
    )

    class Meta:
        ordering = ["key_id"]

    def __str__(self) -> str:  
        return f"{self.key_id} ({self.alg})"

# licenses/serializers.py

from rest_framework import serializers


class LicenseIssueRequestSerializer(serializers.Serializer):
    """
    Request schema for issuing a new license.

    """

    LICENSE_TYPE_CHOICES = ("trial", "subscription", "perpetual")

    customer_id = serializers.CharField(
        help_text="Primary key of Customer (e.g., 'cust-1001')."
    )
    product_id = serializers.CharField(
        help_text="Primary key of Product (e.g., 'prod-data-pipeline')."
    )
    edition_id = serializers.CharField(
        help_text="Primary key of Edition (e.g., 'ed-enterprise')."
    )

    license_type = serializers.ChoiceField(
        choices=LICENSE_TYPE_CHOICES,
        help_text="License type: trial | subscription | perpetual",
    )

    valid_from = serializers.DateTimeField(
        help_text="UTC datetime when the license becomes valid."
    )
    valid_until = serializers.DateTimeField(
        help_text="UTC datetime when the license stops being valid.",
    )

    features = serializers.JSONField(
        required=False,
        help_text="Optional feature flags object (e.g., { 'advanced_export': true }).",
    )
    usage_limits = serializers.JSONField(
        required=False,
        help_text="Optional usage limit object (e.g., { 'max_runs_per_day': 50 }).",
    )
    deployment = serializers.JSONField(
        required=False,
        help_text="Optional deployment metadata for operator reference.",
    )

    note = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional internal note stored on the License record.",
    )

    def validate(self, attrs):
        """
        Cross-field validation: ensure valid_from <= valid_until.
        """
        valid_from = attrs["valid_from"]
        valid_until = attrs["valid_until"]

        if valid_from >= valid_until:
            raise serializers.ValidationError(
                "valid_from must be strictly earlier than valid_until."
            )

        return attrs

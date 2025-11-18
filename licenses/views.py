# licenses/views.py

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import License
from .serializers import LicenseIssueRequestSerializer
from .services.issuance import (
    issue_license_from_validated_data,
    LicenseIssuanceError,
)


class IssueLicenseView(APIView):
    """
    POST /api/licenses/issue/

    Issues a new license and returns:
    {
      "license": { meta, payload, signature },
      "license_id": "...",
      "db_id": "..."
    }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LicenseIssueRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            signed_obj, license_record = issue_license_from_validated_data(
                serializer.validated_data,
                issued_by=request.user,
            )
        except LicenseIssuanceError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = {
            "license": signed_obj,
            "license_id": license_record.license_id,
            "db_id": license_record.id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class DownloadLicenseView(APIView):
    """
    GET /api/licenses/{license_id}/download/

    Returns the license JSON to be saved as a .license file:
    {
      "meta": { ... },
      "payload": { ... },
      "signature": "..."
    }
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, license_id: str, *args, **kwargs):
        license_record = get_object_or_404(License, license_id=license_id)

        license_json = {
            "meta": {
                "version": license_record.meta_version,
                "alg": license_record.meta_alg,
                "key_id": license_record.meta_key_id,
            },
            "payload": license_record.payload,
            "signature": license_record.signature,
        }

        return Response(license_json, status=status.HTTP_200_OK)
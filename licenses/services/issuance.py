# licenses/services/issuance.py

import uuid
from typing import Any, Dict, Tuple
from datetime import datetime, timezone

from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser

from licenses.models import License
from customers.models import Customer
from products.models import Product, Edition
from licenses.services.signing import sign_license_payload


class LicenseIssuanceError(Exception):
    """
    Domain-level error for license issuance problems (e.g., invalid FK relationships).
    """
    pass


def _build_license_payload(
    *,
    license_id: str,
    customer: Customer,
    product: Product,
    edition: Edition,
    license_type: str,
    valid_from: datetime,
    valid_until: datetime,
    features: Dict[str, Any] | None,
    usage_limits: Dict[str, Any] | None,
    deployment: Dict[str, Any] | None,
    issued_by: AbstractBaseUser,
) -> Dict[str, Any]:
    """
    Construct the license payload object that will be signed.
    """
    now = datetime.now(timezone.utc)

    payload = {
        "license_id": license_id,
        "customer": {
            "id": customer.id,
            "name": customer.name,
        },
        "product": {
            "id": product.id,
            "code": product.code,
            "name": product.name,
        },
        "edition": {
            "id": edition.id,
            "code": edition.code,
            "name": edition.name,
        },
        "license_type": license_type,
        "validity": {
            "valid_from": valid_from.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "valid_until": valid_until.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        "features": features or {},
        "usage_limits": usage_limits or {},
        "deployment": deployment or {},
        "issuer": {
            "issued_at": now.isoformat().replace("+00:00", "Z"),
            "issuer_id": str(issued_by.pk),
            "issuer_username": issued_by.get_username(),
        },
    }

    return payload


@transaction.atomic
def issue_license_from_validated_data(
    data: Dict[str, Any],
    *,
    issued_by: AbstractBaseUser,
) -> Tuple[Dict[str, Any], License]:
    """
    Main orchestration function for issuing a license.

    Steps:
    - Resolve Customer, Product, Edition from IDs
    - Validate Edition belongs to Product
    - Generate license_id (UUID)
    - Build payload
    - Sign payload (meta + signature)
    - Persist License row
    - Return (full_license_object, license_record)
    """
    customer_id = data["customer_id"]
    product_id = data["product_id"]
    edition_id = data["edition_id"]

    license_type = data["license_type"]
    valid_from: datetime = data["valid_from"]
    valid_until: datetime = data["valid_until"]
    features = data.get("features") or {}
    usage_limits = data.get("usage_limits") or {}
    deployment = data.get("deployment") or {}
    note = data.get("note", "")

    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist as exc:
        raise LicenseIssuanceError(f"Customer with id '{customer_id}' does not exist.") from exc

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist as exc:
        raise LicenseIssuanceError(f"Product with id '{product_id}' does not exist.") from exc

    try:
        edition = Edition.objects.get(pk=edition_id)
    except Edition.DoesNotExist as exc:
        raise LicenseIssuanceError(f"Edition with id '{edition_id}' does not exist.") from exc

    if edition.product_id != product.id:
        raise LicenseIssuanceError(
            f"Edition '{edition.id}' does not belong to product '{product.id}'."
        )

    # --- Generate external license ID (UUID) ---
    license_id = str(uuid.uuid4())

    # --- Build payload and sign ---
    payload = _build_license_payload(
        license_id=license_id,
        customer=customer,
        product=product,
        edition=edition,
        license_type=license_type,
        valid_from=valid_from,
        valid_until=valid_until,
        features=features,
        usage_limits=usage_limits,
        deployment=deployment,
        issued_by=issued_by,
    )

    signed_obj = sign_license_payload(payload)
    meta = signed_obj["meta"]
    signature = signed_obj["signature"]

    now = datetime.now(timezone.utc)

    license_record = License.objects.create(
        id=license_id,
        license_id=license_id,
        customer=customer,
        product=product,
        edition=edition,
        license_type=license_type,
        valid_from=valid_from,
        valid_until=valid_until,
        meta_version=meta["version"],
        meta_alg=meta["alg"],
        meta_key_id=meta["key_id"],
        payload=payload,
        signature=signature,
        issued_at=now,
        issued_by=issued_by,
        status="active",
        notes=note,
    )

    return signed_obj, license_record

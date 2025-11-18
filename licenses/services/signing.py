
import base64
import json
from typing import Any, Dict, Tuple

from django.conf import settings

from .keys import load_private_signing_key


def _canonical_json_bytes(payload: Dict[str, Any]) -> bytes:
    """
    Serialize a dict to canonical JSON bytes for signing.

    - Sorted keys for deterministic field order
    - No extraneous whitespace
    - UTF-8 encoding
    """
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),  
        ensure_ascii=False,
    ).encode("utf-8")


def _b64url_encode_no_padding(raw: bytes) -> str:
    """
    Base64 URL-safe encoding without padding ('=').
    This is common for token-style signatures.
    """
    encoded = base64.urlsafe_b64encode(raw).decode("ascii")
    return encoded.rstrip("=")



def build_license_meta_and_signature(
    payload: Dict[str, Any],
    key_id: str | None = None,
) -> Tuple[Dict[str, Any], str]:
    """
    Given a payload dict, construct the meta section and compute the signature.

    Returns:
        meta: dict with version, alg, key_id
        signature: base64-url (no padding) encoded Ed25519 signature
    """
    meta = {
        "version": settings.LICENSE_META_VERSION,
        "alg": settings.LICENSE_META_ALG,
        "key_id": key_id or settings.SIGNING_KEY_ID,
    }

    payload_bytes = _canonical_json_bytes(payload)

    private_key = load_private_signing_key()
    raw_sig = private_key.sign(payload_bytes)

    signature_b64 = _b64url_encode_no_padding(raw_sig)
    return meta, signature_b64


def sign_license_payload(
    payload: Dict[str, Any],
    key_id: str | None = None,
) -> Dict[str, Any]:
    """
    High-level helper to produce a full license object
    { meta, payload, signature } from a payload dict.

    This does NOT persist anything to the DB. It's purely crypto.
    """
    meta, signature_b64 = build_license_meta_and_signature(payload, key_id=key_id)

    return {
        "meta": meta,
        "payload": payload,
        "signature": signature_b64,
    }

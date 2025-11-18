# licenses/services/keys.py

import functools
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from django.conf import settings


@functools.lru_cache(maxsize=1)
def load_private_signing_key() -> ed25519.Ed25519PrivateKey:
    """
    Load the Ed25519 private key used for signing license payloads.

    The key is loaded once and cached in memory using lru_cache.
    """
    key_path = Path(settings.PRIVATE_KEY_PATH)

    if not key_path.exists():
        raise FileNotFoundError(
            f"Private signing key not found at {key_path}. "
            "Check PRIVATE_KEY_PATH in .env / settings."
        )

    pem_data = key_path.read_bytes()

    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,
    )

    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise TypeError(
            f"Loaded private key is not an Ed25519 key (got {type(private_key)!r})."
        )

    return private_key

import argparse
import os
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def generate_ed25519_keypair(key_id: str, output_dir: Path) -> None:
    """
    Generate an Ed25519 keypair and write:

    - <output_dir>/<key_id>-private.pem
    - <output_dir>/<key_id>-public.pem
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    private_key_path = output_dir / f"{key_id}-private.pem"
    public_key_path = output_dir / f"{key_id}-public.pem"

    if private_key_path.exists() or public_key_path.exists():
        raise SystemExit(
            f"Refusing to overwrite existing key files:\n"
            f"  {private_key_path}\n"
            f"  {public_key_path}\n"
            f"Move or delete them if you really want to regenerate."
        )
    
    private_key = ed25519.Ed25519PrivateKey.generate()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key = private_key.public_key()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_key_path.write_bytes(private_pem)
    public_key_path.write_bytes(public_pem)

    try:
        os.chmod(private_key_path, 0o600)
    except PermissionError:
        print(f"Warning: could not chmod 600 {private_key_path}")

    print(f"[OK] Private key written to: {private_key_path}")
    print(f"[OK] Public  key written to: {public_key_path}")




def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an Ed25519 signing keypair for the licensing server."
    )
    parser.add_argument(
        "--key-id",
        required=True,
        help=(
            "Logical key ID (e.g., 'main-v1'). "
            "Files will be named <key-id>-private.pem and <key-id>-public.pem"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="keys",
        help="Output directory for key files (default: ./keys)",
    )

    # Parse CLI args
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()

    # Do the actual work
    generate_ed25519_keypair(args.key_id, output_dir)


if __name__ == "__main__":
    main()

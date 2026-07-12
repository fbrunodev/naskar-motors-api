import base64
from pathlib import Path

VAPID_CLAIMS = {"sub": "mailto:admin@naskar-motors.com"}
_KEY_FILE = Path(__file__).parent / ".vapid_private.pem"


def _ensure_keys() -> None:
    if _KEY_FILE.exists():
        return
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PrivateFormat, NoEncryption,
    )
    private_key = ec.generate_private_key(ec.SECP256R1())
    pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())
    _KEY_FILE.write_bytes(pem)
    print(f"[VAPID] Generated new private key at {_KEY_FILE}")


def get_private_key_path() -> str:
    _ensure_keys()
    return str(_KEY_FILE)


def get_public_key_b64() -> str:
    _ensure_keys()
    from cryptography.hazmat.primitives.serialization import (
        load_pem_private_key, Encoding, PublicFormat,
    )
    private_key = load_pem_private_key(_KEY_FILE.read_bytes(), password=None)
    pub_bytes = private_key.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )
    return base64.urlsafe_b64encode(pub_bytes).rstrip(b'=').decode()

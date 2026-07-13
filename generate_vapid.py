"""
Gera um novo par de chaves VAPID no formato DER/PKCS8 (compatível com Apple web.push).

Uso:
    python generate_vapid.py

Cole os valores gerados nas variáveis de ambiente VAPID_PUBLIC_KEY e VAPID_PRIVATE_KEY.
"""
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from py_vapid import Vapid

private_key = ec.generate_private_key(ec.SECP256R1())

# Chave privada: DER/PKCS8, base64 padrão (compatível com Apple e FCM)
priv_der = private_key.private_bytes(
    serialization.Encoding.DER,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
)
priv_b64 = base64.b64encode(priv_der).decode()

# Chave pública: ponto EC não comprimido X9.62, base64url (usado pelo frontend)
pub_bytes = private_key.public_key().public_bytes(
    serialization.Encoding.X962,
    serialization.PublicFormat.UncompressedPoint,
)
pub_b64url = base64.urlsafe_b64encode(pub_bytes).rstrip(b"=").decode()

# Validação round-trip via py_vapid (mesmo caminho que pywebpush usa internamente)
v = Vapid.from_string(priv_b64)
pub_derived = base64.urlsafe_b64encode(
    v.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
).rstrip(b"=").decode()
assert pub_derived == pub_b64url, "Round-trip falhou — chaves inconsistentes"

print("=== Cole estas variáveis no Render ===")
print(f"VAPID_PUBLIC_KEY={pub_b64url}")
print(f"VAPID_PRIVATE_KEY={priv_b64}")

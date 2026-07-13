import os

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
_claims_email = os.getenv("VAPID_CLAIMS_EMAIL", "admin@naskar-motors.com")
VAPID_CLAIMS = {"sub": _claims_email if _claims_email.startswith("mailto:") else f"mailto:{_claims_email}"}

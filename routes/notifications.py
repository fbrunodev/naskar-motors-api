from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
import models
import auth
import vapid_keys
import notifications as notif

router = APIRouter(prefix="/notifications", tags=["notifications"])


class SubscribeRequest(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


@router.get("/vapid-public-key")
def get_vapid_public_key():
    return {"public_key": vapid_keys.VAPID_PUBLIC_KEY}


@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
def subscribe(
    data: SubscribeRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(models.PushSubscription).filter(
        models.PushSubscription.user_id == current_user.id,
        models.PushSubscription.endpoint == data.endpoint,
    ).first()
    if existing:
        existing.p256dh = data.p256dh
        existing.auth = data.auth
    else:
        db.add(models.PushSubscription(
            user_id=current_user.id,
            endpoint=data.endpoint,
            p256dh=data.p256dh,
            auth=data.auth,
        ))
    db.commit()
    return {"status": "subscribed"}


@router.delete("/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db.query(models.PushSubscription).filter(
        models.PushSubscription.user_id == current_user.id
    ).delete()
    db.commit()


@router.post("/test", status_code=status.HTTP_200_OK)
def test_notification(
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    users = db.query(models.User).all()
    for user in users:
        notif.send_push(
            db, user.id,
            "Naskar Motors",
            "Notificações funcionando corretamente!",
        )
    return {"status": "sent", "users": len(users)}


@router.get("/debug-vapid")
def debug_vapid(_: models.User = Depends(auth.require_owner)):
    import base64
    result: dict = {"vapid_public_key_env": vapid_keys.VAPID_PUBLIC_KEY}
    try:
        from py_vapid import Vapid
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        padded = vapid_keys.VAPID_PRIVATE_KEY + "=" * (-len(vapid_keys.VAPID_PRIVATE_KEY) % 4)
        priv_bytes = base64.urlsafe_b64decode(padded)
        from cryptography.hazmat.primitives.asymmetric.ec import derive_private_key, SECP256R1
        priv_key = derive_private_key(int.from_bytes(priv_bytes, "big"), SECP256R1())
        pub_bytes = priv_key.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        derived_pub = base64.urlsafe_b64encode(pub_bytes).rstrip(b"=").decode()
        result["derived_public_key_from_private"] = derived_pub
        result["keys_match"] = derived_pub == vapid_keys.VAPID_PUBLIC_KEY
    except Exception as exc:
        result["error"] = str(exc)
    return result


@router.get("/debug-subscriptions")
def debug_subscriptions(
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    subs = db.query(models.PushSubscription).all()
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "endpoint": s.endpoint,
            "created_at": str(s.created_at) if hasattr(s, "created_at") else "n/a",
        }
        for s in subs
    ]


@router.get("/jobs/check-encalhados")
def run_check_encalhados(_: models.User = Depends(auth.require_owner)):
    from jobs.check_encalhados import check_encalhados
    check_encalhados()
    return {"status": "ok"}

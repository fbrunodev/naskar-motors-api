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
    if not existing:
        sub = models.PushSubscription(
            user_id=current_user.id,
            endpoint=data.endpoint,
            p256dh=data.p256dh,
            auth=data.auth,
        )
        db.add(sub)
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
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    notif.send_push(
        db, current_user.id,
        "Naskar Motors",
        "Notificações funcionando corretamente!",
    )
    return {"status": "sent"}


@router.get("/jobs/check-encalhados")
def run_check_encalhados(_: models.User = Depends(auth.require_owner)):
    from jobs.check_encalhados import check_encalhados
    check_encalhados()
    return {"status": "ok"}

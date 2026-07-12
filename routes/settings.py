from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=schemas.StoreSettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(models.StoreSettings).first()
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store settings not configured",
        )
    return settings


@router.put("/", response_model=schemas.StoreSettingsResponse)
def update_settings(
    settings_data: schemas.StoreSettingsBase,
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    settings = db.query(models.StoreSettings).first()
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store settings not configured",
        )

    for key, value in settings_data.model_dump().items():
        setattr(settings, key, value)

    db.commit()
    db.refresh(settings)
    return settings

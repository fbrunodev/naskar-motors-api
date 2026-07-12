from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
import auth
import cloudinary
import cloudinary.uploader
import os


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/vehicle/{vehicle_id}")
def upload_vehicle_photo(
    vehicle_id: int,
    file: UploadFile = File(...),
    _: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    result = cloudinary.uploader.upload(
        file.file,
        folder="naskar-motors/vehicles",
        transformation=[{"width": 800, "crop": "limit"}],
    )

    vehicle.photos = list(vehicle.photos or []) + [result["secure_url"]]

    db.commit()
    db.refresh(vehicle)
    return {"url": result["secure_url"], "photos": vehicle.photos}


@router.delete("/vehicle/{vehicle_id}/photo")
def delete_vehicle_photo(
    vehicle_id: int,
    photo_url: str,
    _: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    photos = vehicle.photos or []
    if photo_url not in photos:
        raise HTTPException(status_code=404, detail="Photo not found")

    photos.remove(photo_url)
    vehicle.photos = photos

    db.commit()
    return {"message": "Photo deleted", "photos": vehicle.photos}


@router.post("/logo")
def upload_store_logo(
    file: UploadFile = File(...),
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    settings = db.query(models.StoreSettings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Store settings not configured")

    result = cloudinary.uploader.upload(
        file.file,
        folder="naskar-motors/logos",
        public_id="store_logo",
        transformation=[{"width": 400, "crop": "limit"}],
    )

    settings.logo_url = result["secure_url"]
    db.commit()
    return {"url": result["secure_url"]}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models
import schemas
import auth

router = APIRouter(tags=["brands"])


@router.get("/", response_model=List[schemas.BrandResponse])
def list_brands(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Brand)
    if category:
        query = query.filter(models.Brand.category == category)
    return query.order_by(models.Brand.name).all()


@router.get("/{brand_id}/models", response_model=List[schemas.VehicleModelResponse])
def list_models(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return db.query(models.VehicleModel).filter(models.VehicleModel.brand_id == brand_id).order_by(models.VehicleModel.name).all()


@router.post("/", response_model=schemas.BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    data: schemas.BrandCreate,
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    if db.query(models.Brand).filter(models.Brand.name == data.name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Brand already exists")
    brand = models.Brand(**data.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.post("/{brand_id}/models", response_model=schemas.VehicleModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(
    brand_id: int,
    data: schemas.VehicleModelCreate,
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    if not db.query(models.Brand).filter(models.Brand.id == brand_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    vehicle_model = models.VehicleModel(name=data.name, brand_id=brand_id)
    db.add(vehicle_model)
    db.commit()
    db.refresh(vehicle_model)
    return vehicle_model

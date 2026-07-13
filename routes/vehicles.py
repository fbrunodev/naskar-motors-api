from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db
import models
import schemas
import auth
import notifications


class MarkSoldRequest(BaseModel):
    sold_by_id: Optional[int] = None

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=List[schemas.VehicleResponse])
def list_vehicles(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_featured: Optional[bool] = None,
    include_sold: Optional[bool] = False,
    db: Session = Depends(get_db),
):
    query = db.query(models.Vehicle)
    if not include_sold:
        query = query.filter(models.Vehicle.is_sold == False)

    if category:
        query = query.filter(models.Vehicle.category == category)
    if brand:
        query = query.filter(models.Vehicle.brand == brand)
    if min_price is not None:
        query = query.filter(models.Vehicle.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Vehicle.price <= max_price)
    if is_featured is not None:
        query = query.filter(models.Vehicle.is_featured == is_featured)

    return query.all()


@router.get("/{vehicle_id}", response_model=schemas.VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


@router.post("/", response_model=schemas.VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_data: schemas.VehicleCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = models.Vehicle(**vehicle_data.model_dump(), photos=[])
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    if current_user.role != "owner":
        veiculo_nome = f"{vehicle.brand} {vehicle.model} {vehicle.year}"
        background_tasks.add_task(
            notifications.notify_owner_novo_veiculo, current_user.name, veiculo_nome
        )

    return vehicle


@router.put("/{vehicle_id}", response_model=schemas.VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: schemas.VehicleCreate,
    _: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    for key, value in vehicle_data.model_dump().items():
        setattr(vehicle, key, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    _: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()


@router.patch("/{vehicle_id}/available")
def mark_vehicle_available(
    vehicle_id: int,
    _: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    vehicle.is_sold = False
    vehicle.sold_at = None
    vehicle.sold_by = None
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.patch("/{vehicle_id}/sold")
def mark_vehicle_sold(
    vehicle_id: int,
    background_tasks: BackgroundTasks,
    data: MarkSoldRequest = Body(default=MarkSoldRequest()),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    # Owner can attribute the sale to a specific employee via sold_by_id
    if current_user.role == 'owner' and data.sold_by_id:
        seller = db.query(models.User).filter(models.User.id == data.sold_by_id).first()
        if not seller:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendedor não encontrado")
    else:
        seller = current_user

    vehicle.is_sold = True
    vehicle.sold_at = datetime.utcnow()
    vehicle.sold_by = seller.id
    db.commit()
    db.refresh(vehicle)

    veiculo_nome = f"{vehicle.brand} {vehicle.model} {vehicle.year}"
    comissao = float(vehicle.price) * float(vehicle.commission_rate or 2.0) / 100

    # Only notify the seller if they are an employee (not the owner clicking on their own behalf)
    if seller.role == 'employee':
        background_tasks.add_task(
            notifications.notify_vendedor_venda, seller.id, veiculo_nome, comissao
        )

    background_tasks.add_task(
        notifications.notify_owner_venda, seller.name, veiculo_nome, vehicle.price
    )

    meta = seller.monthly_goal or 5
    start_of_month = datetime(datetime.utcnow().year, datetime.utcnow().month, 1)
    vendas_mes = (
        db.query(models.Vehicle)
        .filter(
            models.Vehicle.sold_by == seller.id,
            models.Vehicle.is_sold == True,
            models.Vehicle.sold_at >= start_of_month,
        )
        .count()
    )

    if vendas_mes == meta:
        if seller.role == 'employee':
            background_tasks.add_task(notifications.notify_vendedor_meta_batida, seller.id)
        background_tasks.add_task(notifications.notify_owner_meta_batida, seller.name)
    elif meta >= 2 and vendas_mes == meta // 2:
        if seller.role == 'employee':
            background_tasks.add_task(
                notifications.notify_vendedor_50_porcento, seller.id, vendas_mes, meta
            )

    return {"message": "Vehicle marked as sold"}

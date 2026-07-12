from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
import models
import schemas
import auth
import notifications

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[schemas.UserResponse])
def list_users(
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    return db.query(models.User).filter(models.User.role == "employee").all()


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: schemas.UserCreate,
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use",
        )

    user = models.User(
        name=user_data.name,
        email=user_data.email,
        password_hash=auth.hash_password(user_data.password),
        role="employee",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.role == "employee",
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()


@router.get("/me/stats", response_model=schemas.EmployeeStats)
def get_my_stats(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    all_sold = (
        db.query(models.Vehicle)
        .filter(models.Vehicle.sold_by == current_user.id, models.Vehicle.is_sold == True)
        .all()
    )

    vendidos_mes = [v for v in all_sold if v.sold_at and v.sold_at >= start_of_month]
    faturamento_mes = sum(v.price for v in vendidos_mes)
    comissao_mes = sum(v.price * float(v.commission_rate or 2.0) / 100 for v in vendidos_mes)

    historico = sorted(all_sold, key=lambda v: v.sold_at or datetime.min, reverse=True)[:10]

    return schemas.EmployeeStats(
        vendas_mes=len(vendidos_mes),
        faturamento_mes=faturamento_mes,
        comissao_mes=comissao_mes,
        total_vendas=len(all_sold),
        historico=historico,
    )


@router.patch("/{user_id}/goal", response_model=schemas.UserResponse)
def update_goal(
    user_id: int,
    data: schemas.GoalUpdate,
    background_tasks: BackgroundTasks,
    _: models.User = Depends(auth.require_owner),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.role == "employee",
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.monthly_goal = data.monthly_goal
    db.commit()
    db.refresh(user)

    background_tasks.add_task(
        notifications.notify_vendedor_meta_atualizada, user_id, data.monthly_goal
    )

    return user


@router.put("/me", response_model=schemas.UserResponse)
def update_me(
    data: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if data.name:
        current_user.name = data.name
    if data.email:
        current_user.email = data.email
    if data.new_password:
        if not data.current_password or not auth.verify_password(data.current_password, current_user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha atual incorreta")
        current_user.password_hash = auth.hash_password(data.new_password)
    db.commit()
    db.refresh(current_user)
    return current_user

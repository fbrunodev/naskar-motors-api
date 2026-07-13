from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
import re


# -------------- User --------------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    monthly_goal: Optional[int] = 5

    class Config:
        from_attributes = True


# -------------- StoreSettings --------------

class StoreSettingsBase(BaseModel):
    name: str
    whatsapp: Optional[str] = None
    city: Optional[str] = None
    primary_color: Optional[str] = "#FF0000"
    secondary_color: Optional[str] = "#000000"
    commission_rate: Optional[float] = 2.0


class StoreSettingsResponse(StoreSettingsBase):
    id: int
    logo_url: Optional[str] = None

    class Config:
        from_attributes = True


# -------------- Vehicle --------------

class VehicleBase(BaseModel):
    category: str
    brand: str
    model: str
    year: str
    km: int
    price: float
    color: Optional[str] = None
    description: Optional[str] = None
    is_featured: Optional[bool] = False
    transmission: Optional[str] = None
    fuel: Optional[str] = None
    doors: Optional[int] = None
    body_type: Optional[str] = None
    cilindrada: Optional[int] = None
    marchas: Optional[int] = None
    motor_type: Optional[str] = None
    cooling: Optional[str] = None
    moto_style: Optional[str] = None
    starter: Optional[str] = None
    front_brake: Optional[str] = None
    rear_brake: Optional[str] = None
    fuel_system: Optional[str] = None
    brand_id: Optional[int] = None
    model_id: Optional[int] = None
    features: List[str] = []
    commission_rate: Optional[float] = 2.0

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        if not re.match(r"^\d{4}(\/\d{4})?$", v):
            raise ValueError("Year must be in format 'YYYY' or 'YYYY/YYYY'")
        return v


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    photos: List[str] = []
    is_sold: bool
    created_at: datetime
    sold_at: Optional[datetime] = None
    sold_by: Optional[int] = None
    sold_by_name: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeStats(BaseModel):
    vendas_mes: int
    faturamento_mes: float
    comissao_mes: float
    total_vendas: int
    historico: List[VehicleResponse]


# -------------- Brand / VehicleModel --------------

class BrandBase(BaseModel):
    name: str
    logo_url: Optional[str] = None
    category: str = 'car'

class BrandCreate(BrandBase):
    pass

class BrandResponse(BrandBase):
    id: int
    category: str = 'car'
    created_at: datetime
    class Config:
        from_attributes = True

class VehicleModelBase(BaseModel):
    name: str
    brand_id: int

class VehicleModelCreate(VehicleModelBase):
    pass

class VehicleModelResponse(VehicleModelBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


# -------------- UserUpdate --------------

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


class GoalUpdate(BaseModel):
    monthly_goal: int


# -------------- Auth --------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ARRAY, DateTime, func, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base


class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    logo_url = Column(String, nullable=True)
    category = Column(String, default='car')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    models = relationship("VehicleModel", back_populates="brand")


class VehicleModel(Base):
    __tablename__ = "vehicle_models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    brand = relationship("Brand", back_populates="models")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="employee")  # "owner" or "employee"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    monthly_goal = Column(Integer, default=5)


class StoreSettings(Base):
    __tablename__ = "store_settings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    logo_url = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    city = Column(String, nullable=True)
    primary_color = Column(String, default="#FF0000")
    secondary_color = Column(String, default="#000000")
    commission_rate = Column(Numeric(5, 2), default=2.0)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    brand = Column(String)
    model = Column(String)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    model_id = Column(Integer, ForeignKey("vehicle_models.id"), nullable=True)
    brand_rel = relationship("Brand")
    model_rel = relationship("VehicleModel")
    year = Column(String)
    km = Column(Integer)
    price = Column(Float)
    color = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    photos = Column(ARRAY(String), default=[])
    features = Column(ARRAY(String), default=[])
    is_featured = Column(Boolean, default=False)
    is_sold = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sold_at = Column(DateTime, nullable=True, default=None)
    transmission = Column(String, nullable=True)
    fuel = Column(String, nullable=True)
    doors = Column(Integer, nullable=True)
    body_type = Column(String, nullable=True)
    sold_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    commission_rate = Column(Numeric(5, 2), default=2.0)
    sold_by_user = relationship("User", foreign_keys=[sold_by], lazy="joined")

    @property
    def sold_by_name(self):
        return self.sold_by_user.name if self.sold_by_user else None


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    endpoint = Column(Text, nullable=False)
    p256dh = Column(Text, nullable=False)
    auth = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

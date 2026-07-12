import os
from dotenv import load_dotenv

load_dotenv()

from database import engine, Base, SessionLocal
import models
import auth


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_owner = db.query(models.User).filter(models.User.role == "owner").first()
        if existing_owner:
            print(f"Owner already exists ({existing_owner.email}), skipping.")
        else:
            owner = models.User(
                name=os.getenv("SEED_OWNER_NAME", "Admin"),
                email=os.getenv("SEED_OWNER_EMAIL", "admin@naskar-motors.com"),
                password_hash=auth.hash_password(os.getenv("SEED_OWNER_PASSWORD", "changeme123")),
                role="owner",
                is_active=True,
            )
            db.add(owner)
            db.commit()
            print(f"Owner created: {owner.email}")

        existing_settings = db.query(models.StoreSettings).first()
        if existing_settings:
            print("Store settings already exist, skipping.")
        else:
            store = models.StoreSettings(
                name=os.getenv("SEED_STORE_NAME", "Naskar Motors"),
                whatsapp=os.getenv("SEED_STORE_WHATSAPP", "5585992289191"),
                city=os.getenv("SEED_STORE_CITY", "Fortaleza"),
                primary_color="#0a1628",
                secondary_color="#cc0000",
            )
            db.add(store)
            db.commit()
            print("Default store settings created.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

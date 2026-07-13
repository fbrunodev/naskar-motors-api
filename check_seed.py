from database import SessionLocal
from models import User, StoreSettings

db = SessionLocal()
users = db.query(User).all()
print("=== USERS ===")
for u in users:
    print(f"  {u.email} | role={u.role} | active={u.is_active}")

settings = db.query(StoreSettings).first()
print("\n=== STORE SETTINGS ===")
if settings:
    print(f"  name={settings.name} | whatsapp={settings.whatsapp} | city={settings.city}")
else:
    print("  (none)")

db.close()

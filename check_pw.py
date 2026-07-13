from database import SessionLocal
from models import User

db = SessionLocal()
u = db.query(User).filter(User.email == 'admin@naskar-motors.com').first()
print(f"email: {u.email}")
print(f"password_hash: {u.password_hash}")
db.close()

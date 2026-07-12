from datetime import datetime, timedelta
from database import SessionLocal
import models
import notifications


def check_encalhados() -> None:
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        for dias in [30, 60, 90]:
            janela_fim = now - timedelta(days=dias)
            janela_ini = now - timedelta(days=dias + 1)
            vehicles = db.query(models.Vehicle).filter(
                models.Vehicle.is_sold == False,
                models.Vehicle.created_at <= janela_fim,
                models.Vehicle.created_at > janela_ini,
            ).all()
            for v in vehicles:
                nome = f"{v.brand} {v.model} {v.year}"
                notifications.notify_owner_encalhado(nome, dias)
    finally:
        db.close()

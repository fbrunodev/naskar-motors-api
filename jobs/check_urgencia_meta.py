from datetime import datetime
import calendar
from database import SessionLocal
import models
import notifications


def check_urgencia_meta() -> None:
    now = datetime.utcnow()
    last_day = calendar.monthrange(now.year, now.month)[1]
    dias_restantes = last_day - now.day

    if dias_restantes > 3:
        return

    db = SessionLocal()
    try:
        start_of_month = datetime(now.year, now.month, 1)
        employees = db.query(models.User).filter(models.User.role == "employee").all()
        for emp in employees:
            meta = emp.monthly_goal or 5
            vendas = (
                db.query(models.Vehicle)
                .filter(
                    models.Vehicle.sold_by == emp.id,
                    models.Vehicle.is_sold == True,
                    models.Vehicle.sold_at >= start_of_month,
                )
                .count()
            )
            if vendas < meta:
                notifications.notify_vendedor_urgencia_meta(
                    emp.id, dias_restantes, meta - vendas
                )
    finally:
        db.close()

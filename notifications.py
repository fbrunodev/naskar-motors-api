import json
import logging
from database import SessionLocal
import models
import vapid_keys

logger = logging.getLogger(__name__)


def send_push(db, user_id: int, title: str, body: str, icon: str = "/icon.png") -> None:
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning("pywebpush not installed — skipping push notification")
        return

    subs = db.query(models.PushSubscription).filter(
        models.PushSubscription.user_id == user_id
    ).all()

    for sub in subs:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=json.dumps({"title": title, "body": body, "icon": icon}),
                vapid_private_key=vapid_keys.VAPID_PRIVATE_KEY,
                vapid_claims=vapid_keys.VAPID_CLAIMS,
            )
        except WebPushException as exc:
            if exc.response and exc.response.status_code in (403, 404, 410):
                db.delete(sub)
                db.commit()
            else:
                logger.error("Push error for user %d: %s", user_id, exc)
        except Exception as exc:
            logger.error("Unexpected push error for user %d: %s", user_id, exc)


def _owner_ids(db) -> list[int]:
    return [u.id for u in db.query(models.User).filter(models.User.role == "owner").all()]


# ---- Owner notifications ----

def notify_owner_venda(vendedor_nome: str, veiculo_nome: str, preco: float) -> None:
    db = SessionLocal()
    try:
        for oid in _owner_ids(db):
            send_push(db, oid, "💰 Venda fechada!",
                      f"{vendedor_nome} fechou o {veiculo_nome} por R$ {preco:,.0f}. Boa venda! 🚗")
    finally:
        db.close()


def notify_owner_novo_veiculo(vendedor_nome: str, veiculo_nome: str) -> None:
    db = SessionLocal()
    try:
        for oid in _owner_ids(db):
            send_push(db, oid, "🚗 Novo veículo no catálogo",
                      f"{vendedor_nome} cadastrou o {veiculo_nome}")
    finally:
        db.close()


def notify_owner_encalhado(veiculo_nome: str, dias: int) -> None:
    db = SessionLocal()
    try:
        for oid in _owner_ids(db):
            send_push(db, oid, "⚠️ Atenção ao estoque",
                      f"{veiculo_nome} está há {dias} dias no estoque. Que tal um destaque?")
    finally:
        db.close()


def notify_owner_meta_batida(vendedor_nome: str) -> None:
    db = SessionLocal()
    try:
        for oid in _owner_ids(db):
            send_push(db, oid, "🏆 Meta batida!", f"{vendedor_nome} atingiu a meta este mês. Grande resultado!")
    finally:
        db.close()


# ---- Vendor notifications ----

def notify_vendedor_meta_atualizada(user_id: int, nova_meta: int) -> None:
    db = SessionLocal()
    try:
        send_push(db, user_id, "🎯 Nova meta definida",
                  f"Sua meta para este mês é {nova_meta} vendas. Bora lá!")
    finally:
        db.close()


def notify_vendedor_venda(user_id: int, veiculo_nome: str, comissao: float) -> None:
    db = SessionLocal()
    try:
        send_push(db, user_id, "✅ Venda confirmada!",
                  f"Você vendeu o veículo {veiculo_nome} · Comissão: R$ {comissao:,.0f}")
    finally:
        db.close()


def notify_vendedor_50_porcento(user_id: int, vendas: int, meta: int) -> None:
    db = SessionLocal()
    try:
        restante = meta - vendas
        send_push(db, user_id, "💪 Você está na metade!",
                  f"{vendas} vendas feitas, faltam só {restante} para bater a meta!")
    finally:
        db.close()


def notify_vendedor_meta_batida(user_id: int) -> None:
    db = SessionLocal()
    try:
        send_push(db, user_id, "🎉 Parabéns, meta batida!", "Incrível! Você bateu sua meta deste mês! 🚀")
    finally:
        db.close()


def notify_vendedor_urgencia_meta(user_id: int, dias_restantes: int, vendas_faltando: int) -> None:
    db = SessionLocal()
    try:
        send_push(db, user_id, "⏰ O mês está acabando!",
                  f"Faltam {dias_restantes} dias e você precisa de {vendas_faltando} vendas. Você consegue!")
    finally:
        db.close()

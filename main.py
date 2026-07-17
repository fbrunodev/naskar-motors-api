import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth, users, settings, vehicles, uploads, brands
from routes import notifications

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from apscheduler.schedulers.background import BackgroundScheduler
    from jobs.check_encalhados import check_encalhados
    from jobs.check_urgencia_meta import check_urgencia_meta
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_encalhados, 'cron', hour=9, minute=0)
    scheduler.add_job(check_urgencia_meta, 'cron', hour=9, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Naskar Motors API", lifespan=lifespan)


@app.get("/health")
@app.head("/health")
def health():
    return {"status": "ok"}


_cors_env = os.getenv("CORS_ORIGINS", "")
_cors_origins = (
    [o.strip() for o in _cors_env.split(",") if o.strip()]
    if _cors_env
    else ["https://naskar-motors-frontend.vercel.app"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(settings.router)
app.include_router(vehicles.router)
app.include_router(uploads.router)
app.include_router(brands.router, prefix="/brands", tags=["brands"])
app.include_router(notifications.router)


@app.get("/")
def root():
    return {"message": "Naskar Motors API working!"}

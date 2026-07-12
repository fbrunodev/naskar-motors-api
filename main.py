from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth, users, settings, vehicles, uploads, brands
from routes import notifications


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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


@app.get("/health")
def health():
    return {"status": "ok"}

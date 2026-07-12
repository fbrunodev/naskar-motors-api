from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import time

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


def create_engine_with_retry(url, retries=10, delay=2):
    for attempt in range(1, retries + 1):
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"Database connection established on attempt {attempt}.")
            return engine
        except Exception as e:
            print(f"Attempt {attempt}/{retries}: Database not ready — {e}")
            if attempt < retries:
                time.sleep(delay)
    raise RuntimeError("Could not connect to the database after multiple retries.")


engine = create_engine_with_retry(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base =  declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
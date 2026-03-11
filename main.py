from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import APP_NAME
from app.db.database import engine

app = FastAPI(title=APP_NAME, version="1.0.0")


@app.get("/")
def root():
    return {"message": "HABITA backend running"}


@app.get("/health/db")
def health_db():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "Database connection OK"}
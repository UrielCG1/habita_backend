import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import APP_NAME, STORAGE_DIR
from app.db.database import engine

os.makedirs(STORAGE_DIR, exist_ok=True)

app = FastAPI(title=APP_NAME, version="1.0.0")


@app.get("/")
def root():
    return {"message": "HABITA backend running"}


@app.get("/health/db")
def health_db():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "Database connection OK"}


app.mount("/media", StaticFiles(directory=STORAGE_DIR), name="media")
app.include_router(api_router, prefix="/api")
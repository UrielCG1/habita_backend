import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import APP_NAME, STORAGE_DIR
from app.core.responses import error_response
from app.db.database import engine

os.makedirs(STORAGE_DIR, exist_ok=True)

app = FastAPI(title=APP_NAME, version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_type = "http_error"

    if exc.status_code == 404:
        error_type = "not_found"
    elif exc.status_code == 400:
        error_type = "bad_request"
    elif exc.status_code == 409:
        error_type = "conflict"
    elif exc.status_code == 401:
        error_type = "unauthorized"
    elif exc.status_code == 403:
        error_type = "forbidden"

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error_type=error_type,
            message=str(exc.detail),
            details=None,
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_response(
            error_type="validation_error",
            message="Validation error",
            details=exc.errors(),
        ),
    )


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
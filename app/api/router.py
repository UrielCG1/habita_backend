from fastapi import APIRouter

from app.api.endpoints.properties import router as properties_router

api_router = APIRouter()
api_router.include_router(properties_router)
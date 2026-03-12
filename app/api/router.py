from fastapi import APIRouter

from app.api.endpoints.properties import router as properties_router
from app.api.endpoints.property_images import router as property_images_router

api_router = APIRouter()
api_router.include_router(properties_router)
api_router.include_router(property_images_router)
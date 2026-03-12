from fastapi import APIRouter

from app.api.endpoints.favorites import router as favorites_router
from app.api.endpoints.properties import router as properties_router
from app.api.endpoints.property_images import router as property_images_router
from app.api.endpoints.rental_requests import router as rental_requests_router
from app.api.endpoints.reviews import router as reviews_router

api_router = APIRouter()
api_router.include_router(properties_router)
api_router.include_router(property_images_router)
api_router.include_router(favorites_router)
api_router.include_router(rental_requests_router)
api_router.include_router(reviews_router)
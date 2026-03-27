from fastapi import APIRouter

from app.api.endpoints.favorites import router as favorites_router
from app.api.endpoints.properties import router as properties_router
from app.api.endpoints.property_images import router as property_images_router
from app.api.endpoints.rental_requests import router as rental_requests_router
from app.api.endpoints.reviews import router as reviews_router
from app.api.endpoints.users import router as users_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.owners import router as owners_router

api_router = APIRouter()
api_router.include_router(properties_router)
api_router.include_router(property_images_router)
api_router.include_router(favorites_router)
api_router.include_router(rental_requests_router)
api_router.include_router(reviews_router)
api_router.include_router(users_router)
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(owners_router)
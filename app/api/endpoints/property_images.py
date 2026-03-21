from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.schemas.common import SuccessResponse
from app.core.responses import success_response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.property_image import PropertyImageResponse, PropertyImagePatch
from app.services.property_image_service import (
    delete_property_image,
    list_property_images,
    upload_property_images,
    patch_property_image,
    get_property_image_content,
)

router = APIRouter(tags=["Property Images"])


@router.post(
    "/properties/{property_id}/images",
    response_model=list[PropertyImageResponse],
    status_code=status.HTTP_201_CREATED,
)
def upload_images_to_property(
    property_id: int,
    files: list[UploadFile] = File(...),
    alt_text: Optional[str] = Form(default=None),
    set_first_as_cover: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    return upload_property_images(
        db=db,
        property_id=property_id,
        files=files,
        alt_text=alt_text,
        set_first_as_cover=set_first_as_cover,
    )


@router.get(
    "/properties/{property_id}/images",
    response_model=list[PropertyImageResponse],
)
def list_images_of_property(property_id: int, db: Session = Depends(get_db)):
    return list_property_images(db, property_id)


@router.delete(
    "/property-images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_property_image_endpoint(image_id: int, db: Session = Depends(get_db)):
    delete_property_image(db, image_id)
    return None


@router.patch("/property-images/{image_id}", response_model=SuccessResponse[PropertyImageResponse])
def patch_property_image_endpoint(
    image_id: int,
    payload: PropertyImagePatch,
    db: Session = Depends(get_db),
):
    image_obj = patch_property_image(db=db, image_id=image_id, payload=payload)
    return success_response(image_obj)



@router.get("/property-images/{image_id}/content")
def get_property_image_content_endpoint(
    image_id: int,
    db: Session = Depends(get_db),
):
    return get_property_image_content(db, image_id)
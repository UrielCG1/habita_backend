import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import MEDIA_URL, PROPERTY_IMAGES_DIR, STORAGE_DIR
from app.models.property import Property
from app.models.property_image import PropertyImage

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _build_file_url(relative_path: str) -> str:
    return f"{MEDIA_URL}/{relative_path}"


def _serialize_image(image: PropertyImage) -> dict:
    return {
        "id": image.id,
        "property_id": image.property_id,
        "file_path": image.file_path,
        "file_url": _build_file_url(image.file_path),
        "alt_text": image.alt_text,
        "is_cover": image.is_cover,
        "sort_order": image.sort_order,
    }


def _get_property_or_404(db: Session, property_id: int) -> Property:
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_obj


def list_property_images(db: Session, property_id: int) -> list[dict]:
    _get_property_or_404(db, property_id)

    images = (
        db.query(PropertyImage)
        .filter(PropertyImage.property_id == property_id)
        .order_by(PropertyImage.is_cover.desc(), PropertyImage.sort_order.asc(), PropertyImage.id.asc())
        .all()
    )
    return [_serialize_image(image) for image in images]


def upload_property_images(
    db: Session,
    property_id: int,
    files: list[UploadFile],
    alt_text: Optional[str] = None,
    set_first_as_cover: bool = False,
) -> list[dict]:
    _get_property_or_404(db, property_id)
    os.makedirs(PROPERTY_IMAGES_DIR, exist_ok=True)

    existing_count = (
        db.query(PropertyImage)
        .filter(PropertyImage.property_id == property_id)
        .count()
    )

    created_images: list[PropertyImage] = []

    for index, file in enumerate(files):
        if not file.filename:
            continue

        ext = Path(file.filename).suffix.lower()

        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension: {ext}. Allowed: jpg, jpeg, png, webp",
            )

        if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type: {file.content_type}",
            )

        filename = f"{uuid4().hex}{ext}"
        relative_path = f"properties/{filename}"
        absolute_path = os.path.join(PROPERTY_IMAGES_DIR, filename)

        with open(absolute_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image = PropertyImage(
            property_id=property_id,
            file_path=relative_path,
            alt_text=alt_text,
            is_cover=False,
            sort_order=existing_count + index,
        )

        db.add(image)
        db.flush()
        created_images.append(image)

    if not created_images:
        raise HTTPException(status_code=400, detail="No valid files were uploaded")

    if set_first_as_cover:
        first_image_id = created_images[0].id
        (
            db.query(PropertyImage)
            .filter(PropertyImage.property_id == property_id)
            .update({"is_cover": False}, synchronize_session=False)
        )
        created_images[0].is_cover = True

    elif existing_count == 0:
        created_images[0].is_cover = True

    db.commit()

    for image in created_images:
        db.refresh(image)

    return [_serialize_image(image) for image in created_images]


def delete_property_image(db: Session, image_id: int) -> None:
    image = db.query(PropertyImage).filter(PropertyImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    absolute_path = os.path.join(STORAGE_DIR, image.file_path)

    if os.path.exists(absolute_path):
        os.remove(absolute_path)

    db.delete(image)
    db.commit()
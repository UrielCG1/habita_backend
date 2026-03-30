from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/technical-docs", tags=["technical-docs"])

FAKE_DOCS = [
    {
        "id": 1,
        "title": "Arquitectura técnica HABITA",
        "description": "Documento general",
        "file_name": "arquitectura_habita.pdf",
        "file_path": "/var/www/html/habita/backend/arquitectura_habita.pdf",
        "uploaded_at": "2026-03-29T12:00:00",
    }
]

@router.get("")
def list_technical_docs():
    return {
        "data": [
            {
                "id": doc["id"],
                "title": doc["title"],
                "description": doc["description"],
                "file_name": doc["file_name"],
                "uploaded_at": doc["uploaded_at"],
            }
            for doc in FAKE_DOCS
        ]
    }

@router.get("/{document_id}/download")
def download_technical_doc(document_id: int):
    doc = next((d for d in FAKE_DOCS if d["id"] == document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    return FileResponse(
        path=doc["file_path"],
        filename=doc["file_name"],
        media_type="application/pdf",
    )
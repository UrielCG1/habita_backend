from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .dependencies import require_admin
from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.admin import AdminDashboardDataResponse
from app.schemas.common import SuccessResponse
from app.services.admin_service import get_admin_dashboard_data

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=SuccessResponse[AdminDashboardDataResponse])
def admin_dashboard_endpoint(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    data = get_admin_dashboard_data(db=db)
    return success_response(data)
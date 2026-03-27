from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.common import SuccessResponse
from app.schemas.owner_dashboard import OwnerDashboardReputationResponse
from app.services.owner_dashboard_service import get_owner_dashboard_reputation

router = APIRouter(prefix="/owners", tags=["Owners"])


@router.get(
    "/{owner_id}/dashboard/reputation",
    response_model=SuccessResponse[OwnerDashboardReputationResponse],
)
def owner_dashboard_reputation_endpoint(
    owner_id: int,
    db: Session = Depends(get_db),
):
    data = get_owner_dashboard_reputation(db=db, owner_id=owner_id)
    return success_response(data)
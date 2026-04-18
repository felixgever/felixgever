from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_user_role_names
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.common import AuditLogRead

router = APIRouter()


@router.get("/", response_model=list[AuditLogRead])
def list_audit_logs(
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    if "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    query = select(AuditLog).where(AuditLog.is_deleted.is_(False))
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    return list(db.scalars(query.order_by(AuditLog.created_at.desc()).limit(limit)).all())

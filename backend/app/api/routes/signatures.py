from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    enforce_feature_for_project,
    get_current_user,
    get_db,
    get_user_role_names,
)
from app.models.project import Project, Resident, Signature
from app.models.user import User
from app.schemas.common import SignatureCreate, SignatureRead, SignatureStatusUpdate
from app.services.audit_service import create_audit_log
from app.services.signature_service import request_signature_mock

router = APIRouter()


@router.post("/", response_model=SignatureRead, status_code=201)
def create_signature_request(
    signature_in: SignatureCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Signature:
    project = db.get(Project, signature_in.project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")
    enforce_feature_for_project(
        db=db,
        current_user=current_user,
        project=project,
        feature_key="basic_signatures",
    )

    resident = db.get(Resident, signature_in.resident_id)
    if not resident or resident.project_id != project.id or resident.is_deleted:
        raise HTTPException(status_code=400, detail="Invalid resident for project")

    provider_response = request_signature_mock(
        resident_id=resident.id,
        provider=signature_in.signature_provider,
    )
    signature = Signature(
        project_id=signature_in.project_id,
        resident_id=signature_in.resident_id,
        signature_provider=signature_in.signature_provider,
        status=provider_response["status"],
        external_reference=provider_response["external_reference"],
    )
    db.add(signature)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="signature",
        entity_id=str(signature.id),
        action="create_request",
        after_data=signature_in.model_dump(),
    )
    db.commit()
    db.refresh(signature)
    return signature


@router.get("/", response_model=list[SignatureRead])
def list_signatures(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Signature]:
    return list(
        db.scalars(
            select(Signature).where(
                Signature.project_id == project_id,
                Signature.is_deleted.is_(False),
            )
        ).all()
    )


@router.patch("/{signature_id}/status", response_model=SignatureRead)
def update_signature_status(
    signature_id: int,
    payload: SignatureStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Signature:
    signature = db.get(Signature, signature_id)
    if not signature or signature.is_deleted:
        raise HTTPException(status_code=404, detail="Signature not found")

    project = db.get(Project, signature.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to signature")

    signature.status = payload.status
    if payload.external_reference:
        signature.external_reference = payload.external_reference
    if payload.status == "signed":
        signature.signed_at = datetime.now(tz=timezone.utc)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="signature",
        entity_id=str(signature.id),
        action="update_status",
        after_data=payload.model_dump(),
    )
    db.commit()
    db.refresh(signature)
    return signature

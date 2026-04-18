from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    enforce_feature_for_project,
    get_current_user,
    get_db,
    get_user_role_names,
)
from app.models.project import Project, Resident, Unit
from app.models.user import User
from app.schemas.common import ResidentCreate, ResidentRead, ResidentUpdate
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.post("/", response_model=ResidentRead, status_code=201)
def create_resident(
    resident_in: ResidentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resident:
    project = db.get(Project, resident_in.project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")
    enforce_feature_for_project(
        db=db,
        current_user=current_user,
        project=project,
        feature_key="basic_residents",
    )

    unit = None
    if resident_in.unit_id is not None:
        unit = db.get(Unit, resident_in.unit_id)
        if not unit or unit.project_id != project.id or unit.is_deleted:
            raise HTTPException(status_code=400, detail="Invalid unit_id for project")

    resident = Resident(**resident_in.model_dump())
    db.add(resident)
    if unit:
        unit.residents_count += 1
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="resident",
        entity_id=str(resident.id),
        action="create",
        after_data=resident_in.model_dump(),
    )
    db.commit()
    db.refresh(resident)
    return resident


@router.get("/", response_model=list[ResidentRead])
def list_residents(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Resident]:
    return list(
        db.scalars(
            select(Resident).where(
                Resident.project_id == project_id, Resident.is_deleted.is_(False)
            )
        ).all()
    )


@router.patch("/{resident_id}", response_model=ResidentRead)
def update_resident(
    resident_id: int,
    resident_in: ResidentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resident:
    resident = db.get(Resident, resident_id)
    if not resident or resident.is_deleted:
        raise HTTPException(status_code=404, detail="Resident not found")

    project = db.get(Project, resident.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to resident")

    before_data = {
        "full_name": resident.full_name,
        "phone": resident.phone,
        "email": resident.email,
        "consent_status": resident.consent_status,
    }
    for key, value in resident_in.model_dump(exclude_none=True).items():
        setattr(resident, key, value)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="resident",
        entity_id=str(resident.id),
        action="update",
        before_data=before_data,
        after_data=resident_in.model_dump(exclude_none=True),
    )
    db.commit()
    db.refresh(resident)
    return resident

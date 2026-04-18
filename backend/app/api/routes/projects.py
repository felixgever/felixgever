from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_db, get_user_role_names, require_roles
from app.billing.logic import get_stage_index
from app.models.project import Project, Unit
from app.models.user import ProjectMembership, User
from app.schemas.common import ProjectCreate, ProjectRead, ProjectUpdate, UnitCreate, UnitRead
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.get("/", response_model=list[ProjectRead])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Project]:
    roles = get_user_role_names(current_user)
    query = select(Project).where(Project.is_deleted.is_(False)).options(selectinload(Project.units))
    if "admin" not in roles:
        query = query.where(Project.owner_id == current_user.id)
    return list(db.scalars(query).all())


@router.post("/", response_model=ProjectRead, status_code=201)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(require_roles("organizer", "admin")),
    db: Session = Depends(get_db),
) -> Project:
    project = Project(
        name=project_in.name,
        city=project_in.city,
        address=project_in.address,
        description=project_in.description,
        owner_id=current_user.id,
        per_unit_price_ils=project_in.per_unit_price_ils,
    )
    db.add(project)
    db.flush()
    membership = ProjectMembership(
        project_id=project.id,
        user_id=current_user.id,
        project_role="organizer",
        notes="Owner membership",
    )
    db.add(membership)
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="project",
        entity_id=str(project.id),
        action="create",
        after_data={"name": project.name, "city": project.city},
    )
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    project = db.scalar(
        select(Project)
        .where(Project.id == project_id, Project.is_deleted.is_(False))
        .options(selectinload(Project.units))
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        membership = db.scalar(
            select(ProjectMembership).where(
                ProjectMembership.project_id == project.id,
                ProjectMembership.user_id == current_user.id,
                ProjectMembership.is_deleted.is_(False),
            )
        )
        if not membership:
            raise HTTPException(status_code=403, detail="No access to project")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    current_user: User = Depends(require_roles("organizer", "admin")),
    db: Session = Depends(get_db),
) -> Project:
    project = db.get(Project, project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")

    before_stage = project.current_stage
    for key, value in project_in.model_dump(exclude_none=True).items():
        setattr(project, key, value)
    if get_stage_index(project.current_stage) >= get_stage_index("developer_selection"):
        project.developer_payment_required = True
    if before_stage != project.current_stage and project.current_stage == "developer_selection":
        project.developer_payment_required = True
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="project",
        entity_id=str(project.id),
        action="update",
        before_data={"current_stage": before_stage},
        after_data=project_in.model_dump(exclude_none=True),
    )
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    current_user: User = Depends(require_roles("organizer", "admin")),
    db: Session = Depends(get_db),
) -> None:
    project = db.get(Project, project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")
    project.is_deleted = True
    project.is_active = False
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="project",
        entity_id=str(project.id),
        action="soft_delete",
    )
    db.commit()


@router.post("/{project_id}/units", response_model=UnitRead, status_code=201)
def add_unit(
    project_id: int,
    unit_in: UnitCreate,
    current_user: User = Depends(require_roles("organizer", "admin")),
    db: Session = Depends(get_db),
) -> Unit:
    project = db.get(Project, project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project_id != unit_in.project_id:
        raise HTTPException(status_code=400, detail="Path project_id does not match payload")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")

    unit = Unit(
        project_id=project_id,
        unit_number=unit_in.unit_number,
        floor=unit_in.floor,
        existing_area_sqm=unit_in.existing_area_sqm,
    )
    db.add(unit)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="unit",
        entity_id=str(unit.id),
        action="create",
        after_data={"project_id": project_id, "unit_number": unit.unit_number},
    )
    db.commit()
    db.refresh(unit)
    return unit


@router.get("/{project_id}/units", response_model=list[UnitRead])
def list_units(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Unit]:
    project = db.get(Project, project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return list(
        db.scalars(
            select(Unit).where(Unit.project_id == project_id, Unit.is_deleted.is_(False))
        ).all()
    )


@router.post("/{project_id}/advance-stage", response_model=ProjectRead)
def advance_stage(
    project_id: int,
    current_user: User = Depends(require_roles("organizer", "admin")),
    db: Session = Depends(get_db),
) -> Project:
    project = db.get(Project, project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")

    current_idx = get_stage_index(project.current_stage)
    if current_idx < 0:
        raise HTTPException(status_code=400, detail="Project stage is invalid")
    if current_idx >= get_stage_index("occupancy"):
        raise HTTPException(status_code=400, detail="Project is already at final stage")
    next_idx = current_idx + 1
    stages = [
        "identification",
        "organization",
        "developer_selection",
        "planning",
        "permit",
        "execution",
        "occupancy",
    ]
    project.current_stage = stages[next_idx]
    if project.current_stage == "developer_selection":
        project.developer_payment_required = True
    project.updated_at = datetime.now(tz=timezone.utc)
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="project",
        entity_id=str(project.id),
        action="advance_stage",
        after_data={"current_stage": project.current_stage},
    )
    db.commit()
    db.refresh(project)
    return project

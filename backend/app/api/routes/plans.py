from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    enforce_feature_for_project,
    get_current_user,
    get_db,
    get_user_role_names,
)
from app.models.project import Plan, Project
from app.models.user import User
from app.schemas.common import PlanCreate, PlanRead
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.get("/", response_model=list[PlanRead])
def list_plans(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Plan]:
    return list(
        db.scalars(
            select(Plan).where(Plan.project_id == project_id, Plan.is_deleted.is_(False))
        ).all()
    )


@router.post("/", response_model=PlanRead, status_code=201)
def create_plan(
    plan_in: PlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Plan:
    project = db.get(Project, plan_in.project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")
    enforce_feature_for_project(
        db=db,
        current_user=current_user,
        project=project,
        feature_key="planning_module",
    )

    plan = Plan(**plan_in.model_dump())
    db.add(plan)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="plan",
        entity_id=str(plan.id),
        action="create",
        after_data=plan_in.model_dump(),
    )
    db.commit()
    db.refresh(plan)
    return plan


@router.post("/{plan_id}/score/{score}", response_model=PlanRead)
def score_feasibility(
    plan_id: int,
    score: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Plan:
    plan = db.get(Plan, plan_id)
    if not plan or plan.is_deleted:
        raise HTTPException(status_code=404, detail="Plan not found")
    project = db.get(Project, plan.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to plan")
    enforce_feature_for_project(
        db=db,
        current_user=current_user,
        project=project,
        feature_key="feasibility_module",
    )
    plan.feasibility_score = max(0, min(score, 100))
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="plan",
        entity_id=str(plan.id),
        action="score_feasibility",
        after_data={"feasibility_score": plan.feasibility_score},
    )
    db.commit()
    db.refresh(plan)
    return plan

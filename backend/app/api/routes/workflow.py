from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_user_role_names
from app.models.project import Project, Task, WorkflowStage
from app.models.user import User
from app.schemas.common import (
    TaskCreate,
    TaskRead,
    WorkflowStageCreate,
    WorkflowStageRead,
)
from app.services.audit_service import create_audit_log
from app.utils.constants import WORKFLOW_STAGES

router = APIRouter()


@router.get("/stages", response_model=list[WorkflowStageRead])
def list_stages(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WorkflowStage]:
    return list(
        db.scalars(
            select(WorkflowStage).where(
                WorkflowStage.project_id == project_id,
                WorkflowStage.is_deleted.is_(False),
            )
        ).all()
    )


@router.post("/stages", response_model=WorkflowStageRead, status_code=201)
def create_stage(
    stage_in: WorkflowStageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkflowStage:
    project = db.get(Project, stage_in.project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")
    if stage_in.stage_key not in WORKFLOW_STAGES:
        raise HTTPException(status_code=400, detail="Invalid workflow stage")

    stage = WorkflowStage(
        project_id=stage_in.project_id,
        stage_key=stage_in.stage_key,
        status=stage_in.status,
        notes=stage_in.notes,
        started_at=datetime.now(tz=timezone.utc) if stage_in.status == "active" else None,
    )
    db.add(stage)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="workflow_stage",
        entity_id=str(stage.id),
        action="create",
        after_data=stage_in.model_dump(),
    )
    db.commit()
    db.refresh(stage)
    return stage


@router.post("/stages/{stage_id}/complete", response_model=WorkflowStageRead)
def complete_stage(
    stage_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkflowStage:
    stage = db.get(WorkflowStage, stage_id)
    if not stage or stage.is_deleted:
        raise HTTPException(status_code=404, detail="Stage not found")
    project = db.get(Project, stage.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to workflow stage")

    stage.status = "completed"
    stage.completed_at = datetime.now(tz=timezone.utc)
    project.current_stage = stage.stage_key
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="workflow_stage",
        entity_id=str(stage.id),
        action="complete",
        after_data={"status": stage.status, "completed_at": stage.completed_at.isoformat()},
    )
    db.commit()
    db.refresh(stage)
    return stage


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Task]:
    return list(
        db.scalars(
            select(Task).where(Task.project_id == project_id, Task.is_deleted.is_(False))
        ).all()
    )


@router.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Task:
    project = db.get(Project, task_in.project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")

    task = Task(**task_in.model_dump())
    db.add(task)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="task",
        entity_id=str(task.id),
        action="create",
        after_data=task_in.model_dump(),
    )
    db.commit()
    db.refresh(task)
    return task

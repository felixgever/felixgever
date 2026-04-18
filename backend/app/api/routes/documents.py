from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    enforce_feature_for_project,
    get_current_user,
    get_db,
    get_user_role_names,
)
from app.models.project import Document, Project
from app.models.user import User
from app.schemas.common import DocumentCreate, DocumentRead
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.post("/", response_model=DocumentRead, status_code=201)
def create_document(
    document_in: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    project = db.get(Project, document_in.project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")
    enforce_feature_for_project(
        db=db,
        current_user=current_user,
        project=project,
        feature_key="basic_documents",
    )

    document = Document(**document_in.model_dump())
    db.add(document)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="document",
        entity_id=str(document.id),
        action="create",
        after_data=document_in.model_dump(),
    )
    db.commit()
    db.refresh(document)
    return document


@router.get("/", response_model=list[DocumentRead])
def list_documents(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Document]:
    return list(
        db.scalars(
            select(Document).where(
                Document.project_id == project_id,
                Document.is_deleted.is_(False),
            )
        ).all()
    )

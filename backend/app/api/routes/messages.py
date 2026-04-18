from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    enforce_feature_for_project,
    get_current_user,
    get_db,
    get_user_role_names,
)
from app.models.project import Message, Project
from app.models.user import User
from app.schemas.common import MessageCreate, MessageRead
from app.services.audit_service import create_audit_log
from app.services.communication_service import send_message_mock

router = APIRouter()


@router.get("/", response_model=list[MessageRead])
def list_messages(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Message]:
    return list(
        db.scalars(
            select(Message).where(
                Message.project_id == project_id,
                Message.is_deleted.is_(False),
            )
        ).all()
    )


@router.post("/", response_model=MessageRead, status_code=201)
def send_message(
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    project = db.get(Project, message_in.project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")
    enforce_feature_for_project(
        db=db,
        current_user=current_user,
        project=project,
        feature_key="basic_communication",
    )

    provider_response = send_message_mock(
        channel=message_in.channel,
        recipient=message_in.recipient,
        body=message_in.body,
    )
    message = Message(
        project_id=message_in.project_id,
        sender_id=current_user.id,
        channel=message_in.channel,
        recipient=message_in.recipient,
        body=message_in.body,
        delivery_status=provider_response["status"],
        external_message_id=provider_response["external_message_id"],
    )
    db.add(message)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="message",
        entity_id=str(message.id),
        action="send",
        after_data=message_in.model_dump(),
    )
    db.commit()
    db.refresh(message)
    return message

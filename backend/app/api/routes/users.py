from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles
from app.models.rbac import Role
from app.models.user import User
from app.schemas.common import UserRead, UserUpdate
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> list[User]:
    return list(db.scalars(select(User).where(User.is_deleted.is_(False))).all())


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user.id and "admin" not in {r.name for r in current_user.roles}:
        raise HTTPException(status_code=403, detail="Access denied")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user.id and "admin" not in {r.name for r in current_user.roles}:
        raise HTTPException(status_code=403, detail="Access denied")

    before_data = {
        "full_name": user.full_name,
        "organization_name": user.organization_name,
        "is_active": user.is_active,
    }
    for key, value in user_in.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="user",
        entity_id=str(user.id),
        action="update",
        before_data=before_data,
        after_data=user_in.model_dump(exclude_none=True),
    )
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/roles/{role_name}", response_model=UserRead)
def assign_role(
    user_id: int,
    role_name: str,
    _: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> User:
    user = db.get(User, user_id)
    role = db.scalar(select(Role).where(Role.name == role_name, Role.is_deleted.is_(False)))
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role not in user.roles:
        user.roles.append(role)
    db.commit()
    db.refresh(user)
    return user

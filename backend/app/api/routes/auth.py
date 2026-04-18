from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.auth.security import create_access_token, get_password_hash, verify_password
from app.models.rbac import Role
from app.models.user import User
from app.schemas.common import Token, UserCreate, UserRead
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.scalar(select(User).where(User.email == user_in.email, User.is_deleted.is_(False)))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        organization_name=user_in.organization_name,
    )
    if user_in.roles:
        roles = db.scalars(select(Role).where(Role.name.in_(user_in.roles))).all()
        user.roles = list(roles)
    db.add(user)
    db.flush()
    create_audit_log(
        db,
        actor_id=user.id,
        entity_type="user",
        entity_id=str(user.id),
        action="register",
        after_data={"email": user.email, "roles": [role.name for role in user.roles]},
    )
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = db.scalar(
        select(User).where(User.email == form_data.username, User.is_deleted.is_(False))
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(str(user.id), timedelta(minutes=60 * 24))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

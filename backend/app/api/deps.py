from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.billing.logic import is_feature_allowed
from app.db.session import SessionLocal
from app.models.project import Project
from app.models.user import ProjectMembership, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", 0))
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception
    return user


def require_roles(*allowed_roles: str) -> Callable:
    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        user_role_names = {role.name for role in current_user.roles}
        if not user_role_names.intersection(set(allowed_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role not allowed. Requires one of: {', '.join(allowed_roles)}",
            )
        return current_user

    return _dependency


def get_user_role_names(user: User) -> set[str]:
    return {role.name for role in user.roles}


def get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def enforce_project_access(
    project_id_param: str = "project_id",
) -> Callable:
    def _dependency(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> Project:
        project_id_value = request.path_params.get(project_id_param)
        if project_id_value is None:
            project_id_value = request.query_params.get(project_id_param)
        if project_id_value is None:
            raise HTTPException(status_code=400, detail="project_id is required")

        project = get_project_or_404(db, int(project_id_value))
        if project.owner_id == current_user.id or "admin" in get_user_role_names(current_user):
            return project

        membership = db.scalar(
            select(ProjectMembership).where(
                ProjectMembership.project_id == project.id,
                ProjectMembership.user_id == current_user.id,
                ProjectMembership.is_deleted.is_(False),
            )
        )
        if membership:
            return project
        raise HTTPException(status_code=403, detail="No access to project")

    return _dependency


def enforce_feature(feature_key: str) -> Callable:
    def _dependency(
        project: Project = Depends(enforce_project_access()),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> Project:
        allowed, reason = is_feature_allowed(
            db, project=project, user_id=current_user.id, feature_key=feature_key
        )
        if not allowed:
            raise HTTPException(status_code=402, detail=reason or "Feature is blocked by plan")
        return project

    return _dependency


def enforce_feature_for_project(
    *,
    db: Session,
    current_user: User,
    project: Project,
    feature_key: str,
) -> None:
    allowed, reason = is_feature_allowed(
        db,
        project=project,
        user_id=current_user.id,
        feature_key=feature_key,
    )
    if not allowed:
        raise HTTPException(status_code=402, detail=reason or "Feature is blocked by plan")

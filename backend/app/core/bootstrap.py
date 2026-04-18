import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rbac import Permission, Role

ROLE_PERMISSIONS = {
    "organizer": [
        "project.read",
        "project.write",
        "resident.read",
        "resident.write",
        "signature.read",
        "signature.write",
        "document.read",
        "document.write",
        "workflow.read",
        "workflow.write",
        "billing.read",
    ],
    "developer": [
        "project.read",
        "bid.read",
        "bid.write",
        "plan.read",
        "document.read",
        "billing.read",
    ],
    "resident": [
        "project.read",
        "signature.read",
        "document.read",
        "message.read",
    ],
    "professional": [
        "project.read",
        "plan.read",
        "plan.write",
        "document.read",
        "document.write",
        "workflow.read",
    ],
    "admin": [
        "admin.full",
    ],
}


def seed_roles_permissions(db: Session) -> None:
    existing_roles = {role.name: role for role in db.scalars(select(Role)).all()}
    existing_permissions = {
        permission.key: permission for permission in db.scalars(select(Permission)).all()
    }
    for role_name, permission_keys in ROLE_PERMISSIONS.items():
        role = existing_roles.get(role_name)
        if not role:
            role = Role(name=role_name, description=f"Auto-seeded role {role_name}")
            db.add(role)
            db.flush()
            existing_roles[role_name] = role
        role.description = f"Auto-seeded role {role_name}"

        for permission_key in permission_keys:
            permission = existing_permissions.get(permission_key)
            if not permission:
                permission = Permission(
                    key=permission_key,
                    description=json.dumps({"source": "bootstrap"}),
                )
                db.add(permission)
                db.flush()
                existing_permissions[permission_key] = permission
            if permission not in role.permissions:
                role.permissions.append(permission)
    db.flush()

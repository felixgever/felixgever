from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_user_role_names
from app.models.billing import BillingPlan, Subscription
from app.models.project import Project
from app.models.user import User
from app.schemas.common import SubscriptionCreate, SubscriptionRead
from app.services.audit_service import create_audit_log

router = APIRouter()


def _can_access_subscription(subscription: Subscription, current_user: User) -> bool:
    if "admin" in get_user_role_names(current_user):
        return True
    if subscription.user_id == current_user.id:
        return True
    return False


@router.get("/", response_model=list[SubscriptionRead])
def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Subscription]:
    query = select(Subscription).where(Subscription.is_deleted.is_(False))
    if "admin" not in get_user_role_names(current_user):
        query = query.where(Subscription.user_id == current_user.id)
    return list(db.scalars(query).all())


@router.post("/", response_model=SubscriptionRead, status_code=201)
def create_subscription(
    subscription_in: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Subscription:
    plan = db.get(BillingPlan, subscription_in.billing_plan_id)
    if not plan or plan.is_deleted:
        raise HTTPException(status_code=404, detail="Billing plan not found")

    if subscription_in.project_id:
        project = db.get(Project, subscription_in.project_id)
        if not project or project.is_deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        if (
            project.owner_id != current_user.id
            and "admin" not in get_user_role_names(current_user)
        ):
            raise HTTPException(status_code=403, detail="No access to project")

    if (
        subscription_in.user_id
        and subscription_in.user_id != current_user.id
        and "admin" not in get_user_role_names(current_user)
    ):
        raise HTTPException(status_code=403, detail="Cannot create subscription for another user")

    subscription = Subscription(
        billing_plan_id=subscription_in.billing_plan_id,
        user_id=subscription_in.user_id,
        project_id=subscription_in.project_id,
        status=subscription_in.status,
        auto_renew=subscription_in.auto_renew,
        add_ons_json=subscription_in.add_ons_json,
        started_at=datetime.now(tz=timezone.utc),
    )
    db.add(subscription)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="subscription",
        entity_id=str(subscription.id),
        action="create",
        after_data=subscription_in.model_dump(),
    )
    db.commit()
    db.refresh(subscription)
    return subscription


@router.post("/{subscription_id}/upgrade/{new_plan_id}", response_model=SubscriptionRead)
def upgrade_subscription(
    subscription_id: int,
    new_plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Subscription:
    subscription = db.get(Subscription, subscription_id)
    if not subscription or subscription.is_deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if not _can_access_subscription(subscription, current_user):
        raise HTTPException(status_code=403, detail="No access to subscription")

    plan = db.get(BillingPlan, new_plan_id)
    if not plan or plan.is_deleted:
        raise HTTPException(status_code=404, detail="Target plan not found")

    before = {"billing_plan_id": subscription.billing_plan_id}
    subscription.billing_plan_id = new_plan_id
    subscription.status = "active"
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="subscription",
        entity_id=str(subscription.id),
        action="upgrade_plan",
        before_data=before,
        after_data={"billing_plan_id": new_plan_id},
    )
    db.commit()
    db.refresh(subscription)
    return subscription

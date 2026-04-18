import json
from datetime import datetime, timezone

from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from app.models.billing import BillingPlan, Invoice, Subscription
from app.models.project import Project, Unit
from app.utils.constants import WORKFLOW_STAGES

BASIC_FEATURES = {
    "basic_residents",
    "basic_signatures",
    "basic_documents",
    "basic_communication",
    "basic_dashboard",
}

ADVANCED_FEATURES = {
    "tender_module",
    "planning_module",
    "feasibility_module",
    "gis_placeholder",
    "advanced_documents",
    "objections_module",
    "advanced_communication",
    "advanced_dashboard",
}

ADD_ON_FEATURES = {
    "ai_modules",
    "bulk_signatures",
    "advanced_whatsapp",
    "contract_analysis",
    "proposal_scoring",
}

PROFESSIONAL_FEATURES = {
    "planning_module",
    "feasibility_module",
    "advanced_dashboard",
}


def get_stage_index(stage: str) -> int:
    try:
        return WORKFLOW_STAGES.index(stage)
    except ValueError:
        return -1


def calculate_project_unit_cost(project: Project, unit_count: int) -> int:
    return int(project.per_unit_price_ils * max(unit_count, 0))


def get_existing_unit_count(db: Session, project_id: int) -> int:
    return len(
        db.scalars(
            select(Unit).where(and_(Unit.project_id == project_id, Unit.is_deleted.is_(False)))
        ).all()
    )


def get_project_subscription(db: Session, project_id: int) -> Subscription | None:
    return db.scalar(
        select(Subscription)
        .where(
            and_(
                Subscription.project_id == project_id,
                Subscription.status.in_(["active", "trial"]),
                Subscription.is_deleted.is_(False),
            )
        )
        .order_by(desc(Subscription.created_at))
    )


def get_user_subscription(db: Session, user_id: int) -> Subscription | None:
    return db.scalar(
        select(Subscription)
        .where(
            and_(
                Subscription.user_id == user_id,
                Subscription.status.in_(["active", "trial"]),
                Subscription.is_deleted.is_(False),
            )
        )
        .order_by(desc(Subscription.created_at))
    )


def _subscription_features(subscription: Subscription | None) -> set[str]:
    if not subscription:
        return set()
    plan_features: set[str] = set()
    if subscription.billing_plan and subscription.billing_plan.included_features_json:
        try:
            parsed = json.loads(subscription.billing_plan.included_features_json)
            if isinstance(parsed, list):
                plan_features.update(str(item) for item in parsed)
        except json.JSONDecodeError:
            pass
    if subscription.add_ons_json:
        try:
            parsed = json.loads(subscription.add_ons_json)
            if isinstance(parsed, list):
                plan_features.update(str(item) for item in parsed)
        except json.JSONDecodeError:
            pass
    return plan_features


def is_feature_allowed(
    db: Session, *, project: Project, user_id: int | None, feature_key: str
) -> tuple[bool, str | None]:
    stage_idx = get_stage_index(project.current_stage)
    before_developer_selection = stage_idx <= get_stage_index("organization")

    if feature_key in BASIC_FEATURES:
        return True, None

    project_subscription = get_project_subscription(db, project.id)
    user_subscription = get_user_subscription(db, user_id) if user_id else None
    project_features = _subscription_features(project_subscription)
    user_features = _subscription_features(user_subscription)
    has_project_feature = feature_key in project_features
    has_user_feature = feature_key in user_features
    has_feature_by_subscription = has_project_feature or has_user_feature

    if feature_key in ADVANCED_FEATURES:
        if feature_key in PROFESSIONAL_FEATURES and has_user_feature:
            return True, None
        if before_developer_selection:
            return False, "Advanced feature available only from Developer Selection stage"
        if not project_subscription:
            return False, "Project developer subscription required"
        if not has_project_feature:
            return False, "Feature not included in current project subscription"
        return True, None

    if feature_key in ADD_ON_FEATURES:
        if not has_feature_by_subscription:
            return False, "Add-on is not active"
        return True, None

    return has_feature_by_subscription, None if has_feature_by_subscription else "Feature blocked"


def ensure_developer_selection_lock(project: Project) -> bool:
    return get_stage_index(project.current_stage) >= get_stage_index("developer_selection")


def create_project_subscription_invoice(db: Session, subscription: Subscription) -> Invoice:
    if not subscription.project_id:
        raise ValueError("Project subscription required")
    project = db.get(Project, subscription.project_id)
    if not project:
        raise ValueError("Project not found")

    unit_count = get_existing_unit_count(db, project.id)
    amount = calculate_project_unit_cost(project, unit_count)
    invoice = Invoice(
        subscription_id=subscription.id,
        amount_ils=amount,
        status="issued",
        currency="ILS",
        issued_at=datetime.now(tz=timezone.utc),
        line_items_json=json.dumps(
            [
                {
                    "type": "per_unit",
                    "units": unit_count,
                    "unit_price_ils": project.per_unit_price_ils,
                    "amount_ils": amount,
                }
            ]
        ),
    )
    db.add(invoice)
    db.flush()
    return invoice


def seed_default_billing_plans(db: Session) -> None:
    existing = db.scalars(select(BillingPlan)).all()
    if existing:
        return

    plans = [
        BillingPlan(
            code="freemium-organizer",
            name="Freemium Organizer",
            plan_type="freemium",
            monthly_price_ils=0,
            per_unit_price_ils=0,
            included_features_json=json.dumps(sorted(BASIC_FEATURES)),
        ),
        BillingPlan(
            code="developer-per-unit",
            name="Developer Per Unit",
            plan_type="developer_project",
            monthly_price_ils=0,
            per_unit_price_ils=30,
            included_features_json=json.dumps(sorted(ADVANCED_FEATURES)),
        ),
        BillingPlan(
            code="professional-monthly",
            name="Professional Monthly",
            plan_type="professional_user",
            monthly_price_ils=99,
            per_unit_price_ils=0,
            included_features_json=json.dumps(
                sorted({"advanced_dashboard", "planning_module", "feasibility_module"})
            ),
        ),
    ]
    db.add_all(plans)
    db.flush()

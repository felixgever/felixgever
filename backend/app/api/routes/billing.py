from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, get_user_role_names
from app.billing.logic import (
    calculate_project_unit_cost,
    create_project_subscription_invoice,
    get_existing_unit_count,
    seed_default_billing_plans,
)
from app.models.billing import BillingPlan, Invoice, Payment, Subscription
from app.models.project import Project
from app.models.user import User
from app.schemas.common import (
    BillingPlanCreate,
    BillingPlanRead,
    InvoiceCreate,
    InvoiceRead,
    PaymentCreate,
    PaymentRead,
)
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.post("/seed-plans", response_model=list[BillingPlanRead])
def seed_plans(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[BillingPlan]:
    seed_default_billing_plans(db)
    db.commit()
    return list(db.scalars(select(BillingPlan).where(BillingPlan.is_deleted.is_(False))).all())


@router.get("/plans", response_model=list[BillingPlanRead])
def list_billing_plans(db: Session = Depends(get_db)) -> list[BillingPlan]:
    return list(db.scalars(select(BillingPlan).where(BillingPlan.is_deleted.is_(False))).all())


@router.post("/plans", response_model=BillingPlanRead, status_code=201)
def create_billing_plan(
    plan_in: BillingPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BillingPlan:
    if "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    exists = db.scalar(select(BillingPlan).where(BillingPlan.code == plan_in.code))
    if exists:
        raise HTTPException(status_code=400, detail="Plan code already exists")
    plan = BillingPlan(**plan_in.model_dump())
    db.add(plan)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="billing_plan",
        entity_id=str(plan.id),
        action="create",
        after_data=plan_in.model_dump(),
    )
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/projects/{project_id}/estimate")
def estimate_project_cost(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    project = db.get(Project, project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    unit_count = get_existing_unit_count(db, project.id)
    total = calculate_project_unit_cost(project, unit_count)
    return {
        "project_id": project.id,
        "unit_count": unit_count,
        "per_unit_price_ils": project.per_unit_price_ils,
        "estimated_total_ils": total,
    }


@router.post("/invoices", response_model=InvoiceRead, status_code=201)
def create_invoice(
    invoice_in: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Invoice:
    subscription = db.get(Subscription, invoice_in.subscription_id)
    if not subscription or subscription.is_deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="Admin only")

    invoice = Invoice(
        subscription_id=invoice_in.subscription_id,
        amount_ils=invoice_in.amount_ils,
        due_at=invoice_in.due_at,
        line_items_json=invoice_in.line_items_json,
        status="issued",
        issued_at=datetime.now(tz=timezone.utc),
    )
    db.add(invoice)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="invoice",
        entity_id=str(invoice.id),
        action="create",
        after_data={"amount_ils": invoice.amount_ils},
    )
    db.commit()
    db.refresh(invoice)
    return invoice


@router.post("/subscriptions/{subscription_id}/generate-invoice", response_model=InvoiceRead)
def generate_project_invoice(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Invoice:
    if "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    subscription = db.get(Subscription, subscription_id)
    if not subscription or subscription.is_deleted:
        raise HTTPException(status_code=404, detail="Subscription not found")
    invoice = create_project_subscription_invoice(db, subscription)
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="invoice",
        entity_id=str(invoice.id),
        action="generate_project_invoice",
    )
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/invoices", response_model=list[InvoiceRead])
def list_invoices(
    subscription_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Invoice]:
    query = select(Invoice).where(Invoice.is_deleted.is_(False))
    if subscription_id:
        query = query.where(Invoice.subscription_id == subscription_id)
    if "admin" not in get_user_role_names(current_user):
        query = query.join(Subscription, Invoice.subscription_id == Subscription.id).where(
            Subscription.user_id == current_user.id
        )
    return list(db.scalars(query).all())


@router.post("/payments", response_model=PaymentRead, status_code=201)
def create_payment(
    payment_in: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Payment:
    invoice = db.get(Invoice, payment_in.invoice_id)
    if not invoice or invoice.is_deleted:
        raise HTTPException(status_code=404, detail="Invoice not found")

    payment = Payment(
        invoice_id=payment_in.invoice_id,
        amount_ils=payment_in.amount_ils,
        provider=payment_in.provider,
        status="paid",
        paid_at=datetime.now(tz=timezone.utc),
        transaction_ref=f"mock-tx-{invoice.id}-{int(datetime.now(tz=timezone.utc).timestamp())}",
    )
    invoice.status = "paid"
    invoice.paid_at = payment.paid_at
    db.add(payment)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="payment",
        entity_id=str(payment.id),
        action="create",
        after_data={"invoice_id": payment.invoice_id, "amount_ils": payment.amount_ils},
    )
    db.commit()
    db.refresh(payment)
    return payment

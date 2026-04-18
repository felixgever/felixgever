from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class PermissionRead(ORMBaseSchema):
    id: int
    key: str
    description: str | None = None


class RoleRead(ORMBaseSchema):
    id: int
    name: str
    description: str | None = None
    permissions: list[PermissionRead] = []


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    organization_name: str | None = None
    roles: list[str] = []


class UserRead(ORMBaseSchema):
    id: int
    email: EmailStr
    full_name: str
    organization_name: str | None = None
    is_active: bool
    roles: list[RoleRead] = []
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = None
    organization_name: str | None = None
    is_active: bool | None = None


class ProjectCreate(BaseModel):
    name: str
    city: str
    address: str | None = None
    description: str | None = None
    per_unit_price_ils: int = 30


class ProjectUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    address: str | None = None
    description: str | None = None
    current_stage: str | None = None
    per_unit_price_ils: int | None = None


class UnitCreate(BaseModel):
    project_id: int
    unit_number: str
    floor: int | None = None
    existing_area_sqm: int | None = None


class UnitRead(ORMBaseSchema):
    id: int
    project_id: int
    unit_number: str
    floor: int | None = None
    existing_area_sqm: int | None = None
    residents_count: int


class ProjectRead(ORMBaseSchema):
    id: int
    name: str
    city: str
    address: str | None = None
    description: str | None = None
    owner_id: int
    current_stage: str
    developer_payment_required: bool
    per_unit_price_ils: int
    is_active: bool
    created_at: datetime
    units: list[UnitRead] = []


class ResidentCreate(BaseModel):
    project_id: int
    unit_id: int | None = None
    full_name: str
    phone: str | None = None
    email: EmailStr | None = None
    id_number: str | None = None
    is_primary_contact: bool = False


class ResidentUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    consent_status: str | None = None


class ResidentRead(ORMBaseSchema):
    id: int
    project_id: int
    unit_id: int | None = None
    full_name: str
    phone: str | None = None
    email: EmailStr | None = None
    is_primary_contact: bool
    consent_status: str


class SignatureCreate(BaseModel):
    project_id: int
    resident_id: int
    signature_provider: str = "mock-provider"


class SignatureRead(ORMBaseSchema):
    id: int
    project_id: int
    resident_id: int
    signature_provider: str
    external_reference: str | None = None
    status: str
    signed_at: datetime | None = None


class SignatureStatusUpdate(BaseModel):
    status: str
    external_reference: str | None = None


class DocumentCreate(BaseModel):
    project_id: int
    title: str
    category: str = "general"
    storage_key: str
    mime_type: str | None = None
    visibility: str = "project"
    metadata_json: str | None = None


class DocumentRead(ORMBaseSchema):
    id: int
    project_id: int
    title: str
    category: str
    storage_key: str
    mime_type: str | None = None
    visibility: str
    metadata_json: str | None = None


class WorkflowStageCreate(BaseModel):
    project_id: int
    stage_key: str
    status: str = "pending"
    notes: str | None = None


class WorkflowStageRead(ORMBaseSchema):
    id: int
    project_id: int
    stage_key: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: str | None = None
    assignee_id: int | None = None
    status: str = "todo"


class TaskRead(ORMBaseSchema):
    id: int
    project_id: int
    title: str
    description: str | None = None
    assignee_id: int | None = None
    status: str


class DeveloperBidCreate(BaseModel):
    project_id: int
    developer_name: str
    proposal_summary: str | None = None
    price_offer_ils: int | None = None


class DeveloperBidRead(ORMBaseSchema):
    id: int
    project_id: int
    developer_name: str
    proposal_summary: str | None = None
    score: int | None = None
    price_offer_ils: int | None = None
    status: str


class PlanCreate(BaseModel):
    project_id: int
    name: str
    zoning_status: str = "draft"
    feasibility_score: int | None = None
    assumptions_json: str | None = None


class PlanRead(ORMBaseSchema):
    id: int
    project_id: int
    name: str
    zoning_status: str
    feasibility_score: int | None = None
    assumptions_json: str | None = None


class MessageCreate(BaseModel):
    project_id: int
    channel: str = "email"
    recipient: str
    body: str


class MessageRead(ORMBaseSchema):
    id: int
    project_id: int
    sender_id: int
    channel: str
    recipient: str
    body: str
    delivery_status: str
    external_message_id: str | None = None


class BillingPlanCreate(BaseModel):
    code: str
    name: str
    plan_type: str
    monthly_price_ils: int = 0
    per_unit_price_ils: int = 0
    included_features_json: str | None = None


class BillingPlanRead(ORMBaseSchema):
    id: int
    code: str
    name: str
    plan_type: str
    monthly_price_ils: int
    per_unit_price_ils: int
    included_features_json: str | None = None
    is_active: bool


class SubscriptionCreate(BaseModel):
    billing_plan_id: int
    user_id: int | None = None
    project_id: int | None = None
    status: str = "active"
    auto_renew: bool = True
    add_ons_json: str | None = None


class SubscriptionRead(ORMBaseSchema):
    id: int
    billing_plan_id: int
    user_id: int | None = None
    project_id: int | None = None
    status: str
    started_at: datetime
    ends_at: datetime | None = None
    auto_renew: bool
    add_ons_json: str | None = None


class InvoiceRead(ORMBaseSchema):
    id: int
    subscription_id: int
    amount_ils: int
    currency: str
    status: str
    issued_at: datetime
    due_at: datetime | None = None
    paid_at: datetime | None = None
    line_items_json: str | None = None


class PaymentCreate(BaseModel):
    invoice_id: int
    amount_ils: int
    provider: str = "mock-gateway"


class PaymentRead(ORMBaseSchema):
    id: int
    invoice_id: int
    amount_ils: int
    provider: str
    status: str
    transaction_ref: str | None = None
    paid_at: datetime | None = None


class InvoiceCreate(BaseModel):
    subscription_id: int
    amount_ils: int
    due_at: datetime | None = None
    line_items_json: str | None = None


class FeatureGateResult(BaseModel):
    allowed: bool
    reason: str | None = None
    metadata: dict[str, Any] = {}


class AuditLogRead(ORMBaseSchema):
    id: int
    actor_id: int | None = None
    entity_type: str
    entity_id: str
    action: str
    before_json: str | None = None
    after_json: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime

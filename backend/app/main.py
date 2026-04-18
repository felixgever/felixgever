from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    audit,
    auth,
    bids,
    billing,
    documents,
    messages,
    plans,
    projects,
    residents,
    signatures,
    subscriptions,
    users,
    workflow,
)
from app.billing.logic import seed_default_billing_plans
from app.core.bootstrap import seed_roles_permissions
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # For local/demo bootstrap. In production, prefer Alembic migrations only.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_roles_permissions(db)
        seed_default_billing_plans(db)
        db.commit()
    finally:
        db.close()


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(residents.router, prefix="/residents", tags=["residents"])
app.include_router(signatures.router, prefix="/signatures", tags=["signatures"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
app.include_router(bids.router, prefix="/bids", tags=["bids"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(audit.router, prefix="/audit", tags=["audit"])

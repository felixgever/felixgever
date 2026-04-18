from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    enforce_feature_for_project,
    get_current_user,
    get_db,
    get_user_role_names,
)
from app.models.project import DeveloperBid, Project
from app.models.user import User
from app.schemas.common import DeveloperBidCreate, DeveloperBidRead
from app.services.audit_service import create_audit_log

router = APIRouter()


@router.get("/", response_model=list[DeveloperBidRead])
def list_bids(
    project_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeveloperBid]:
    return list(
        db.scalars(
            select(DeveloperBid).where(
                DeveloperBid.project_id == project_id,
                DeveloperBid.is_deleted.is_(False),
            )
        ).all()
    )


@router.post("/", response_model=DeveloperBidRead, status_code=201)
def create_bid(
    bid_in: DeveloperBidCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeveloperBid:
    project = db.get(Project, bid_in.project_id)
    if not project or project.is_deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to project")
    enforce_feature_for_project(
        db=db,
        current_user=current_user,
        project=project,
        feature_key="tender_module",
    )

    bid = DeveloperBid(**bid_in.model_dump())
    db.add(bid)
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="developer_bid",
        entity_id=str(bid.id),
        action="create",
        after_data=bid_in.model_dump(),
    )
    db.commit()
    db.refresh(bid)
    return bid


@router.post("/{bid_id}/score/{score}", response_model=DeveloperBidRead)
def score_bid(
    bid_id: int,
    score: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeveloperBid:
    bid = db.get(DeveloperBid, bid_id)
    if not bid or bid.is_deleted:
        raise HTTPException(status_code=404, detail="Bid not found")
    project = db.get(Project, bid.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and "admin" not in get_user_role_names(current_user):
        raise HTTPException(status_code=403, detail="No access to bid")
    enforce_feature_for_project(
        db=db,
        current_user=current_user,
        project=project,
        feature_key="proposal_scoring",
    )

    bid.score = max(0, min(score, 100))
    db.flush()
    create_audit_log(
        db,
        actor_id=current_user.id,
        entity_type="developer_bid",
        entity_id=str(bid.id),
        action="score",
        after_data={"score": bid.score},
    )
    db.commit()
    db.refresh(bid)
    return bid

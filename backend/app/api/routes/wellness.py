"""
Wellness Routes – personalized recommendations and wellness plan management.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.wellness import WellnessPlan
from app.schemas.wellness import (
    WellnessPlanCreate, WellnessPlanUpdate,
    WellnessPlanResponse, WellnessRecommendations,
)
from app.services.wellness_service import wellness_service

router = APIRouter()


@router.get("/recommendations", response_model=WellnessRecommendations)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await wellness_service.get_recommendations(db, current_user.id)
    return WellnessRecommendations(**result)


@router.post("/plans", response_model=WellnessPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: WellnessPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    plan_data = await wellness_service.generate_plan(db, current_user.id, data.plan_type)
    plan = WellnessPlan(
        user_id=current_user.id, plan_type=data.plan_type,
        goals=plan_data["goals"], recommendations=plan_data["recommendations"],
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return WellnessPlanResponse.model_validate(plan)


@router.get("/plans", response_model=list[WellnessPlanResponse])
async def list_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WellnessPlan)
        .where(WellnessPlan.user_id == current_user.id)
        .order_by(WellnessPlan.created_at.desc())
    )
    return [WellnessPlanResponse.model_validate(p) for p in result.scalars().all()]


@router.put("/plans/{plan_id}", response_model=WellnessPlanResponse)
async def update_plan(
    plan_id: UUID, data: WellnessPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WellnessPlan).where(
            WellnessPlan.id == plan_id, WellnessPlan.user_id == current_user.id
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if data.progress is not None:
        plan.progress = data.progress
    if data.status is not None:
        plan.status = data.status
    await db.flush()
    await db.refresh(plan)
    return WellnessPlanResponse.model_validate(plan)

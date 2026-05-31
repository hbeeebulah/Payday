"""CRUD routes for businesses (employers)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Business
from app.schemas.business import BusinessCreate, BusinessRead, BusinessUpdate

router = APIRouter(prefix="/businesses", tags=["businesses"])


async def _get_or_404(db: AsyncSession, business_id: str) -> Business:
    business = await db.get(Business, business_id)
    if business is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


@router.post("", response_model=BusinessRead, status_code=status.HTTP_201_CREATED)
async def create_business(
    payload: BusinessCreate,
    db: AsyncSession = Depends(get_db),
) -> Business:
    business = Business(**payload.model_dump())
    db.add(business)
    await db.commit()
    await db.refresh(business)
    return business


@router.get("", response_model=list[BusinessRead])
async def list_businesses(db: AsyncSession = Depends(get_db)) -> list[Business]:
    result = await db.execute(select(Business).order_by(Business.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{business_id}", response_model=BusinessRead)
async def get_business(business_id: str, db: AsyncSession = Depends(get_db)) -> Business:
    return await _get_or_404(db, business_id)


@router.patch("/{business_id}", response_model=BusinessRead)
async def update_business(
    business_id: str,
    payload: BusinessUpdate,
    db: AsyncSession = Depends(get_db),
) -> Business:
    business = await _get_or_404(db, business_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(business, field, value)
    await db.commit()
    await db.refresh(business)
    return business


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(business_id: str, db: AsyncSession = Depends(get_db)) -> Response:
    business = await _get_or_404(db, business_id)
    await db.delete(business)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

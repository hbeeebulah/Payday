"""CRUD routes for employees, scoped under a business."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Business, Employee
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate

router = APIRouter(prefix="/businesses/{business_id}/employees", tags=["employees"])


async def _ensure_business(db: AsyncSession, business_id: str) -> Business:
    business = await db.get(Business, business_id)
    if business is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


async def _get_employee_or_404(
    db: AsyncSession, business_id: str, employee_id: str
) -> Employee:
    employee = await db.get(Employee, employee_id)
    if employee is None or employee.business_id != business_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
async def create_employee(
    business_id: str,
    payload: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    await _ensure_business(db, business_id)
    employee = Employee(business_id=business_id, **payload.model_dump())
    db.add(employee)
    await db.commit()
    await db.refresh(employee)
    return employee


@router.get("", response_model=list[EmployeeRead])
async def list_employees(
    business_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[Employee]:
    await _ensure_business(db, business_id)
    result = await db.execute(
        select(Employee)
        .where(Employee.business_id == business_id)
        .order_by(Employee.last_name, Employee.first_name)
    )
    return list(result.scalars().all())


@router.get("/{employee_id}", response_model=EmployeeRead)
async def get_employee(
    business_id: str,
    employee_id: str,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    return await _get_employee_or_404(db, business_id, employee_id)


@router.patch("/{employee_id}", response_model=EmployeeRead)
async def update_employee(
    business_id: str,
    employee_id: str,
    payload: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
) -> Employee:
    employee = await _get_employee_or_404(db, business_id, employee_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    await db.commit()
    await db.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    business_id: str,
    employee_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    employee = await _get_employee_or_404(db, business_id, employee_id)
    await db.delete(employee)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

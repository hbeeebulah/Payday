"""Pydantic schemas for the Employee resource."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import EmployeeStatus


class EmployeeBase(BaseModel):
    first_name: str = Field(..., max_length=128)
    last_name: str = Field(..., max_length=128)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    role: str = Field(..., max_length=128)
    department: str | None = Field(default=None, max_length=128)
    salary: Decimal = Field(..., ge=0)
    currency: str = Field(default="NGN", max_length=3)
    bank_name: str | None = Field(default=None, max_length=128)
    bank_account_number: str = Field(..., max_length=32)
    bank_account_name: str | None = Field(default=None, max_length=255)
    bank_routing_code: str = Field(..., max_length=32)
    status: EmployeeStatus = EmployeeStatus.ACTIVE


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=128)
    last_name: str | None = Field(default=None, max_length=128)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    role: str | None = Field(default=None, max_length=128)
    department: str | None = Field(default=None, max_length=128)
    salary: Decimal | None = Field(default=None, ge=0)
    bank_name: str | None = Field(default=None, max_length=128)
    bank_account_number: str | None = Field(default=None, max_length=32)
    bank_account_name: str | None = Field(default=None, max_length=255)
    bank_routing_code: str | None = Field(default=None, max_length=32)
    status: EmployeeStatus | None = None


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    business_id: str
    created_at: datetime
    updated_at: datetime

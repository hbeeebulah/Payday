"""Pydantic schemas for the Business resource."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BusinessBase(BaseModel):
    name: str = Field(..., max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    registration_number: str | None = Field(default=None, max_length=64)
    industry: str | None = Field(default=None, max_length=128)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=512)
    country: str = Field(default="NG", max_length=2)
    alatpay_business_id: str | None = Field(default=None, max_length=128)


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    legal_name: str | None = Field(default=None, max_length=255)
    registration_number: str | None = Field(default=None, max_length=64)
    industry: str | None = Field(default=None, max_length=128)
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=512)
    alatpay_business_id: str | None = Field(default=None, max_length=128)


class BusinessRead(BusinessBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime

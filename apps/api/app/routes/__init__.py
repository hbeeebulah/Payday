"""API route registration."""

from fastapi import APIRouter

from app.routes import businesses, employees, health, payroll, webhooks

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(businesses.router)
api_router.include_router(employees.router)
api_router.include_router(payroll.router)
api_router.include_router(webhooks.router)

__all__ = ["api_router"]

"""API route registration."""

from fastapi import APIRouter

from app.routes import (
    analytics,
    auth,
    businesses,
    employees,
    health,
    payroll,
    wallets,
    webhooks,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(businesses.router)
api_router.include_router(employees.router)
api_router.include_router(wallets.router)
api_router.include_router(payroll.router)
api_router.include_router(analytics.router)
api_router.include_router(webhooks.router)

__all__ = ["api_router"]

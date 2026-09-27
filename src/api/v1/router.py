"""AssureX Claim Engine - API v1 Router

Mounts all endpoint modules under /api/v1
"""

from fastapi import APIRouter

from src.api.v1 import (
    auth,
    users,
    products,
    warranties,
    claims,
    documents,
    predictions,
    reviews,
    notifications,
    dashboard,
    analytics,
    reports,
    admin,
    repairs,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, tags=["Users"])
api_router.include_router(products.router, tags=["Products"])
api_router.include_router(warranties.router, tags=["Warranties"])
api_router.include_router(claims.router, tags=["Claims"])
api_router.include_router(documents.router, tags=["Documents"])
api_router.include_router(predictions.router, tags=["Predictions"])
api_router.include_router(reviews.router, tags=["Reviews"])
api_router.include_router(notifications.router, tags=["Notifications"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(analytics.router, tags=["Analytics"])
api_router.include_router(reports.router, tags=["Reports"])
api_router.include_router(admin.router, tags=["Admin"])
api_router.include_router(repairs.router)
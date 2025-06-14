from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    financials,
    analytics,
    ratios,
    charts,
    insights,
    compliance,
    auth,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    financials.router,
    prefix="/financials",
    tags=["Financial Statements"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Financial Analytics"]
)

api_router.include_router(
    ratios.router,
    prefix="/ratios",
    tags=["Financial Ratios"]
)

api_router.include_router(
    charts.router,
    prefix="/charts",
    tags=["Charts & Visualizations"]
)

api_router.include_router(
    insights.router,
    prefix="/insights",
    tags=["AI Insights"]
)

api_router.include_router(
    compliance.router,
    prefix="/compliance",
    tags=["Compliance & ESG"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

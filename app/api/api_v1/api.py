from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    financials,
    analytics,
    ratios,
    charts,
    insights,
    compliance,
    auth,
    dividends,
    portfolio,
    query
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

api_router.include_router(
    dividends.router,
    prefix="/dividends",
    tags=["Dividend Analysis"]
)

api_router.include_router(
    portfolio.router,
    prefix="/portfolio",
    tags=["Portfolio Optimization"]
)

api_router.include_router(
    query.router,
    prefix="/query",
    tags=["Natural Language Query"]
)

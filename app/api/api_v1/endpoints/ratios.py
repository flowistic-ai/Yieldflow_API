"""
Financial ratios endpoints
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.deps import require_basic_financials

router = APIRouter()


@router.get("/calculate/{symbol}")
async def calculate_ratios(
    symbol: str,
    user: Dict[str, Any] = Depends(require_basic_financials)
):
    """Calculate financial ratios for a symbol"""
    # TODO: Implement ratios calculation
    return {
        "symbol": symbol,
        "message": "Ratios endpoint - coming soon",
        "user_plan": user.get("plan", "unknown")
    }


@router.get("/health")
async def ratios_health():
    """Health check for ratios module"""
    return {"status": "healthy", "module": "ratios"}

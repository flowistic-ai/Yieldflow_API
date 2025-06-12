"""
Compliance and ESG endpoints
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.deps import require_compliance

router = APIRouter()


@router.get("/esg/{symbol}")
async def get_esg_data(
    symbol: str,
    user: Dict[str, Any] = Depends(require_compliance)
):
    """Get ESG compliance data for a symbol"""
    # TODO: Implement ESG data retrieval
    return {
        "symbol": symbol,
        "message": "ESG/Compliance endpoint - coming soon",
        "user_plan": user.get("plan", "unknown")
    }


@router.get("/health")
async def compliance_health():
    """Health check for compliance module"""
    return {"status": "healthy", "module": "compliance"}

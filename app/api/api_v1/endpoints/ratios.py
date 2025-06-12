"""
Financial ratios endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, Optional

from app.core.deps import require_basic_financials
from app.services.data_provider import DataProvider
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.ratio_calculator import RatioCalculator
from app.services.cache_service import CacheService
from app.utils.exceptions import TickerNotFoundError, ValidationError

router = APIRouter()


@router.get("/calculate/{symbol}")
async def calculate_ratios(
    symbol: str,
    period: str = Query("annual", description="Period type: annual or quarterly"),
    limit: int = Query(4, description="Number of periods to return", ge=1, le=10),
    user: Dict[str, Any] = Depends(require_basic_financials),
    cache_service: CacheService = Depends(),
    data_provider: DataProvider = Depends(),
    analyzer: FinancialAnalyzer = Depends(),
    ratio_calculator: RatioCalculator = Depends()
):
    """Calculate comprehensive financial ratios for a symbol"""
    
    # Check cache first (with version to invalidate old cache)
    cache_key = f"ratios_v2_{symbol}_{period}_{limit}"
    cached_data = await cache_service.get_financial_data(symbol, f"ratios_v2_{period}")
    
    if cached_data:
        return cached_data
    
    try:
        # Fetch financial data
        income_statements = await data_provider.get_income_statements(
            ticker=symbol, period=period, limit=limit
        )
        balance_sheets = await data_provider.get_balance_sheets(
            ticker=symbol, period=period, limit=limit
        )
        cash_flows = await data_provider.get_cash_flows(
            ticker=symbol, period=period, limit=limit
        )
        
        if not income_statements:
            raise TickerNotFoundError(symbol)
        
        # Calculate comprehensive ratios using RatioCalculator
        comprehensive_ratios = await ratio_calculator.calculate_all_ratios(
            income_statements, balance_sheets, cash_flows
        )
        
        all_ratios = comprehensive_ratios.get("ratios", {})
        
        # Extract profitability ratios (handle both nested and flat structures)
        profitability_data = all_ratios.get("profitability", {})
        if "ratios" in profitability_data:
            profitability_data = profitability_data["ratios"]
        
        profitability_ratios = {
            "gross_margin": (profitability_data.get("gross_margin") * 100) if profitability_data.get("gross_margin") else None,
            "operating_margin": (profitability_data.get("operating_margin") * 100) if profitability_data.get("operating_margin") else None,
            "net_margin": (profitability_data.get("net_margin") * 100) if profitability_data.get("net_margin") else None,
            "return_on_assets": (profitability_data.get("return_on_assets") * 100) if profitability_data.get("return_on_assets") else None,
            "return_on_equity": (profitability_data.get("return_on_equity") * 100) if profitability_data.get("return_on_equity") else None,
            "return_on_invested_capital": (profitability_data.get("return_on_invested_capital") * 100) if profitability_data.get("return_on_invested_capital") else None
        }
        
        # Calculate EPS growth using analyzer (if available)
        analyzer_profitability = await analyzer.calculate_profitability_ratios(income_statements)
        profitability_ratios["eps_growth"] = analyzer_profitability.get("eps_growth")
        
        # Extract liquidity ratios
        liquidity_data = all_ratios.get("liquidity", {})
        if "ratios" in liquidity_data:
            liquidity_data = liquidity_data["ratios"]
            
        liquidity_ratios = {
            "current_ratio": liquidity_data.get("current_ratio"),
            "quick_ratio": liquidity_data.get("quick_ratio"),
            "cash_ratio": liquidity_data.get("cash_ratio"),
            "working_capital": liquidity_data.get("working_capital"),
            "operating_cash_flow_ratio": liquidity_data.get("operating_cash_flow_ratio")
        }
        
        # Extract solvency/leverage ratios
        leverage_data = all_ratios.get("leverage", {})
        if "ratios" in leverage_data:
            leverage_data = leverage_data["ratios"]
            
        solvency_ratios = {
            "debt_to_equity": leverage_data.get("debt_to_equity"),
            "debt_to_assets": leverage_data.get("debt_to_assets"),
            "equity_ratio": leverage_data.get("equity_ratio"),
            "debt_to_capital": leverage_data.get("debt_to_capital"),
            "long_term_debt_to_equity": leverage_data.get("long_term_debt_to_equity")
        }
        
        # Calculate interest coverage separately if needed
        if income_statements:
            latest_income = income_statements[0]
            operating_income = latest_income.get("operating_income")
            interest_expense = latest_income.get("interest_expense")
            if operating_income and interest_expense and interest_expense > 0:
                solvency_ratios["interest_coverage"] = operating_income / interest_expense
            else:
                solvency_ratios["interest_coverage"] = None
        
        # Extract efficiency ratios
        efficiency_data = all_ratios.get("efficiency", {})
        if "ratios" in efficiency_data:
            efficiency_data = efficiency_data["ratios"]
        efficiency_ratios = efficiency_data
        
        # Calculate cash flow ratios
        cash_flow_ratios = {}
        if cash_flows:
            latest_cf = cash_flows[0]
            latest_income = income_statements[0] if income_statements else {}
            
            operating_cf = latest_cf.get("operating_cash_flow")
            capex = latest_cf.get("capital_expenditures", 0)
            revenue = latest_income.get("revenue", 1)
            
            # Calculate free cash flow
            free_cf = None
            if operating_cf is not None and capex is not None:
                free_cf = operating_cf - abs(capex)
            
            # Calculate FCF margin
            fcf_margin = None
            if free_cf is not None and revenue > 0:
                fcf_margin = (free_cf / revenue) * 100
            
            cash_flow_ratios = {
                "operating_cash_flow": operating_cf,
                "free_cash_flow": free_cf,
                "fcf_margin": fcf_margin,
                "cash_flow_score": 8.5 if operating_cf and operating_cf > 0 else 5.0
            }
        
        # Compile comprehensive response
        response = {
            "symbol": symbol,
            "period": period,
            "profitability_ratios": profitability_ratios,
            "liquidity_ratios": liquidity_ratios,
            "solvency_ratios": solvency_ratios,
            "efficiency_ratios": efficiency_ratios,
            "cash_flow_ratios": cash_flow_ratios,
            "data_completeness": {
                "income_statements": len(income_statements),
                "balance_sheets": len(balance_sheets),
                "cash_flows": len(cash_flows)
            },
            "ratio_scores": comprehensive_ratios.get("scores", {}),
            "user_plan": user.get("plan", "unknown")
        }
        
        # Cache the response with new version key
        await cache_service.cache_financial_data(symbol, f"ratios_v2_{period}", response)
        
        return response
        
    except Exception as e:
        if isinstance(e, (TickerNotFoundError, ValidationError)):
            raise e
        raise HTTPException(status_code=500, detail=f"Error calculating ratios: {str(e)}")


@router.get("/health")
async def ratios_health():
    """Health check for ratios module"""
    return {"status": "healthy", "module": "ratios"}

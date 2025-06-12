from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List, Dict, Any
from datetime import date

from app.core.deps import get_current_user, require_basic_financials
from app.schemas.financial import (
    FinancialDataRequest,
    FinancialStatementsResponse,
    IncomeStatementResponse,
    BalanceSheetResponse,
    CashFlowStatementResponse
)
from app.services.data_provider import DataProvider
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.cache_service import CacheService
from app.utils.exceptions import TickerNotFoundError, ValidationError

router = APIRouter()


@router.get("/health")
async def financials_health():
    """Health check for financials module"""
    return {"status": "healthy", "module": "financials"}


@router.get(
    "/income-statements",
    response_model=Dict[str, Any],
    summary="Get Income Statements with Analytics",
    description="Fetch income statements with enhanced analysis including trends and key ratios"
)
async def get_income_statements(
    ticker: str = Query(..., description="Stock ticker symbol"),
    period: str = Query("annual", description="Period type: annual or quarterly"),
    limit: int = Query(4, description="Number of periods to return", ge=1, le=20),
    report_period_gte: Optional[date] = Query(None, description="Report period >= date"),
    report_period_lte: Optional[date] = Query(None, description="Report period <= date"),
    user: Dict[str, Any] = Depends(require_basic_financials),
    cache_service: CacheService = Depends(),
    data_provider: DataProvider = Depends(),
    analyzer: FinancialAnalyzer = Depends()
):
    """Get income statements with enhanced analytics"""
    
    # Check cache first
    cache_key = f"income_statements_{ticker}_{period}_{limit}"
    cached_data = await cache_service.get_financial_data(ticker, f"income_{period}")
    
    if cached_data:
        return cached_data
    
    try:
        # Fetch income statement data
        income_statements = await data_provider.get_income_statements(
            ticker=ticker,
            period=period,
            limit=limit,
            period_gte=report_period_gte,
            period_lte=report_period_lte
        )
        
        if not income_statements:
            raise TickerNotFoundError(ticker)
        
        # Perform enhanced analysis
        analysis_summary = await analyzer.analyze_income_trends(income_statements)
        key_ratios = await analyzer.calculate_profitability_ratios(income_statements)
        
        # Construct response
        response = {
            "ticker": ticker,
            "period": period,
            "income_statements": income_statements,
            "analysis_summary": {
                "revenue_trend": analysis_summary.get("revenue_trend", "stable"),
                "profit_margin_trend": analysis_summary.get("margin_trend", "stable"),
                "growth_rate_3y": analysis_summary.get("revenue_cagr_3y", 0.0),
                "earnings_quality": analysis_summary.get("earnings_quality", "medium")
            },
            "key_ratios": {
                "gross_margin": key_ratios.get("gross_margin"),
                "operating_margin": key_ratios.get("operating_margin"),
                "net_margin": key_ratios.get("net_margin"),
                "eps_growth": key_ratios.get("eps_growth")
            },
            "data_quality": {
                "completeness_score": analysis_summary.get("data_completeness", 0.8),
                "confidence_level": analysis_summary.get("confidence", 0.9),
                "last_updated": analysis_summary.get("last_updated")
            }
        }
        
        # Cache the response
        await cache_service.cache_financial_data(ticker, f"income_{period}", response)
        
        return response
        
    except Exception as e:
        if isinstance(e, (TickerNotFoundError, ValidationError)):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching income statements: {str(e)}")


@router.get(
    "/balance-sheets",
    response_model=Dict[str, Any],
    summary="Get Balance Sheets with Liquidity Analysis",
    description="Fetch balance sheets with enhanced liquidity and solvency analysis"
)
async def get_balance_sheets(
    ticker: str = Query(..., description="Stock ticker symbol"),
    period: str = Query("annual", description="Period type: annual or quarterly"),
    limit: int = Query(4, description="Number of periods to return", ge=1, le=20),
    report_period_gte: Optional[date] = Query(None, description="Report period >= date"),
    report_period_lte: Optional[date] = Query(None, description="Report period <= date"),
    user: Dict[str, Any] = Depends(require_basic_financials),
    cache_service: CacheService = Depends(),
    data_provider: DataProvider = Depends(),
    analyzer: FinancialAnalyzer = Depends()
):
    """Get balance sheets with enhanced analysis"""
    
    # Check cache first
    cached_data = await cache_service.get_financial_data(ticker, f"balance_{period}")
    
    if cached_data:
        return cached_data
    
    try:
        # Fetch balance sheet data
        balance_sheets = await data_provider.get_balance_sheets(
            ticker=ticker,
            period=period,
            limit=limit,
            period_gte=report_period_gte,
            period_lte=report_period_lte
        )
        
        if not balance_sheets:
            raise TickerNotFoundError(ticker)
        
        # Perform enhanced analysis
        liquidity_analysis = await analyzer.analyze_liquidity(balance_sheets)
        solvency_analysis = await analyzer.analyze_solvency(balance_sheets)
        
        # Construct response
        response = {
            "ticker": ticker,
            "period": period,
            "balance_sheets": balance_sheets,
            "liquidity_analysis": {
                "current_ratio": liquidity_analysis.get("current_ratio"),
                "quick_ratio": liquidity_analysis.get("quick_ratio"),
                "cash_ratio": liquidity_analysis.get("cash_ratio"),
                "working_capital": liquidity_analysis.get("working_capital"),
                "liquidity_score": liquidity_analysis.get("score", 5.0),
                "assessment": liquidity_analysis.get("assessment", "adequate")
            },
            "solvency_analysis": {
                "debt_to_equity": solvency_analysis.get("debt_to_equity"),
                "debt_to_assets": solvency_analysis.get("debt_to_assets"),
                "equity_ratio": solvency_analysis.get("equity_ratio"),
                "interest_coverage": solvency_analysis.get("interest_coverage"),
                "solvency_score": solvency_analysis.get("score", 5.0),
                "assessment": solvency_analysis.get("assessment", "adequate")
            },
            "asset_quality": {
                "asset_turnover": solvency_analysis.get("asset_turnover"),
                "tangible_assets_ratio": solvency_analysis.get("tangible_assets_ratio"),
                "goodwill_percentage": solvency_analysis.get("goodwill_percentage")
            }
        }
        
        # Cache the response
        await cache_service.cache_financial_data(ticker, f"balance_{period}", response)
        
        return response
        
    except Exception as e:
        if isinstance(e, (TickerNotFoundError, ValidationError)):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching balance sheets: {str(e)}")


@router.get(
    "/cash-flows",
    response_model=Dict[str, Any],
    summary="Get Cash Flow Statements with Quality Analysis",
    description="Fetch cash flow statements with enhanced cash flow quality analysis"
)
async def get_cash_flows(
    ticker: str = Query(..., description="Stock ticker symbol"),
    period: str = Query("annual", description="Period type: annual or quarterly"),
    limit: int = Query(4, description="Number of periods to return", ge=1, le=20),
    report_period_gte: Optional[date] = Query(None, description="Report period >= date"),
    report_period_lte: Optional[date] = Query(None, description="Report period <= date"),
    user: Dict[str, Any] = Depends(require_basic_financials),
    cache_service: CacheService = Depends(),
    data_provider: DataProvider = Depends(),
    analyzer: FinancialAnalyzer = Depends()
):
    """Get cash flow statements with enhanced analysis"""
    
    # Check cache first
    cached_data = await cache_service.get_financial_data(ticker, f"cashflow_{period}")
    
    if cached_data:
        return cached_data
    
    try:
        # Fetch cash flow data
        cash_flows = await data_provider.get_cash_flows(
            ticker=ticker,
            period=period,
            limit=limit,
            period_gte=report_period_gte,
            period_lte=report_period_lte
        )
        
        if not cash_flows:
            raise TickerNotFoundError(ticker)
        
        # Perform enhanced analysis
        cash_flow_analysis = await analyzer.analyze_cash_flow_quality(cash_flows)
        
        # Construct response
        response = {
            "ticker": ticker,
            "period": period,
            "cash_flows": cash_flows,
            "cash_flow_analysis": {
                "operating_cf_quality": cash_flow_analysis.get("operating_quality", "medium"),
                "free_cash_flow": cash_flow_analysis.get("latest_fcf"),
                "fcf_margin": cash_flow_analysis.get("fcf_margin"),
                "cash_conversion_cycle": cash_flow_analysis.get("cash_conversion_cycle"),
                "capex_intensity": cash_flow_analysis.get("capex_intensity"),
                "fcf_stability": cash_flow_analysis.get("fcf_stability", "medium")
            },
            "cash_generation": {
                "ocf_to_sales": cash_flow_analysis.get("ocf_to_sales"),
                "ocf_to_ni": cash_flow_analysis.get("ocf_to_net_income"),
                "fcf_yield": cash_flow_analysis.get("fcf_yield"),
                "cash_roi": cash_flow_analysis.get("cash_roi")
            },
            "capital_allocation": {
                "dividend_payout_ratio": cash_flow_analysis.get("dividend_payout"),
                "buyback_ratio": cash_flow_analysis.get("buyback_ratio"),
                "reinvestment_rate": cash_flow_analysis.get("reinvestment_rate"),
                "debt_repayment_ratio": cash_flow_analysis.get("debt_repayment_ratio")
            }
        }
        
        # Cache the response
        await cache_service.cache_financial_data(ticker, f"cashflow_{period}", response)
        
        return response
        
    except Exception as e:
        if isinstance(e, (TickerNotFoundError, ValidationError)):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching cash flows: {str(e)}")


@router.get(
    "/comprehensive/{ticker}",
    response_model=Dict[str, Any],
    summary="Get Comprehensive Financial Data",
    description="Get all financial statements with complete analysis in one call"
)
async def get_comprehensive_financials(
    ticker: str,
    period: str = Query("annual", description="Period type: annual or quarterly"),
    limit: int = Query(4, description="Number of periods to return", ge=1, le=20),
    user: Dict[str, Any] = Depends(require_basic_financials),
    cache_service: CacheService = Depends(),
    data_provider: DataProvider = Depends(),
    analyzer: FinancialAnalyzer = Depends()
):
    """Get comprehensive financial analysis combining all statements"""
    
    # Check cache first
    cached_data = await cache_service.get_financial_data(ticker, f"comprehensive_{period}")
    
    if cached_data:
        return cached_data
    
    try:
        # Fetch all financial data
        company_info = await data_provider.get_company_info(ticker)
        income_statements = await data_provider.get_income_statements(ticker, period, limit)
        balance_sheets = await data_provider.get_balance_sheets(ticker, period, limit)
        cash_flows = await data_provider.get_cash_flows(ticker, period, limit)
        
        if not any([income_statements, balance_sheets, cash_flows]):
            raise TickerNotFoundError(ticker)
        
        # Perform comprehensive analysis
        comprehensive_analysis = await analyzer.comprehensive_analysis(
            income_statements, balance_sheets, cash_flows
        )
        
        # Construct comprehensive response
        response = {
            "ticker": ticker,
            "company": company_info,
            "period": period,
            "statements": {
                "income_statements": income_statements,
                "balance_sheets": balance_sheets,
                "cash_flows": cash_flows
            },
            "financial_health": {
                "overall_score": comprehensive_analysis.get("overall_score", 5.0),
                "profitability_score": comprehensive_analysis.get("profitability_score", 5.0),
                "liquidity_score": comprehensive_analysis.get("liquidity_score", 5.0),
                "solvency_score": comprehensive_analysis.get("solvency_score", 5.0),
                "efficiency_score": comprehensive_analysis.get("efficiency_score", 5.0),
                "growth_score": comprehensive_analysis.get("growth_score", 5.0)
            },
            "key_insights": comprehensive_analysis.get("insights", []),
            "risk_factors": comprehensive_analysis.get("risk_factors", []),
            "opportunities": comprehensive_analysis.get("opportunities", []),
            "peer_comparison": comprehensive_analysis.get("peer_comparison", {}),
            "analyst_summary": comprehensive_analysis.get("summary", "")
        }
        
        # Cache the comprehensive response
        await cache_service.cache_financial_data(ticker, f"comprehensive_{period}", response)
        
        return response
        
    except Exception as e:
        if isinstance(e, (TickerNotFoundError, ValidationError)):
            raise e
        raise HTTPException(status_code=500, detail=f"Error fetching comprehensive data: {str(e)}")


@router.get("/data-sources", response_model=Dict[str, Any])
async def get_data_sources_info(current_user: Dict = Depends(get_current_user)):
    """
    Get information about data sources used for maximum accuracy.
    
    This endpoint provides transparency about the multiple data sources
    used to ensure the highest accuracy of financial data.
    """
    
    data_provider = DataProvider()
    
    # Check which data sources are currently available
    available_sources = []
    
    # Primary sources (always available)
    if data_provider.alpha_vantage_key:
        available_sources.append({
            "name": "Alpha Vantage",
            "type": "Primary",
            "reliability_score": 0.95,
            "description": "Official NASDAQ vendor with high-quality, regulated data",
            "coverage": ["Stocks", "Options", "Forex", "Crypto", "Technical Indicators"],
            "status": "Active"
        })
    
    # Yahoo Finance (free source)
    available_sources.append({
        "name": "Yahoo Finance",
        "type": "Secondary/Fallback", 
        "reliability_score": 0.75,
        "description": "Comprehensive free financial data source",
        "coverage": ["Stocks", "ETFs", "Mutual Funds", "Indices"],
        "status": "Active"
    })
    
    # FMP (SEC data source)
    if data_provider.fmp_key and data_provider.fmp_key != "":
        available_sources.append({
            "name": "Financial Modeling Prep",
            "type": "Secondary",
            "reliability_score": 0.90,
            "description": "SEC data source with high accuracy fundamental data",
            "coverage": ["Fundamental Data", "Financial Statements", "Ratios"],
            "status": "Active"
        })
    
    # Additional premium sources (if configured)
    premium_sources = [
        ("Polygon.io", data_provider.polygon_key, 0.85, "Premium institutional data with high accuracy"),
        ("TwelveData", data_provider.twelvedata_key, 0.80, "Good coverage and accuracy for global markets"),
        ("IEX Cloud", data_provider.iex_key, 0.85, "High-quality market data (now discontinued)"),
        ("EOD Historical", data_provider.eod_key, 0.80, "Excellent for historical data analysis"),
        ("Quandl", data_provider.quandl_key, 0.90, "High-quality alternative and economic data")
    ]
    
    for name, api_key, score, desc in premium_sources:
        if api_key:
            available_sources.append({
                "name": name,
                "type": "Premium",
                "reliability_score": score,
                "description": desc,
                "status": "Active"
            })
        else:
            available_sources.append({
                "name": name,
                "type": "Premium",
                "reliability_score": score,
                "description": f"{desc} (Not configured)",
                "status": "Not Configured"
            })
    
    return {
        "data_accuracy_strategy": {
            "approach": "Multi-source cross-validation with weighted confidence scoring",
            "validation_method": "Cross-reference data points across multiple sources",
            "confidence_scoring": "Weighted averages based on source reliability",
            "variance_threshold": "10% maximum variance between sources for validation"
        },
        "available_sources": available_sources,
        "data_merging": {
            "primary_strategy": "Use highest reliability source as base",
            "validation": "Cross-validate numerical fields across all sources",
            "conflict_resolution": "Weighted average when sources agree within 10% variance",
            "confidence_boost": "Increase confidence score when multiple sources agree"
        },
        "source_priority": [
            "1. Alpha Vantage (Official NASDAQ vendor)",
            "2. Financial Modeling Prep (SEC data)",
            "3. Premium sources (Polygon, TwelveData, etc.)",
            "4. Yahoo Finance (fallback)"
        ],
        "total_active_sources": len([s for s in available_sources if s["status"] == "Active"]),
        "accuracy_features": [
            "Multiple data source validation",
            "Weighted confidence scoring", 
            "Cross-reference validation",
            "Automatic fallback mechanisms",
            "Real-time source health monitoring"
        ]
    }

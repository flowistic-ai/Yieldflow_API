"""
Charts and visualizations endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, Optional, List
import base64
import json

from app.core.deps import require_charts
from app.services.data_provider import DataProvider
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.cache_service import CacheService
from app.utils.exceptions import TickerNotFoundError, ValidationError

router = APIRouter()


@router.get("/generate/{symbol}")
async def generate_chart(
    symbol: str,
    chart_type: str = Query("line", description="Chart type: line, bar, pie, area"),
    metric: str = Query("revenue", description="Metric to chart: revenue, profit, margins, ratios"),
    period: str = Query("annual", description="Period type: annual or quarterly"),
    limit: int = Query(4, description="Number of periods to return", ge=2, le=10),
    user: Dict[str, Any] = Depends(require_charts),
    cache_service: CacheService = Depends(),
    data_provider: DataProvider = Depends(),
    analyzer: FinancialAnalyzer = Depends()
):
    """Generate chart data for financial visualizations"""
    
    # Check cache first
    cache_key = f"chart_{symbol}_{chart_type}_{metric}_{period}_{limit}"
    cached_data = await cache_service.get_financial_data(symbol, f"chart_{chart_type}_{metric}")
    
    if cached_data:
        return cached_data
    
    try:
        # Fetch financial data based on metric
        chart_data = {}
        
        if metric in ["revenue", "profit", "income", "margins"]:
            income_statements = await data_provider.get_income_statements(
                ticker=symbol, period=period, limit=limit
            )
            
            if not income_statements:
                raise TickerNotFoundError(symbol)
            
            chart_data = await _prepare_income_chart_data(
                income_statements, chart_type, metric, analyzer
            )
            
        elif metric in ["liquidity", "solvency", "balance"]:
            balance_sheets = await data_provider.get_balance_sheets(
                ticker=symbol, period=period, limit=limit
            )
            
            if not balance_sheets:
                raise TickerNotFoundError(symbol)
            
            chart_data = await _prepare_balance_chart_data(
                balance_sheets, chart_type, metric, analyzer
            )
            
        elif metric in ["cash_flow", "fcf"]:
            cash_flows = await data_provider.get_cash_flows(
                ticker=symbol, period=period, limit=limit
            )
            
            if not cash_flows:
                raise TickerNotFoundError(symbol)
            
            chart_data = await _prepare_cash_flow_chart_data(
                cash_flows, chart_type, metric, analyzer
            )
            
        elif metric == "ratios":
            # Comprehensive ratios chart
            income_statements = await data_provider.get_income_statements(
                ticker=symbol, period=period, limit=limit
            )
            balance_sheets = await data_provider.get_balance_sheets(
                ticker=symbol, period=period, limit=limit
            )
            
            if not income_statements:
                raise TickerNotFoundError(symbol)
            
            chart_data = await _prepare_ratios_chart_data(
                income_statements, balance_sheets, chart_type, analyzer
            )
        
        else:
            raise ValueError(f"Unsupported metric: {metric}")
        
        # Create response
        response = {
            "symbol": symbol,
            "chart_type": chart_type,
            "metric": metric,
            "period": period,
            "chart_data": chart_data,
            "chart_config": {
                "title": f"{symbol} - {metric.title()} ({period.title()})",
                "x_axis_label": "Period",
                "y_axis_label": _get_y_axis_label(metric),
                "theme": "professional"
            },
            "user_plan": user.get("plan", "unknown")
        }
        
        # Cache the response
        await cache_service.cache_financial_data(symbol, f"chart_{chart_type}_{metric}", response)
        
        return response
        
    except Exception as e:
        if isinstance(e, (TickerNotFoundError, ValidationError)):
            raise e
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")


async def _prepare_income_chart_data(
    income_statements: List[Dict[str, Any]], 
    chart_type: str, 
    metric: str, 
    analyzer: FinancialAnalyzer
) -> Dict[str, Any]:
    """Prepare chart data for income statement metrics"""
    
    # Sort by period
    sorted_statements = sorted(income_statements, key=lambda x: x.get('period_ending', ''))
    
    periods = [stmt.get('period_ending', '') for stmt in sorted_statements]
    
    if metric == "revenue":
        values = [stmt.get('revenue', 0) for stmt in sorted_statements]
        return {
            "labels": periods,
            "datasets": [{
                "label": "Revenue",
                "data": values,
                "type": chart_type
            }]
        }
    
    elif metric == "profit":
        net_income = [stmt.get('net_income', 0) for stmt in sorted_statements]
        operating_income = [stmt.get('operating_income', 0) for stmt in sorted_statements]
        gross_profit = [stmt.get('gross_profit', 0) for stmt in sorted_statements]
        
        return {
            "labels": periods,
            "datasets": [
                {"label": "Net Income", "data": net_income, "type": chart_type},
                {"label": "Operating Income", "data": operating_income, "type": chart_type},
                {"label": "Gross Profit", "data": gross_profit, "type": chart_type}
            ]
        }
    
    elif metric == "margins":
        # Calculate margins for each period
        margin_data = []
        for stmt in sorted_statements:
            ratios = await analyzer.calculate_profitability_ratios([stmt])
            margin_data.append({
                "gross_margin": ratios.get("gross_margin", 0),
                "operating_margin": ratios.get("operating_margin", 0),
                "net_margin": ratios.get("net_margin", 0)
            })
        
        return {
            "labels": periods,
            "datasets": [
                {"label": "Gross Margin %", "data": [d["gross_margin"] for d in margin_data], "type": chart_type},
                {"label": "Operating Margin %", "data": [d["operating_margin"] for d in margin_data], "type": chart_type},
                {"label": "Net Margin %", "data": [d["net_margin"] for d in margin_data], "type": chart_type}
            ]
        }
    
    return {"labels": periods, "datasets": []}


async def _prepare_balance_chart_data(
    balance_sheets: List[Dict[str, Any]], 
    chart_type: str, 
    metric: str, 
    analyzer: FinancialAnalyzer
) -> Dict[str, Any]:
    """Prepare chart data for balance sheet metrics"""
    
    sorted_sheets = sorted(balance_sheets, key=lambda x: x.get('period_ending', ''))
    periods = [sheet.get('period_ending', '') for sheet in sorted_sheets]
    
    if metric == "liquidity":
        # Calculate liquidity ratios for each period
        liquidity_data = []
        for sheet in sorted_sheets:
            analysis = await analyzer.analyze_liquidity([sheet])
            liquidity_data.append(analysis)
        
        return {
            "labels": periods,
            "datasets": [
                {"label": "Current Ratio", "data": [d.get("current_ratio", 0) for d in liquidity_data], "type": chart_type},
                {"label": "Quick Ratio", "data": [d.get("quick_ratio", 0) for d in liquidity_data], "type": chart_type},
                {"label": "Cash Ratio", "data": [d.get("cash_ratio", 0) for d in liquidity_data], "type": chart_type}
            ]
        }
    
    elif metric == "balance":
        assets = [sheet.get('total_assets', 0) for sheet in sorted_sheets]
        liabilities = [sheet.get('total_liabilities', 0) for sheet in sorted_sheets]
        equity = [sheet.get('total_equity', 0) for sheet in sorted_sheets]
        
        return {
            "labels": periods,
            "datasets": [
                {"label": "Total Assets", "data": assets, "type": chart_type},
                {"label": "Total Liabilities", "data": liabilities, "type": chart_type},
                {"label": "Total Equity", "data": equity, "type": chart_type}
            ]
        }
    
    return {"labels": periods, "datasets": []}


async def _prepare_cash_flow_chart_data(
    cash_flows: List[Dict[str, Any]], 
    chart_type: str, 
    metric: str, 
    analyzer: FinancialAnalyzer
) -> Dict[str, Any]:
    """Prepare chart data for cash flow metrics"""
    
    sorted_flows = sorted(cash_flows, key=lambda x: x.get('period_ending', ''))
    periods = [flow.get('period_ending', '') for flow in sorted_flows]
    
    operating_cf = [flow.get('operating_cash_flow', 0) for flow in sorted_flows]
    investing_cf = [flow.get('investing_cash_flow', 0) for flow in sorted_flows]
    financing_cf = [flow.get('financing_cash_flow', 0) for flow in sorted_flows]
    
    # Calculate free cash flow
    free_cf = []
    for flow in sorted_flows:
        fcf = (flow.get('operating_cash_flow', 0) - 
               flow.get('capital_expenditures', 0))
        free_cf.append(fcf)
    
    return {
        "labels": periods,
        "datasets": [
            {"label": "Operating Cash Flow", "data": operating_cf, "type": chart_type},
            {"label": "Investing Cash Flow", "data": investing_cf, "type": chart_type},
            {"label": "Financing Cash Flow", "data": financing_cf, "type": chart_type},
            {"label": "Free Cash Flow", "data": free_cf, "type": chart_type}
        ]
    }


async def _prepare_ratios_chart_data(
    income_statements: List[Dict[str, Any]], 
    balance_sheets: List[Dict[str, Any]], 
    chart_type: str, 
    analyzer: FinancialAnalyzer
) -> Dict[str, Any]:
    """Prepare chart data for comprehensive ratios"""
    
    periods = [stmt.get('period_ending', '') for stmt in income_statements]
    
    # Calculate key ratios for each period
    roe_data = []
    roa_data = []
    profit_margin_data = []
    
    for i, stmt in enumerate(income_statements):
        # ROE and ROA need balance sheet data
        if i < len(balance_sheets):
            net_income = stmt.get('net_income', 0)
            total_assets = balance_sheets[i].get('total_assets', 1)
            total_equity = balance_sheets[i].get('total_equity', 1)
            
            roe = (net_income / total_equity) * 100 if total_equity > 0 else 0
            roa = (net_income / total_assets) * 100 if total_assets > 0 else 0
            
            roe_data.append(roe)
            roa_data.append(roa)
        
        # Profit margin from income statement
        revenue = stmt.get('revenue', 1)
        net_income = stmt.get('net_income', 0)
        profit_margin = (net_income / revenue) * 100 if revenue > 0 else 0
        profit_margin_data.append(profit_margin)
    
    return {
        "labels": periods,
        "datasets": [
            {"label": "ROE %", "data": roe_data, "type": chart_type},
            {"label": "ROA %", "data": roa_data, "type": chart_type},
            {"label": "Profit Margin %", "data": profit_margin_data, "type": chart_type}
        ]
    }


def _get_y_axis_label(metric: str) -> str:
    """Get appropriate Y-axis label for metric"""
    labels = {
        "revenue": "Revenue ($)",
        "profit": "Profit ($)",
        "margins": "Margin (%)",
        "ratios": "Ratio Value",
        "liquidity": "Ratio Value",
        "cash_flow": "Cash Flow ($)",
        "balance": "Amount ($)"
    }
    return labels.get(metric, "Value")


@router.get("/health")
async def charts_health():
    """Health check for charts module"""
    return {"status": "healthy", "module": "charts"}

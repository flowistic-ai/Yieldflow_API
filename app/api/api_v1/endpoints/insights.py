"""
AI insights endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.deps import require_ai_insights
from app.services.data_provider import DataProvider
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.cache_service import CacheService
from app.utils.exceptions import TickerNotFoundError, ValidationError

router = APIRouter()


@router.get("/analyze/{symbol}")
async def get_ai_insights(
    symbol: str,
    period: str = Query("annual", description="Period type: annual or quarterly"),
    limit: int = Query(4, description="Number of periods to return", ge=2, le=8),
    analysis_type: str = Query("comprehensive", description="Analysis type: comprehensive, risk, growth, value"),
    user: Dict[str, Any] = Depends(require_ai_insights),
    cache_service: CacheService = Depends(),
    data_provider: DataProvider = Depends(),
    analyzer: FinancialAnalyzer = Depends()
):
    """Get AI-powered financial insights for a symbol"""
    
    # Check cache first
    cache_key = f"insights_{symbol}_{analysis_type}_{period}_{limit}"
    cached_data = await cache_service.get_financial_data(symbol, f"insights_{analysis_type}")
    
    if cached_data:
        return cached_data
    
    try:
        # Fetch comprehensive financial data
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
        
        # Perform comprehensive analysis
        comprehensive_analysis = await analyzer.comprehensive_analysis(
            income_statements=income_statements,
            balance_sheets=balance_sheets or [],
            cash_flows=cash_flows or []
        )
        
        # Generate specific insights based on analysis type
        insights = await _generate_insights(
            symbol, analysis_type, comprehensive_analysis, 
            income_statements, balance_sheets, cash_flows
        )
        
        # Create response
        response = {
            "symbol": symbol,
            "analysis_type": analysis_type,
            "period": period,
            "insights": insights,
            "analysis_summary": {
                "overall_score": comprehensive_analysis.get("overall_score", 5.0),
                "profitability_score": comprehensive_analysis.get("profitability_score", 5.0),
                "liquidity_score": comprehensive_analysis.get("liquidity_analysis", {}).get("score", 5.0),
                "solvency_score": comprehensive_analysis.get("solvency_analysis", {}).get("score", 5.0),
                "confidence_level": comprehensive_analysis.get("confidence", 0.8)
            },
            "key_metrics": _extract_key_metrics(comprehensive_analysis),
            "recommendations": _generate_recommendations(comprehensive_analysis, analysis_type),
            "risk_factors": comprehensive_analysis.get("risk_factors", []),
            "opportunities": comprehensive_analysis.get("opportunities", []),
            "generated_at": datetime.utcnow().isoformat(),
            "user_plan": user.get("plan", "unknown")
        }
        
        # Cache the response
        await cache_service.cache_financial_data(symbol, f"insights_{analysis_type}", response)
        
        return response
        
    except Exception as e:
        if isinstance(e, (TickerNotFoundError, ValidationError)):
            raise e
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


async def _generate_insights(
    symbol: str,
    analysis_type: str,
    comprehensive_analysis: Dict[str, Any],
    income_statements: List[Dict[str, Any]],
    balance_sheets: List[Dict[str, Any]],
    cash_flows: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Generate AI insights based on analysis type"""
    
    insights = []
    
    # Overall financial health insight
    overall_score = comprehensive_analysis.get("overall_score", 5.0)
    if overall_score >= 7.5:
        insights.append({
            "type": "positive",
            "category": "financial_health",
            "title": "Strong Financial Position",
            "description": f"{symbol} demonstrates strong overall financial health with an excellent score of {overall_score:.1f}/10.",
            "confidence": 0.9
        })
    elif overall_score <= 3.5:
        insights.append({
            "type": "warning",
            "category": "financial_health",
            "title": "Concerning Financial Position",
            "description": f"{symbol} shows concerning financial health with a low score of {overall_score:.1f}/10.",
            "confidence": 0.9
        })
    
    # Revenue and profitability insights
    income_analysis = comprehensive_analysis.get("income_analysis", {})
    revenue_trend = income_analysis.get("revenue_trend", "stable")
    
    if revenue_trend == "strong_growth":
        insights.append({
            "type": "positive",
            "category": "growth",
            "title": "Strong Revenue Growth",
            "description": f"{symbol} shows strong revenue growth momentum, indicating effective business expansion.",
            "confidence": 0.85
        })
    elif revenue_trend == "declining":
        insights.append({
            "type": "warning",
            "category": "growth",
            "title": "Revenue Decline Trend",
            "description": f"{symbol} is experiencing declining revenue, which may indicate market challenges or operational issues.",
            "confidence": 0.85
        })
    
    # Profitability margin insights
    margin_trend = income_analysis.get("margin_trend", "stable")
    if margin_trend == "improving":
        insights.append({
            "type": "positive",
            "category": "profitability",
            "title": "Improving Profit Margins",
            "description": f"{symbol} demonstrates improving profit margins, suggesting better operational efficiency.",
            "confidence": 0.8
        })
    elif margin_trend == "declining":
        insights.append({
            "type": "warning",
            "category": "profitability",
            "title": "Declining Profit Margins",
            "description": f"{symbol} shows declining profit margins, indicating potential cost pressures or pricing challenges.",
            "confidence": 0.8
        })
    
    # Liquidity insights
    liquidity_analysis = comprehensive_analysis.get("liquidity_analysis", {})
    liquidity_assessment = liquidity_analysis.get("assessment", "adequate")
    
    if liquidity_assessment == "excellent":
        insights.append({
            "type": "positive",
            "category": "liquidity",
            "title": "Excellent Liquidity Position",
            "description": f"{symbol} maintains excellent liquidity, providing strong ability to meet short-term obligations.",
            "confidence": 0.9
        })
    elif liquidity_assessment == "poor":
        insights.append({
            "type": "warning",
            "category": "liquidity",
            "title": "Poor Liquidity Position",
            "description": f"{symbol} has poor liquidity ratios, which may indicate difficulty meeting short-term obligations.",
            "confidence": 0.9
        })
    
    # Cash flow insights
    cash_flow_analysis = comprehensive_analysis.get("cash_flow_analysis", {})
    if cash_flow_analysis:
        fcf_trend = cash_flow_analysis.get("fcf_trend", "stable")
        if fcf_trend == "improving":
            insights.append({
                "type": "positive",
                "category": "cash_flow",
                "title": "Strong Free Cash Flow Generation",
                "description": f"{symbol} shows improving free cash flow, indicating strong cash generation capabilities.",
                "confidence": 0.85
            })
        elif fcf_trend == "declining":
            insights.append({
                "type": "warning",
                "category": "cash_flow",
                "title": "Declining Free Cash Flow",
                "description": f"{symbol} shows declining free cash flow, which may limit financial flexibility.",
                "confidence": 0.85
            })
    
    # Solvency insights
    solvency_analysis = comprehensive_analysis.get("solvency_analysis", {})
    if solvency_analysis:
        debt_to_equity = solvency_analysis.get("debt_to_equity", 0)
        if debt_to_equity > 2.0:
            insights.append({
                "type": "warning",
                "category": "debt",
                "title": "High Debt Levels",
                "description": f"{symbol} has high debt-to-equity ratio of {debt_to_equity:.2f}, indicating elevated financial leverage.",
                "confidence": 0.9
            })
        elif debt_to_equity < 0.3:
            insights.append({
                "type": "positive",
                "category": "debt",
                "title": "Conservative Debt Management",
                "description": f"{symbol} maintains low debt levels with D/E ratio of {debt_to_equity:.2f}, providing financial stability.",
                "confidence": 0.9
            })
    
    # Growth and efficiency insights based on analysis type
    if analysis_type in ["growth", "comprehensive"]:
        growth_score = comprehensive_analysis.get("growth_score", 5.0)
        if growth_score >= 7.0:
            insights.append({
                "type": "positive",
                "category": "growth",
                "title": "Strong Growth Metrics",
                "description": f"{symbol} demonstrates strong growth potential with a growth score of {growth_score:.1f}/10.",
                "confidence": 0.8
            })
    
    if analysis_type in ["value", "comprehensive"]:
        efficiency_score = comprehensive_analysis.get("efficiency_score", 5.0)
        if efficiency_score >= 7.0:
            insights.append({
                "type": "positive",
                "category": "efficiency",
                "title": "High Operational Efficiency",
                "description": f"{symbol} shows high operational efficiency with a score of {efficiency_score:.1f}/10.",
                "confidence": 0.8
            })
    
    return insights[:8]  # Limit to 8 key insights


def _extract_key_metrics(comprehensive_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from comprehensive analysis"""
    
    income_analysis = comprehensive_analysis.get("income_analysis", {})
    liquidity_analysis = comprehensive_analysis.get("liquidity_analysis", {})
    solvency_analysis = comprehensive_analysis.get("solvency_analysis", {})
    cash_flow_analysis = comprehensive_analysis.get("cash_flow_analysis", {})
    
    return {
        "revenue_growth_3y": income_analysis.get("revenue_cagr_3y", 0.0),
        "profit_margin_trend": income_analysis.get("margin_trend", "stable"),
        "current_ratio": liquidity_analysis.get("current_ratio", 0.0),
        "debt_to_equity": solvency_analysis.get("debt_to_equity", 0.0),
        "free_cash_flow": cash_flow_analysis.get("free_cash_flow", 0.0),
        "earnings_quality": income_analysis.get("earnings_quality", "medium"),
        "overall_health_score": comprehensive_analysis.get("overall_score", 5.0)
    }


def _generate_recommendations(comprehensive_analysis: Dict[str, Any], analysis_type: str) -> List[str]:
    """Generate actionable recommendations based on analysis"""
    
    recommendations = []
    overall_score = comprehensive_analysis.get("overall_score", 5.0)
    
    # General recommendations based on overall score
    if overall_score >= 8.0:
        recommendations.append("Consider this company for long-term investment given its strong financial fundamentals")
        recommendations.append("Monitor for any changes in key performance indicators to maintain current trajectory")
    elif overall_score <= 4.0:
        recommendations.append("Exercise caution - address identified financial weaknesses before considering investment")
        recommendations.append("Focus on improving liquidity and profitability metrics")
    
    # Specific recommendations based on analysis components
    liquidity_score = comprehensive_analysis.get("liquidity_analysis", {}).get("score", 5.0)
    if liquidity_score < 5.0:
        recommendations.append("Improve working capital management to enhance liquidity position")
    
    solvency_score = comprehensive_analysis.get("solvency_analysis", {}).get("score", 5.0)
    if solvency_score < 5.0:
        recommendations.append("Consider debt reduction strategies to improve financial leverage")
    
    # Growth-specific recommendations
    if analysis_type == "growth":
        growth_score = comprehensive_analysis.get("growth_score", 5.0)
        if growth_score >= 7.0:
            recommendations.append("Strong growth metrics support expansion opportunities")
        else:
            recommendations.append("Focus on revenue growth initiatives and market expansion")
    
    return recommendations[:5]  # Limit to 5 recommendations


@router.get("/health")
async def insights_health():
    """Health check for insights module"""
    return {"status": "healthy", "module": "insights"}

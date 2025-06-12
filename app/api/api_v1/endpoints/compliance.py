"""
Compliance and ESG endpoints
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.deps import require_compliance
from app.services.data_provider import DataProvider
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.cache_service import CacheService
from app.utils.exceptions import TickerNotFoundError, ValidationError

router = APIRouter()


@router.get("/esg/{symbol}")
async def get_esg_data(
    symbol: str,
    period: str = Query("annual", description="Period type: annual or quarterly"),
    limit: int = Query(4, description="Number of periods to return", ge=1, le=8),
    user: Dict[str, Any] = Depends(require_compliance),
    cache_service: CacheService = Depends(),
    data_provider: DataProvider = Depends(),
    analyzer: FinancialAnalyzer = Depends()
):
    """Get ESG compliance and sustainability metrics for a symbol"""
    
    # Check cache first
    cache_key = f"esg_{symbol}_{period}_{limit}"
    cached_data = await cache_service.get_financial_data(symbol, f"esg_{period}")
    
    if cached_data:
        return cached_data
    
    try:
        # Fetch financial data for ESG analysis
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
        
        # Analyze ESG-related financial metrics
        esg_analysis = await _analyze_esg_metrics(
            symbol, income_statements, balance_sheets, cash_flows, analyzer
        )
        
        # Generate governance assessment
        governance_assessment = await _assess_governance_metrics(
            symbol, income_statements, balance_sheets, cash_flows
        )
        
        # Environmental impact indicators
        environmental_indicators = await _analyze_environmental_indicators(
            symbol, income_statements, cash_flows
        )
        
        # Social responsibility metrics
        social_metrics = await _analyze_social_responsibility(
            symbol, income_statements, balance_sheets
        )
        
        # Create response
        response = {
            "symbol": symbol,
            "period": period,
            "esg_analysis": esg_analysis,
            "governance_metrics": governance_assessment,
            "environmental_indicators": environmental_indicators,
            "social_responsibility": social_metrics,
            "overall_esg_score": _calculate_overall_esg_score(
                esg_analysis, governance_assessment, environmental_indicators, social_metrics
            ),
            "compliance_status": _assess_compliance_status(
                esg_analysis, governance_assessment
            ),
            "recommendations": _generate_esg_recommendations(
                esg_analysis, governance_assessment, environmental_indicators, social_metrics
            ),
            "generated_at": datetime.utcnow().isoformat(),
            "user_plan": user.get("plan", "unknown")
        }
        
        # Cache the response
        await cache_service.cache_financial_data(symbol, f"esg_{period}", response)
        
        return response
        
    except Exception as e:
        if isinstance(e, (TickerNotFoundError, ValidationError)):
            raise e
        raise HTTPException(status_code=500, detail=f"Error analyzing ESG data: {str(e)}")


async def _analyze_esg_metrics(
    symbol: str,
    income_statements: List[Dict[str, Any]],
    balance_sheets: List[Dict[str, Any]],
    cash_flows: List[Dict[str, Any]],
    analyzer: FinancialAnalyzer
) -> Dict[str, Any]:
    """Analyze ESG-related financial metrics"""
    
    # Perform comprehensive financial analysis
    comprehensive_analysis = await analyzer.comprehensive_analysis(
        income_statements=income_statements,
        balance_sheets=balance_sheets or [],
        cash_flows=cash_flows or []
    )
    
    # Extract ESG-relevant metrics
    latest_income = income_statements[0]
    
    # Revenue stability and growth (sustainability indicator)
    revenue_stability = comprehensive_analysis.get("income_analysis", {}).get("revenue_trend", "stable")
    
    # Capital allocation efficiency
    capital_efficiency = comprehensive_analysis.get("efficiency_score", 5.0)
    
    # Long-term financial sustainability
    financial_sustainability = comprehensive_analysis.get("overall_score", 5.0)
    
    return {
        "revenue_stability": revenue_stability,
        "capital_efficiency_score": capital_efficiency,
        "financial_sustainability_score": financial_sustainability,
        "revenue_growth_3y": comprehensive_analysis.get("income_analysis", {}).get("revenue_cagr_3y", 0.0),
        "profit_margin_stability": comprehensive_analysis.get("income_analysis", {}).get("margin_trend", "stable"),
        "cash_flow_quality": comprehensive_analysis.get("cash_flow_analysis", {}).get("score", 5.0)
    }


async def _assess_governance_metrics(
    symbol: str,
    income_statements: List[Dict[str, Any]],
    balance_sheets: List[Dict[str, Any]],
    cash_flows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Assess corporate governance through financial indicators"""
    
    latest_income = income_statements[0]
    latest_balance = balance_sheets[0] if balance_sheets else {}
    
    # Debt management (governance indicator)
    total_debt = latest_balance.get("total_liabilities", 0)
    total_equity = latest_balance.get("total_equity", 1)
    debt_to_equity = total_debt / total_equity if total_equity > 0 else 0
    
    # Operational efficiency
    revenue = latest_income.get("revenue", 1)
    operating_income = latest_income.get("operating_income", 0)
    operating_margin = (operating_income / revenue * 100) if revenue > 0 else 0
    
    # Board effectiveness (inferred from financial performance)
    board_effectiveness_score = min(10, max(1, (operating_margin / 10) + 5))
    
    return {
        "financial_transparency_score": 10.0,  # Assume high if we have data
        "debt_management_score": max(1, min(10, 10 - (debt_to_equity * 2))),
        "operational_efficiency_score": min(10, max(1, operating_margin / 2 + 5)),
        "board_effectiveness_score": board_effectiveness_score,
        "overall_governance_score": (
            10.0 +
            max(1, min(10, 10 - (debt_to_equity * 2))) +
            min(10, max(1, operating_margin / 2 + 5)) +
            board_effectiveness_score
        ) / 4
    }


async def _analyze_environmental_indicators(
    symbol: str,
    income_statements: List[Dict[str, Any]],
    cash_flows: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Analyze environmental impact indicators from financial data"""
    
    latest_income = income_statements[0]
    latest_cash = cash_flows[0] if cash_flows else {}
    
    # Capital expenditures as proxy for sustainability investments
    capex = abs(latest_cash.get("capital_expenditures", 0))
    revenue = latest_income.get("revenue", 1)
    capex_ratio = (capex / revenue * 100) if revenue > 0 else 0
    
    # R&D spending (proxy for green innovation)
    rd_expense = latest_income.get("research_and_development", 0)
    rd_intensity = (rd_expense / revenue * 100) if revenue > 0 else 0
    
    # Energy efficiency (inferred from cost structure)
    cost_of_revenue = latest_income.get("cost_of_revenue", 0)
    gross_margin = ((revenue - cost_of_revenue) / revenue * 100) if revenue > 0 else 0
    
    # Environmental score based on financial efficiency
    environmental_score = (
        min(10, capex_ratio) +  # Higher capex potentially means sustainability investments
        min(10, rd_intensity * 2) +  # R&D intensity
        min(10, gross_margin / 5)  # Operational efficiency
    ) / 3
    
    return {
        "capital_investment_ratio": capex_ratio,
        "rd_intensity": rd_intensity,
        "operational_efficiency": gross_margin,
        "environmental_score": environmental_score,
        "sustainability_investment_indicator": "high" if capex_ratio > 10 else "medium" if capex_ratio > 5 else "low"
    }


async def _analyze_social_responsibility(
    symbol: str,
    income_statements: List[Dict[str, Any]],
    balance_sheets: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Analyze social responsibility indicators"""
    
    latest_income = income_statements[0]
    latest_balance = balance_sheets[0] if balance_sheets else {}
    
    # Financial stability (affects stakeholder security)
    current_assets = latest_balance.get("current_assets", 0)
    current_liabilities = latest_balance.get("current_liabilities", 1)
    current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
    
    # Long-term value creation
    retained_earnings = latest_balance.get("retained_earnings", 0)
    total_equity = latest_balance.get("total_equity", 1)
    value_creation_ratio = (retained_earnings / total_equity * 100) if total_equity > 0 else 0
    
    # Social responsibility score
    social_score = (
        min(10, current_ratio * 2) +  # Financial stability
        min(10, max(0, value_creation_ratio / 10)) +  # Long-term value creation
        5  # Base score for having financial data
    ) / 3
    
    return {
        "financial_stability_score": min(10, current_ratio * 2),
        "stakeholder_value_creation": value_creation_ratio,
        "social_responsibility_score": social_score,
        "community_impact_indicator": "positive" if social_score > 6 else "neutral" if social_score > 4 else "needs_improvement"
    }


def _calculate_overall_esg_score(
    esg_analysis: Dict[str, Any],
    governance_metrics: Dict[str, Any],
    environmental_indicators: Dict[str, Any],
    social_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate overall ESG score"""
    
    environmental_score = environmental_indicators.get("environmental_score", 5.0)
    social_score = social_metrics.get("social_responsibility_score", 5.0)
    governance_score = governance_metrics.get("overall_governance_score", 5.0)
    
    overall_score = (environmental_score + social_score + governance_score) / 3
    
    # Determine rating
    if overall_score >= 8.0:
        rating = "A"
    elif overall_score >= 6.5:
        rating = "B"
    elif overall_score >= 5.0:
        rating = "C"
    elif overall_score >= 3.5:
        rating = "D"
    else:
        rating = "F"
    
    return {
        "overall_score": overall_score,
        "environmental_score": environmental_score,
        "social_score": social_score,
        "governance_score": governance_score,
        "esg_rating": rating,
        "percentile_rank": min(100, max(0, overall_score * 10))
    }


def _assess_compliance_status(
    esg_analysis: Dict[str, Any],
    governance_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Assess compliance status based on governance and financial metrics"""
    
    governance_score = governance_metrics.get("overall_governance_score", 5.0)
    financial_sustainability = esg_analysis.get("financial_sustainability_score", 5.0)
    
    if governance_score >= 7.0 and financial_sustainability >= 7.0:
        status = "compliant"
        risk_level = "low"
    elif governance_score >= 5.0 and financial_sustainability >= 5.0:
        status = "adequate"
        risk_level = "medium"
    else:
        status = "needs_improvement"
        risk_level = "high"
    
    return {
        "compliance_status": status,
        "risk_level": risk_level,
        "governance_compliance": "strong" if governance_score >= 7.0 else "adequate" if governance_score >= 5.0 else "weak",
        "financial_compliance": "strong" if financial_sustainability >= 7.0 else "adequate" if financial_sustainability >= 5.0 else "weak"
    }


def _generate_esg_recommendations(
    esg_analysis: Dict[str, Any],
    governance_metrics: Dict[str, Any],
    environmental_indicators: Dict[str, Any],
    social_metrics: Dict[str, Any]
) -> List[str]:
    """Generate ESG improvement recommendations"""
    
    recommendations = []
    
    # Environmental recommendations
    env_score = environmental_indicators.get("environmental_score", 5.0)
    if env_score < 6.0:
        recommendations.append("Increase capital investments in sustainable technologies and processes")
        recommendations.append("Enhance R&D spending focus on environmental innovation")
    
    # Social recommendations
    social_score = social_metrics.get("social_responsibility_score", 5.0)
    if social_score < 6.0:
        recommendations.append("Improve financial stability to better serve stakeholder interests")
        recommendations.append("Focus on long-term value creation for all stakeholders")
    
    # Governance recommendations
    governance_score = governance_metrics.get("overall_governance_score", 5.0)
    if governance_score < 6.0:
        recommendations.append("Enhance financial transparency and reporting quality")
        recommendations.append("Improve debt management and capital allocation efficiency")
    
    # Overall recommendations
    if len(recommendations) == 0:
        recommendations.append("Maintain current ESG practices and continue monitoring performance")
        recommendations.append("Consider setting more ambitious sustainability targets")
    
    return recommendations[:5]  # Limit to 5 recommendations


@router.get("/health")
async def compliance_health():
    """Health check for compliance module"""
    return {"status": "healthy", "module": "compliance"} 
"""
Financial API Endpoints
Provides comprehensive financial data and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
import structlog

from app.api.deps import get_current_user, require_basic_access, require_advanced_analytics
from app.services.data_provider import DataProvider
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.ratio_calculator import RatioCalculator
from app.utils.exceptions import TickerNotFoundError, DataSourceError, CalculationError

logger = structlog.get_logger()
router = APIRouter()

# Initialize services
data_provider = DataProvider()
financial_analyzer = FinancialAnalyzer()
ratio_calculator = RatioCalculator()


@router.get("/company/{ticker}")
async def get_company_info(
    ticker: str,
    current_user = Depends(require_basic_access)
):
    """
    Get comprehensive company information
    
    Returns basic company details including:
    - Company name and description
    - Sector and industry
    - Market capitalization
    - Key metrics
    """
    try:
        logger.info("Fetching company info", ticker=ticker, user_id=current_user.id)
        
        company_data = await data_provider.get_company_info(ticker)
        
        if not company_data:
            raise TickerNotFoundError(ticker)
        
        return {
            "ticker": ticker,
            "status": "success",
            "data": company_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except TickerNotFoundError:
        logger.warning("Ticker not found", ticker=ticker)
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
    
    except DataSourceError as e:
        logger.error("Data source error", ticker=ticker, error=str(e))
        raise HTTPException(status_code=503, detail="Data source temporarily unavailable")
    
    except Exception as e:
        logger.error("Unexpected error in company info", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/statements/{ticker}")
async def get_financial_statements(
    ticker: str,
    statement_type: str = Query("income", regex="^(income|balance|cash_flow)$"),
    period: str = Query("annual", regex="^(annual|quarterly)$"),
    limit: int = Query(4, ge=1, le=10),
    current_user = Depends(require_basic_access)
):
    """
    Get financial statements with basic analytics
    
    Statement types:
    - income: Income statements 
    - balance: Balance sheets
    - cash_flow: Cash flow statements
    """
    try:
        logger.info("Fetching financial statements", 
                   ticker=ticker, statement_type=statement_type, 
                   period=period, limit=limit, user_id=current_user.id)
        
        if statement_type == "income":
            statements = await data_provider.get_income_statements(ticker, period, limit)
        elif statement_type == "balance":
            statements = await data_provider.get_balance_sheets(ticker, period, limit)
        elif statement_type == "cash_flow":
            statements = await data_provider.get_cash_flows(ticker, period, limit)
        
        if not statements:
            raise TickerNotFoundError(ticker)
        
        return {
            "ticker": ticker,
            "statement_type": statement_type,
            "period": period,
            "status": "success",
            "data": statements,
            "count": len(statements),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except TickerNotFoundError:
        raise HTTPException(status_code=404, detail=f"No {statement_type} statements found for ticker '{ticker}'")
    
    except DataSourceError as e:
        raise HTTPException(status_code=503, detail="Data source temporarily unavailable")
    
    except Exception as e:
        logger.error("Unexpected error in financial statements", 
                    ticker=ticker, statement_type=statement_type, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ratios/{ticker}")
async def get_financial_ratios(
    ticker: str,
    period: str = Query("annual", regex="^(annual|quarterly)$"),
    ratio_category: str = Query("all", regex="^(all|profitability|liquidity|leverage|efficiency|growth)$"),
    current_user = Depends(require_basic_access)
):
    """
    Calculate comprehensive financial ratios
    
    Categories:
    - all: All ratio categories
    - profitability: Margins, ROE, ROA
    - liquidity: Current, quick, cash ratios
    - leverage: Debt ratios, coverage ratios
    - efficiency: Turnover ratios
    - growth: Growth metrics
    """
    try:
        logger.info("Calculating financial ratios", 
                   ticker=ticker, period=period, 
                   category=ratio_category, user_id=current_user.id)
        
        # Get required financial data
        income_statements = await data_provider.get_income_statements(ticker, period, 5)
        balance_sheets = await data_provider.get_balance_sheets(ticker, period, 5)
        
        if not income_statements or not balance_sheets:
            raise TickerNotFoundError(ticker)
        
        # Calculate ratios based on category
        if ratio_category == "all":
            ratios = await ratio_calculator.calculate_all_ratios(income_statements, balance_sheets)
        elif ratio_category == "profitability":
            ratios = await ratio_calculator.calculate_profitability_ratios(income_statements, balance_sheets)
        elif ratio_category == "liquidity":
            ratios = await ratio_calculator.calculate_liquidity_ratios(balance_sheets)
        elif ratio_category == "leverage":
            ratios = await ratio_calculator.calculate_leverage_ratios(balance_sheets, income_statements)
        elif ratio_category == "efficiency":
            ratios = await ratio_calculator.calculate_efficiency_ratios(income_statements, balance_sheets)
        elif ratio_category == "growth":
            ratios = await ratio_calculator.calculate_growth_ratios(income_statements, balance_sheets)
        
        return {
            "ticker": ticker,
            "period": period,
            "category": ratio_category,
            "status": "success",
            "data": ratios,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except TickerNotFoundError:
        raise HTTPException(status_code=404, detail=f"Insufficient data for ratio calculation for ticker '{ticker}'")
    
    except CalculationError as e:
        raise HTTPException(status_code=422, detail=f"Ratio calculation failed: {str(e)}")
    
    except Exception as e:
        logger.error("Unexpected error in ratio calculation", 
                    ticker=ticker, category=ratio_category, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analysis/{ticker}")
async def get_financial_analysis(
    ticker: str,
    analysis_type: str = Query("comprehensive", regex="^(comprehensive|trends|liquidity|profitability|cashflow)$"),
    period: str = Query("annual", regex="^(annual|quarterly)$"),
    current_user = Depends(require_advanced_analytics)
):
    """
    Advanced financial analysis with AI insights
    
    Analysis types:
    - comprehensive: Complete financial health analysis
    - trends: Revenue and profit trend analysis
    - liquidity: Liquidity and working capital analysis
    - profitability: Profitability and efficiency analysis
    - cashflow: Cash flow quality analysis
    """
    try:
        logger.info("Performing financial analysis", 
                   ticker=ticker, analysis_type=analysis_type,
                   period=period, user_id=current_user.id)
        
        # Get comprehensive financial data
        income_statements = await data_provider.get_income_statements(ticker, period, 5)
        balance_sheets = await data_provider.get_balance_sheets(ticker, period, 5)
        cash_flows = await data_provider.get_cash_flows(ticker, period, 5)
        
        if not income_statements or not balance_sheets:
            raise TickerNotFoundError(ticker)
        
        # Perform analysis based on type
        if analysis_type == "comprehensive":
            analysis = await financial_analyzer.comprehensive_analysis(
                income_statements, balance_sheets, cash_flows
            )
        elif analysis_type == "trends":
            analysis = await financial_analyzer.analyze_income_trends(income_statements)
        elif analysis_type == "liquidity":
            analysis = await financial_analyzer.analyze_liquidity(balance_sheets)
        elif analysis_type == "profitability":
            # Create profitability analysis by combining metrics
            ratios = await ratio_calculator.calculate_profitability_ratios(income_statements, balance_sheets)
            trends = await financial_analyzer.analyze_income_trends(income_statements)
            analysis = {
                "profitability_ratios": ratios,
                "revenue_trends": trends,
                "analysis_type": "profitability"
            }
        elif analysis_type == "cashflow":
            analysis = await financial_analyzer.analyze_cash_flow_quality(cash_flows)
        
        return {
            "ticker": ticker,
            "analysis_type": analysis_type,
            "period": period,
            "status": "success",
            "data": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except TickerNotFoundError:
        raise HTTPException(status_code=404, detail=f"Insufficient data for analysis for ticker '{ticker}'")
    
    except CalculationError as e:
        raise HTTPException(status_code=422, detail=f"Analysis calculation failed: {str(e)}")
    
    except Exception as e:
        logger.error("Unexpected error in financial analysis", 
                    ticker=ticker, analysis_type=analysis_type, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/overview/{ticker}")
async def get_financial_overview(
    ticker: str,
    current_user = Depends(require_basic_access)
):
    """
    Get a complete financial overview combining company info, key metrics, and summary analytics
    """
    try:
        logger.info("Fetching financial overview", ticker=ticker, user_id=current_user.id)
        
        # Fetch all data in parallel
        company_info = await data_provider.get_company_info(ticker)
        income_statements = await data_provider.get_income_statements(ticker, "annual", 3)
        balance_sheets = await data_provider.get_balance_sheets(ticker, "annual", 3)
        
        if not company_info or not income_statements or not balance_sheets:
            raise TickerNotFoundError(ticker)
        
        # Calculate key ratios
        key_ratios = await ratio_calculator.calculate_profitability_ratios(
            income_statements[:2], balance_sheets[:2]
        )
        
        # Basic trend analysis
        trend_analysis = await financial_analyzer.analyze_income_trends(income_statements)
        
        overview = {
            "company_info": company_info,
            "latest_financials": {
                "income_statement": income_statements[0] if income_statements else None,
                "balance_sheet": balance_sheets[0] if balance_sheets else None
            },
            "key_ratios": key_ratios.get("ratios", {}),
            "trend_analysis": trend_analysis,
            "summary": {
                "revenue_trend": trend_analysis.get("revenue_trend", "unknown"),
                "profitability_score": key_ratios.get("scores", {}).get("overall_score", 0),
                "data_quality": min(
                    income_statements[0].get("confidence_score", 0.5),
                    balance_sheets[0].get("confidence_score", 0.5)
                ) if income_statements and balance_sheets else 0.5
            }
        }
        
        return {
            "ticker": ticker,
            "status": "success",
            "data": overview,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except TickerNotFoundError:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found or insufficient data")
    
    except Exception as e:
        logger.error("Unexpected error in financial overview", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") 
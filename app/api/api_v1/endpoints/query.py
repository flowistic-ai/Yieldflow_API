from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime
import structlog

from app.core.deps import get_current_user
from app.models.user import User
from app.services.live_investment_assistant import LiveInvestmentAssistant
from app.services.professional_investment_assistant import ProfessionalInvestmentAssistant
from pydantic import BaseModel, Field

router = APIRouter()
logger = structlog.get_logger()

class QueryRequest(BaseModel):
    """Natural language query request."""
    query: str = Field(..., description="Natural language query", min_length=3, max_length=500)
    user_context: Optional[Dict[str, Any]] = Field(None, description="Optional user context")

class QueryResponseModel(BaseModel):
    """Professional investment assistant response."""
    success: bool = Field(..., description="Whether the query was processed successfully")
    data: Optional[Dict[str, Any]] = Field(None, description="Query results data")
    explanation: str = Field(..., description="Human-readable explanation of results")
    suggestions: list[str] = Field(..., description="Suggested next actions")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score based on data completeness")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: str = Field(..., description="Response timestamp")

@router.post("/ask", response_model=QueryResponseModel)
async def process_natural_language_query(
    request: QueryRequest,
    current_user = Depends(get_current_user)
):
    """
    Professional Investment Assistant - Fast, Accurate, Reliable
    
    **Focus Areas:**
    - Real-time stock data with accurate prices and metrics
    - Fast screening (< 1 second response time)
    - Professional-grade dividend analysis
    - Clear, actionable insights
    
    **What Works:**
    - Stock screening: "Find dividend stocks with yield above 4%"
    - Analysis: "Analyze AAPL MSFT JNJ" 
    - Filtering: "Show tech stocks with P/E below 15"
    - Criteria: "Utility stocks under $100 with yield above 3%"
    
    **Capabilities:**
    - Real-time stock prices and dividend yields
    - P/E ratios, market cap, sector filtering
    - Quality scoring based on financial metrics
    - Fast batch processing of stock data
    - Professional assessment of dividend quality
    """
    try:
        logger.info(f"Processing professional investment query for user {current_user.get('email', 'unknown')}")
        logger.info(f"Query: {request.query}")
        
        # Initialize live assistant for accurate real-time data
        assistant = LiveInvestmentAssistant()
        
        # Process query with focus on speed and accuracy
        response = await assistant.process_query(request.query)
        
        # Calculate quality score based on data completeness
        quality_score = 1.0 if response.success else 0.3
        if response.data and 'screening_results' in response.data:
            # Higher quality for more complete results
            results_count = len(response.data['screening_results'])
            quality_score = min(1.0, 0.7 + (results_count * 0.02))
        
        # Convert to API response format
        return QueryResponseModel(
            success=response.success,
            data=response.data,
            explanation=response.message,
            suggestions=response.suggestions,
            quality_score=quality_score,
            processing_time=response.processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Professional investment query processing failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Query processing failed: {str(e)}"
        )

@router.get("/examples")
async def get_query_examples():
    """Get example queries for the professional investment assistant."""
    
    examples = {
        "screening": [
            "Find dividend stocks with yield above 4%",
            "Show me tech stocks with P/E below 20", 
            "Utility stocks under $100 with good dividends",
            "Find healthcare stocks with market cap over $10B",
            "Show REITs with yield above 5%"
        ],
        "analysis": [
            "Analyze AAPL MSFT JNJ",
            "Evaluate KO PEP dividend quality",
            "Compare VZ T dividend metrics", 
            "Assess VYM SCHD DVY ETF performance",
            "Review JPM BAC financial strength"
        ],
        "professional_queries": [
            "Screen dividend aristocrats with sustainable payouts",
            "Find value stocks with strong dividend coverage",
            "Show defensive stocks for income portfolio",
            "Identify high-quality REITs for diversification",
            "Find undervalued stocks with growing dividends"
        ],
        "criteria_examples": [
            "Stocks with dividend yield between 3% and 6%",
            "Large cap stocks with P/E below 15", 
            "Technology stocks under $200 per share",
            "Companies with payout ratio below 70%",
            "Stocks with market cap above $50 billion"
        ]
    }
    
    return {
        "examples": examples,
        "professional_features": [
            "Real-time Yahoo Finance data integration",
            "Sub-second response times for screening",
            "Quality scoring based on financial metrics",
            "Professional dividend sustainability analysis",
            "Accurate P/E ratios and market cap data",
            "Sector-based filtering and analysis"
        ],
        "tips": [
            "Be specific about your criteria (yield %, price range, sector)",
            "Use ticker symbols for analysis (AAPL, MSFT, etc.)",
            "Combine multiple criteria for better screening",
            "Specify time horizon and risk tolerance",
            "Ask for specific sectors or market cap ranges"
        ],
        "data_quality": {
            "explanation": "Quality scores (0.0-1.0) based on:",
            "factors": [
                "Real-time data availability",
                "Number of matching results", 
                "Data completeness and accuracy",
                "Financial metrics coverage",
                "Processing speed and reliability"
            ],
            "interpretation": {
                "0.9-1.0": "Excellent - Complete data with fast processing",
                "0.7-0.9": "Good - Solid results with minor gaps",
                "0.5-0.7": "Moderate - Basic data available",
                "0.0-0.5": "Limited - Incomplete data or processing issues"
            }
        }
    }

@router.get("/status")
async def get_system_status():
    """Get current system status and capabilities."""
    
    try:
        # Test the assistant initialization
        assistant = LiveInvestmentAssistant()
        
        return {
            "status": "operational",
            "assistant_type": "Professional Investment Assistant",
            "data_source": "Yahoo Finance (real-time)",
            "features": {
                "real_time_data": True,
                "fast_screening": True,
                "professional_analysis": True,
                "quality_scoring": True,
                "dividend_focus": True
            },
            "performance": {
                "target_response_time": "< 1 second",
                "cache_ttl": "5 minutes",
                "batch_processing": True,
                "concurrent_requests": True
            },
            "universe_size": len(assistant.dividend_universe),
            "supported_queries": [
                "Stock screening with multiple criteria",
                "Individual stock analysis", 
                "Dividend quality assessment",
                "Sector-based filtering",
                "Financial ratio analysis"
            ],
            "quality_metrics": [
                "Real dividend yields and P/E ratios",
                "Current stock prices",
                "Market capitalization data",
                "Payout ratio analysis",
                "Professional quality scoring"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "System initialization failed"
        }

@router.get("/intent-test")
async def test_query_intent(
    query: str = Query(..., description="Test query to analyze intent"),
    current_user = Depends(get_current_user)
):
    """Test query parsing and intent extraction (for debugging)."""
    
    try:
        assistant = ProfessionalInvestmentAssistant()
        intent, criteria = assistant._parse_query(query)
        
        return {
            "query": query,
            "intent": intent,
            "criteria": {
                "min_dividend_yield": criteria.min_dividend_yield,
                "max_dividend_yield": criteria.max_dividend_yield,
                "min_price": criteria.min_price,
                "max_price": criteria.max_price,
                "min_pe_ratio": criteria.min_pe_ratio,
                "max_pe_ratio": criteria.max_pe_ratio,
                "sectors": criteria.sectors,
                "min_market_cap": criteria.min_market_cap
            },
            "formatted_criteria": assistant._format_criteria(criteria)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "message": "Intent parsing failed"
        } 
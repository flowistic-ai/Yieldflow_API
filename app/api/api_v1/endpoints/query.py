from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from app.core.deps import get_current_user
from app.models.user import User
from app.services.natural_language_query import NaturalLanguageQueryEngine, QueryResponse
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)

class QueryRequest(BaseModel):
    """Natural language query request."""
    query: str = Field(..., description="Natural language query", min_length=3, max_length=500)
    user_context: Optional[Dict[str, Any]] = Field(None, description="Optional user context (risk tolerance, goals, etc.)")

class QueryResponseModel(BaseModel):
    """Natural language query response."""
    success: bool = Field(..., description="Whether the query was processed successfully")
    data: Optional[Dict[str, Any]] = Field(None, description="Query results data")
    explanation: str = Field(..., description="Human-readable explanation of results")
    suggestions: list[str] = Field(..., description="Suggested next actions or improvements")
    visualization_config: Optional[Dict[str, Any]] = Field(None, description="Configuration for data visualization")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the response")
    timestamp: str = Field(..., description="Response timestamp")

@router.post("/ask", response_model=QueryResponseModel)
async def process_natural_language_query(
    request: QueryRequest,
    current_user = Depends(get_current_user)
):
    """
    Process a natural language query about portfolios, stocks, or dividends.
    
    **Examples:**
    - "Find dividend stocks with yield above 4%"
    - "Optimize a portfolio with AAPL, MSFT, JNJ"
    - "Analyze TSLA dividend quality"
    - "Show me technology stocks under $100"
    - "Create a balanced portfolio for retirement"
    
    **Capabilities:**
    - Stock screening with natural language criteria
    - Portfolio optimization and allocation
    - Individual stock analysis and evaluation
    - Investment recommendations based on goals
    - Risk assessment and comparison
    """
    try:
        logger.info(f"Processing natural language query for user {current_user.get('email', 'unknown')}")
        logger.info(f"Query: {request.query}")
        
        # Initialize the query engine
        query_engine = NaturalLanguageQueryEngine()
        
        # Process the query
        response = await query_engine.process_query(
            query=request.query,
            user_context=request.user_context
        )
        
        # Convert to response model
        return QueryResponseModel(
            success=response.success,
            data=response.data,
            explanation=response.explanation,
            suggestions=response.suggestions,
            visualization_config=response.visualization_config,
            confidence=response.confidence,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Natural language query processing failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Query processing failed: {str(e)}"
        )

@router.get("/examples")
async def get_query_examples():
    """Get example queries to help users understand capabilities."""
    
    examples = {
        "screening": [
            "Find dividend stocks with yield above 4%",
            "Show me technology stocks under $100",
            "Search for defensive stocks in healthcare sector",
            "Filter stocks with market cap over $10 billion",
            "Find value stocks with PE ratio below 15"
        ],
        "optimization": [
            "Optimize a portfolio with AAPL, MSFT, JNJ",
            "Create a balanced portfolio for income",
            "Build an optimal mix of dividend stocks",
            "Rebalance my portfolio for maximum Sharpe ratio",
            "Optimize allocation for dividend growth"
        ],
        "analysis": [
            "Analyze AAPL dividend quality",
            "Evaluate TSLA risk profile",
            "How good is JNJ for dividend investing?",
            "Assess portfolio risk and diversification",
            "What are the strengths of Microsoft stock?"
        ],
        "advanced": [
            "I need $500 monthly income with low risk",
            "Find conservative stocks for retirement",
            "What's the best dividend ETF alternative?",
            "Compare AAPL vs MSFT for dividend growth",
            "Recommend stocks for aggressive growth strategy"
        ]
    }
    
    return {
        "examples": examples,
        "tips": [
            "Be specific about your criteria (yield, price, sector)",
            "Include stock tickers when you have specific stocks in mind",
            "Mention your investment goals (income, growth, balanced)",
            "Specify risk tolerance (conservative, moderate, aggressive)",
            "Ask follow-up questions to dive deeper into results"
        ],
        "capabilities": [
            "Stock screening and filtering",
            "Portfolio optimization and allocation",
            "Individual stock analysis",
            "Risk assessment and evaluation",
            "Investment recommendations",
            "AI-powered insights and explanations"
        ]
    }

@router.get("/intent-test")
async def test_query_intent(
    query: str = Query(..., description="Test query to analyze intent"),
    current_user = Depends(get_current_user)
):
    """
    Test endpoint to understand how a query would be interpreted.
    Useful for debugging and understanding the query parsing logic.
    """
    try:
        query_engine = NaturalLanguageQueryEngine()
        intent = await query_engine._parse_query_intent(query)
        
        return {
            "query": query,
            "parsed_intent": {
                "action": intent.action,
                "confidence": intent.confidence,
                "parameters": intent.parameters,
                "explanation": intent.explanation,
                "requires_confirmation": intent.requires_confirmation
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Intent testing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Intent analysis failed: {str(e)}"
        ) 
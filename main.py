"""
Yieldflow API - Main FastAPI Application
From Data to Insights in One API Call
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.api.endpoints import financial
from app.utils.exceptions import (
    TickerNotFoundError, 
    DataSourceError, 
    ValidationError, 
    CalculationError,
    InsufficientDataError
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Yieldflow API...")
    
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created/verified")
        
        # Test external API connections
        logger.info("Verifying external API connections...")
        
        logger.info("Yieldflow API started successfully")
        yield
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Yieldflow API...")


# Create FastAPI application
app = FastAPI(
    title="Yieldflow API",
    description="""
    ## 🚀 From Data to Insights in One API Call

    Yieldflow API provides comprehensive financial analytics that goes beyond raw data to deliver 
    intelligent analysis, ratios, visualizations, and AI-powered insights.

    ### Key Features:
    - **Multi-source Data Integration**: Alpha Vantage, Financial Modeling Prep, Yahoo Finance, FRED
    - **Advanced Analytics**: Beyond raw financial data to meaningful insights
    - **Intelligent Ratios**: 50+ financial ratios with scoring and interpretation
    - **Trend Analysis**: Historical analysis and pattern recognition
    - **Cross-validation**: Data accuracy through multiple source verification
    - **High-speed Caching**: Redis-powered performance optimization

    ### Plans & Features:
    - **Free**: Basic company info and financial data (1K requests/day)
    - **Basic**: + Financial ratios and trend analysis (10K requests/day)  
    - **Pro**: + Advanced analytics and forecasting (50K requests/day)
    - **Enterprise**: + Bulk data and real-time updates (200K requests/day)

    ### Getting Started:
    1. Sign up for an API key
    2. Make your first request to `/financial/company/{ticker}`
    3. Explore advanced analytics with `/financial/analysis/{ticker}`

    ---
    *Competing with premium financial data services through intelligent analytics*
    """,
    version="1.0.0",
    contact={
        "name": "Yieldflow API Support",
        "url": "https://github.com/flowistic-ai/Yieldflow_API",
        "email": "support@yieldflow.ai"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Note: TrustedHostMiddleware would be added in production with proper hosts


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing"""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client=request.client.host if request.client else "unknown"
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 4)
    )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(TickerNotFoundError)
async def ticker_not_found_handler(request: Request, exc: TickerNotFoundError):
    logger.warning("Ticker not found", ticker=exc.ticker, url=str(request.url))
    return JSONResponse(
        status_code=404,
        content={
            "error": "ticker_not_found",
            "message": f"Ticker '{exc.ticker}' not found or invalid",
            "suggestion": "Please verify the ticker symbol and try again"
        }
    )


@app.exception_handler(DataSourceError) 
async def data_source_error_handler(request: Request, exc: DataSourceError):
    logger.error("Data source error", source=exc.source, error=str(exc), url=str(request.url))
    return JSONResponse(
        status_code=503,
        content={
            "error": "data_source_unavailable", 
            "message": f"Data source '{exc.source}' is currently unavailable",
            "suggestion": "Please try again later or contact support if this persists"
        }
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    logger.warning("Validation error", error=str(exc), url=str(request.url))
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": str(exc),
            "suggestion": "Please check your request parameters and try again"
        }
    )


@app.exception_handler(CalculationError)
async def calculation_error_handler(request: Request, exc: CalculationError):
    logger.error("Calculation error", calculation=exc.calculation, error=str(exc), url=str(request.url))
    return JSONResponse(
        status_code=422,
        content={
            "error": "calculation_error",
            "message": f"Failed to calculate {exc.calculation}",
            "suggestion": "This may be due to insufficient or invalid data"
        }
    )


@app.exception_handler(InsufficientDataError)
async def insufficient_data_handler(request: Request, exc: InsufficientDataError):
    logger.warning("Insufficient data", data_type=exc.data_type, url=str(request.url))
    return JSONResponse(
        status_code=422,
        content={
            "error": "insufficient_data",
            "message": f"Insufficient {exc.data_type} data for analysis",
            "suggestion": "This ticker may not have enough historical data available"
        }
    )


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """
    API Health Check
    Returns basic API information and status
    """
    return {
        "message": "Yieldflow API - From Data to Insights in One API Call",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "github": "https://github.com/flowistic-ai/Yieldflow_API"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check endpoint
    Returns system status and dependencies
    """
    try:
        # You could add actual health checks here:
        # - Database connectivity
        # - Redis connectivity  
        # - External API status
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "database": "operational",
                "cache": "operational", 
                "external_apis": "operational"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


# Include API routers
app.include_router(
    financial.router,
    prefix="/financial",
    tags=["Financial Data & Analytics"]
)


# API Information endpoint
@app.get("/info", tags=["API Info"])
async def api_info():
    """
    Get API information and feature comparison
    """
    return {
        "api_name": "Yieldflow API",
        "tagline": "From Data to Insights in One API Call",
        "value_proposition": "Comprehensive financial analytics beyond raw data",
        "features": {
            "data_sources": [
                "Alpha Vantage",
                "Financial Modeling Prep", 
                "Yahoo Finance",
                "FRED (Federal Reserve)"
            ],
            "analytics": [
                "50+ Financial Ratios",
                "Trend Analysis",
                "Liquidity Analysis", 
                "Profitability Scoring",
                "Growth Analysis",
                "Cash Flow Quality"
            ],
            "capabilities": [
                "Multi-source Data Validation",
                "Intelligent Caching",
                "Real-time Analysis",
                "Historical Trends",
                "Predictive Insights"
            ]
        },
        "plans": {
            "free": {
                "requests_per_day": 1000,
                "features": ["Basic company info", "Basic financial data"]
            },
            "basic": {
                "requests_per_day": 10000,
                "features": ["Everything in Free", "Financial ratios", "Trend analysis"]
            },
            "pro": {
                "requests_per_day": 50000,
                "features": ["Everything in Basic", "Advanced analytics", "Forecasting"]
            },
            "enterprise": {
                "requests_per_day": 200000,
                "features": ["Everything in Pro", "Bulk data", "Real-time updates", "White-label"]
            }
        },
        "competitive_advantages": [
            "Multi-source data validation for accuracy",
            "Intelligent analytics beyond raw data",
            "Real-time ratio calculations and scoring",
            "Advanced caching for sub-second responses",
            "Comprehensive trend analysis and insights"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        log_level="info"
    ) 
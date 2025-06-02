from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import structlog

from app.core.config import settings, validate_api_keys
from app.core.database import init_db, close_db
from app.api.api_v1.api import api_router
from app.utils.exceptions import YieldflowException

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

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Add CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add trusted host middleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all requests and responses"""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        headers=dict(request.headers),
        client_ip=request.client.host,
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=process_time,
    )
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


@app.exception_handler(YieldflowException)
async def yieldflow_exception_handler(request: Request, exc: YieldflowException):
    """Handle custom Yieldflow exceptions"""
    logger.error(
        "YieldflowException occurred",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        url=str(request.url),
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(
        "Unhandled exception occurred",
        exception=str(exc),
        exception_type=type(exc).__name__,
        url=str(request.url),
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": str(exc) if settings.DEBUG else None,
            }
        },
    )


@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("Starting Yieldflow API", version=settings.VERSION)
    
    # Validate API keys
    try:
        validate_api_keys()
        logger.info("API key validation successful")
    except Exception as e:
        logger.warning("API key validation warning", error=str(e))
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialization successful")
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise
    
    logger.info("Yieldflow API startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down Yieldflow API")
    
    # Close database connections
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database connections", error=str(e))
    
    logger.info("Yieldflow API shutdown completed")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": time.time(),
    }


# API status endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.DESCRIPTION,
        "docs_url": f"{settings.API_V1_STR}/docs",
        "api_v1_prefix": settings.API_V1_STR,
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 
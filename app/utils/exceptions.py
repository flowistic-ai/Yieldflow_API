from typing import Optional, Dict, Any


class YieldflowException(Exception):
    """Base exception class for Yieldflow API"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(YieldflowException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class DataSourceError(YieldflowException):
    """Raised when external data source fails"""
    
    def __init__(self, message: str, source: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Data source error from {source}: {message}",
            error_code="DATA_SOURCE_ERROR",
            status_code=503,
            details={"source": source, **(details or {})}
        )


class CalculationError(YieldflowException):
    """Raised when financial calculation fails"""
    
    def __init__(self, message: str, calculation_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Calculation error in {calculation_type}: {message}",
            error_code="CALCULATION_ERROR",
            status_code=422,
            details={"calculation_type": calculation_type, **(details or {})}
        )


class InsufficientDataError(YieldflowException):
    """Raised when insufficient data is available for analysis"""
    
    def __init__(self, message: str, required_periods: int, available_periods: int):
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_DATA",
            status_code=400,
            details={
                "required_periods": required_periods,
                "available_periods": available_periods
            }
        )


class TickerNotFoundError(YieldflowException):
    """Raised when ticker symbol is not found"""
    
    def __init__(self, ticker: str):
        super().__init__(
            message=f"Ticker '{ticker}' not found or not supported",
            error_code="TICKER_NOT_FOUND",
            status_code=404,
            details={"ticker": ticker}
        )


class RateLimitExceededError(YieldflowException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, plan: str, limit_type: str, reset_time: int):
        super().__init__(
            message=f"Rate limit exceeded for {plan} plan",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={
                "plan": plan,
                "limit_type": limit_type,
                "reset_time": reset_time
            }
        )


class FeatureNotAvailableError(YieldflowException):
    """Raised when feature is not available in user's plan"""
    
    def __init__(self, feature: str, current_plan: str, required_plan: str):
        super().__init__(
            message=f"Feature '{feature}' requires {required_plan} plan or higher",
            error_code="FEATURE_NOT_AVAILABLE",
            status_code=403,
            details={
                "feature": feature,
                "current_plan": current_plan,
                "required_plan": required_plan
            }
        )


class CacheError(YieldflowException):
    """Raised when cache operation fails"""
    
    def __init__(self, message: str, operation: str):
        super().__init__(
            message=f"Cache {operation} failed: {message}",
            error_code="CACHE_ERROR",
            status_code=500,
            details={"operation": operation}
        )


class AIServiceError(YieldflowException):
    """Raised when AI service fails"""
    
    def __init__(self, message: str, service: str, model_version: str):
        super().__init__(
            message=f"AI service error from {service}: {message}",
            error_code="AI_SERVICE_ERROR",
            status_code=503,
            details={
                "service": service,
                "model_version": model_version
            }
        )


class ComplianceError(YieldflowException):
    """Raised when compliance check fails"""
    
    def __init__(self, message: str, regulation: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Compliance error for {regulation}: {message}",
            error_code="COMPLIANCE_ERROR",
            status_code=400,
            details={"regulation": regulation, **(details or {})}
        )

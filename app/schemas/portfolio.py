from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class OptimizationObjective(str, Enum):
    """Optimization objectives for dividend portfolios."""
    SHARPE_RATIO = "sharpe_ratio"
    DIVIDEND_YIELD = "dividend_yield"
    DIVIDEND_GROWTH = "dividend_growth"
    BALANCED = "balanced"

class ShrinkageMethod(str, Enum):
    """Shrinkage parameter selection methods."""
    AUTO = "auto"
    FIXED = "fixed"
    CUSTOM = "custom"

class AssetContribution(BaseModel):
    """Individual asset contribution to portfolio metrics."""
    weight: float = Field(..., ge=0, le=1, description="Portfolio weight")
    return_contribution: float = Field(..., description="Contribution to portfolio return")
    risk_contribution: float = Field(..., description="Contribution to portfolio risk")
    dividend_yield: float = Field(..., ge=0, description="Asset dividend yield")
    dividend_growth: float = Field(..., description="Asset dividend growth rate")
    quality_score: float = Field(..., ge=0, le=1, description="Dividend quality score")

class RiskMetrics(BaseModel):
    """Portfolio risk metrics."""
    max_weight: float = Field(..., ge=0, le=1, description="Maximum individual position size")
    effective_positions: float = Field(..., gt=0, description="Effective number of positions")
    concentration_risk: float = Field(..., ge=0, description="Concentration risk measure")
    avg_dividend_consistency: float = Field(..., ge=0, le=1, description="Average dividend consistency score")

class PortfolioOptimizationResult(BaseModel):
    """Results from portfolio optimization."""
    weights: Dict[str, float] = Field(..., description="Optimized portfolio weights")
    expected_return: float = Field(..., description="Expected portfolio return")
    volatility: float = Field(..., gt=0, description="Expected portfolio volatility")
    sharpe_ratio: float = Field(..., description="Portfolio Sharpe ratio")
    expected_dividend_yield: float = Field(..., ge=0, description="Expected portfolio dividend yield")
    risk_metrics: RiskMetrics = Field(..., description="Portfolio risk metrics")
    individual_contributions: Dict[str, AssetContribution] = Field(..., description="Individual asset contributions")
    optimization_method: str = Field(..., description="Optimization method used")
    shrinkage_parameter: float = Field(..., ge=0, le=1, description="EPO shrinkage parameter used")

class PortfolioOptimizationRequest(BaseModel):
    """Request for portfolio optimization."""
    tickers: List[str] = Field(..., min_items=2, max_items=20, description="List of stock tickers")
    objective: OptimizationObjective = Field(OptimizationObjective.SHARPE_RATIO, description="Optimization objective")
    shrinkage_method: ShrinkageMethod = Field(ShrinkageMethod.AUTO, description="Shrinkage parameter method")
    shrinkage_value: Optional[float] = Field(None, ge=0, le=1, description="Custom shrinkage value (if method=custom)")
    anchor_portfolio: Optional[Dict[str, float]] = Field(None, description="Optional anchor portfolio weights")
    max_weight: Optional[float] = Field(0.3, ge=0.05, le=0.5, description="Maximum weight per asset")
    min_dividend_yield: Optional[float] = Field(0.01, ge=0, description="Minimum dividend yield filter")

class EfficientFrontierPoint(BaseModel):
    """Point on the efficient frontier."""
    expected_return: float = Field(..., description="Expected return")
    volatility: float = Field(..., gt=0, description="Volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    weights: Dict[str, float] = Field(..., description="Portfolio weights")

class EfficientFrontier(BaseModel):
    """Efficient frontier for dividend portfolios."""
    frontier_points: List[EfficientFrontierPoint] = Field(..., description="Points on the efficient frontier")
    risk_free_rate: float = Field(..., description="Risk-free rate used")
    max_sharpe_portfolio: EfficientFrontierPoint = Field(..., description="Maximum Sharpe ratio portfolio")

class PortfolioComparison(BaseModel):
    """Comparison between portfolio optimization methods."""
    epo_portfolio: PortfolioOptimizationResult = Field(..., description="EPO optimized portfolio")
    equal_weight_portfolio: PortfolioOptimizationResult = Field(..., description="Equal weight benchmark")
    traditional_mvo: Optional[PortfolioOptimizationResult] = Field(None, description="Traditional MVO portfolio")
    performance_improvement: Dict[str, float] = Field(..., description="Performance improvements vs benchmarks")

class BacktestResult(BaseModel):
    """Portfolio backtest results."""
    dates: List[str] = Field(..., description="Backtest dates")
    portfolio_values: List[float] = Field(..., description="Portfolio values over time")
    benchmark_values: List[float] = Field(..., description="Benchmark values over time")
    returns: List[float] = Field(..., description="Portfolio returns")
    cumulative_dividends: List[float] = Field(..., description="Cumulative dividends received")
    sharpe_ratio: float = Field(..., description="Realized Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    total_return: float = Field(..., description="Total return")
    dividend_income: float = Field(..., description="Total dividend income")

class PortfolioRiskAnalysis(BaseModel):
    """Comprehensive portfolio risk analysis."""
    var_95: float = Field(..., description="95% Value at Risk")
    cvar_95: float = Field(..., description="95% Conditional Value at Risk")
    beta: float = Field(..., description="Portfolio beta")
    correlation_with_market: float = Field(..., description="Correlation with market")
    sector_concentration: Dict[str, float] = Field(..., description="Sector concentration")
    top_10_holdings_weight: float = Field(..., description="Weight of top 10 holdings")
    
class OptimizationConstraints(BaseModel):
    """Portfolio optimization constraints."""
    max_weight_per_stock: Optional[float] = Field(0.3, ge=0.05, le=0.5)
    min_weight_per_stock: Optional[float] = Field(0.0, ge=0.0, le=0.1)
    max_sector_weight: Optional[float] = Field(0.4, ge=0.1, le=0.8)
    min_dividend_yield: Optional[float] = Field(0.01, ge=0.0)
    max_volatility: Optional[float] = Field(None, gt=0)
    min_quality_score: Optional[float] = Field(None, ge=0, le=1)
    rebalance_threshold: Optional[float] = Field(0.05, ge=0.01, le=0.2)

class PortfolioInsights(BaseModel):
    """AI-generated portfolio insights and recommendations."""
    summary: str = Field(..., description="Portfolio summary")
    strengths: List[str] = Field(..., description="Portfolio strengths")
    risks: List[str] = Field(..., description="Portfolio risks")
    recommendations: List[str] = Field(..., description="Optimization recommendations")
    diversification_score: float = Field(..., ge=0, le=10, description="Diversification score (1-10)")
    quality_score: float = Field(..., ge=0, le=10, description="Overall quality score (1-10)")
    esg_score: Optional[float] = Field(None, ge=0, le=10, description="ESG score if available")

class PortfolioOptimizationFullResult(BaseModel):
    """Complete portfolio optimization results with analysis."""
    optimization_result: PortfolioOptimizationResult = Field(..., description="Core optimization results")
    efficient_frontier: Optional[EfficientFrontier] = Field(None, description="Efficient frontier")
    comparison: Optional[PortfolioComparison] = Field(None, description="Method comparison")
    risk_analysis: Optional[PortfolioRiskAnalysis] = Field(None, description="Risk analysis")
    backtest: Optional[BacktestResult] = Field(None, description="Historical backtest")
    insights: Optional[PortfolioInsights] = Field(None, description="AI insights")
    timestamp: str = Field(..., description="Analysis timestamp") 
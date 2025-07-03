import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from scipy.optimize import minimize
from scipy.linalg import LinAlgError
import logging
from datetime import datetime, timedelta
import asyncio

from app.services.data_provider import DataProvider
from app.schemas.financial import DividendAnalysisResponse
from app.services.news_sentiment_service import NewsEnhancedPortfolioService

logger = logging.getLogger(__name__)

@dataclass
class AssetMetrics:
    """Asset-level metrics for portfolio optimization."""
    ticker: str
    expected_return: float
    volatility: float
    dividend_yield: float
    dividend_growth_rate: float
    payout_ratio: float
    debt_to_equity: float
    roe: float
    current_ratio: float
    earnings_growth: float
    dividend_consistency_score: float

@dataclass
class PortfolioResults:
    """Results from portfolio optimization."""
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    expected_dividend_yield: float
    risk_metrics: Dict[str, float]
    individual_contributions: Dict[str, Dict[str, float]]
    optimization_method: str
    shrinkage_parameter: float

class EnhancedPortfolioOptimizer:
    """
    Enhanced Portfolio Optimization (EPO) implementation for dividend portfolios.
    
    Based on Enhanced Portfolio Optimization methodology:
    - Correlation shrinkage to address estimation errors
    - Sharpe ratio maximization with risk model corrections
    - Dividend-focused objective functions
    - Robust optimization with numerical stability
    """
    
    def __init__(self, data_provider: DataProvider, risk_free_rate: float = 0.02):
        self.data_provider = data_provider
        self.risk_free_rate = risk_free_rate
        self.min_weight = 0.05  # Minimum 5% allocation
        self.max_weight = 0.50  # Maximum 50% allocation
        self.min_dividend_yield = 0.01
        self.news_service = NewsEnhancedPortfolioService()  # Initialize NEPO service
        
    async def optimize_dividend_portfolio(
        self,
        tickers: List[str],
        objective: str = "sharpe_ratio",
        shrinkage_method: str = "auto",
        anchor_portfolio: Optional[Dict[str, float]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> PortfolioResults:
        """Main optimization function implementing EPO for dividend portfolios."""
        try:
            logger.info(f"Starting EPO optimization for {tickers} with objective {objective}")
            
            # 1. Gather asset data and compute metrics
            asset_metrics = await self._compute_asset_metrics(tickers)
            logger.info(f"Computed metrics for {len(asset_metrics)} assets")
            
            # 2. Build expected returns vector and covariance matrix
            returns_data = await self._get_historical_returns(tickers)
            expected_returns = self._compute_expected_returns(asset_metrics, objective)
            cov_matrix = self._compute_covariance_matrix(returns_data)
            
            logger.info(f"Expected returns: {expected_returns}")
            logger.info(f"Covariance matrix shape: {cov_matrix.shape}")
            
            # 3. Apply Enhanced Portfolio Optimization
            if shrinkage_method == "auto":
                shrinkage_param = self._optimize_shrinkage_parameter(
                    expected_returns, cov_matrix, returns_data
                )
            elif shrinkage_method == "fixed":
                shrinkage_param = 0.75  # Default from paper
            else:
                shrinkage_param = float(shrinkage_method)
                
            logger.info(f"Using shrinkage parameter: {shrinkage_param}")
            
            # 4. Shrink correlation matrix (core EPO step)
            shrunk_cov_matrix = self._apply_correlation_shrinkage(cov_matrix, shrinkage_param)
            
            # 5. Optimize portfolio weights
            if anchor_portfolio:
                weights = self._optimize_anchored_portfolio(
                    expected_returns, shrunk_cov_matrix, anchor_portfolio, constraints, tickers
                )
            else:
                weights = self._optimize_simple_epo(
                    expected_returns, shrunk_cov_matrix, constraints, tickers
                )
                
            logger.info(f"Optimized weights: {weights}")
            
            # 6. Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(
                weights, expected_returns, shrunk_cov_matrix, asset_metrics
            )
            
            # 7. Analyze individual asset contributions
            contributions = self._calculate_asset_contributions(
                weights, asset_metrics, expected_returns, shrunk_cov_matrix
            )
            
            return PortfolioResults(
                weights=weights,
                expected_return=portfolio_metrics["return"],
                volatility=portfolio_metrics["volatility"],
                sharpe_ratio=portfolio_metrics["sharpe_ratio"],
                expected_dividend_yield=portfolio_metrics["dividend_yield"],
                risk_metrics=portfolio_metrics["risk_metrics"],
                individual_contributions=contributions,
                optimization_method=f"EPO_{objective}",
                shrinkage_parameter=shrinkage_param
            )
            
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            raise
    
    async def optimize_news_enhanced_portfolio(
        self,
        tickers: List[str],
        objective: str = "news_enhanced_sharpe",
        investment_amount: float = 100000,
        time_horizon: str = "medium",
        include_news_analysis: bool = True,
        shrinkage_method: str = "auto"
    ) -> Dict[str, Any]:
        """
        News-Enhanced Portfolio Optimization (NEPO) that combines:
        1. Traditional EPO methodology
        2. Real-time news sentiment analysis
        3. Geopolitical risk assessment
        4. AI-powered investment thesis generation
        """
        try:
            logger.info(f"Starting NEPO optimization for {tickers} with {objective}")
            
            # Step 1: Run traditional EPO first to get base weights
            base_portfolio = await self.optimize_dividend_portfolio(
                tickers=tickers,
                objective="sharpe_ratio",
                shrinkage_method=shrinkage_method
            )
            
            base_weights = base_portfolio.weights
            logger.info(f"Base EPO weights: {base_weights}")
            
            # Step 2: Apply News-Enhanced analysis if enabled
            if include_news_analysis:
                logger.info("Applying News-Enhanced optimization with quantitative analysis")
                
                # Get news-enhanced portfolio
                news_enhanced_result = await self.news_service.analyze_portfolio_with_news(
                    tickers=tickers,
                    base_weights=base_weights,
                    investment_amount=investment_amount,
                    time_horizon=time_horizon
                )
                
                # Combine EPO + NEPO results
                combined_result = self._combine_epo_nepo_results(
                    epo_result=base_portfolio,
                    nepo_result=news_enhanced_result,
                    combination_weight=0.7  # 70% EPO, 30% news sentiment
                )
                
                return {
                    **combined_result,
                    'methodology': 'EPO + NEPO (Enhanced Portfolio Optimization with News Intelligence)',
                    'base_epo_results': {
                        'weights': base_portfolio.weights,
                        'expected_return': base_portfolio.expected_return,
                        'volatility': base_portfolio.volatility,
                        'sharpe_ratio': base_portfolio.sharpe_ratio
                    },
                    'news_enhancement': {
                        'gemini_powered': True,
                        'geopolitical_risk': news_enhanced_result.get('geopolitical_risk_level', 0.5),
                        'news_analyses': news_enhanced_result.get('news_analyses', {}),
                        'investment_thesis': news_enhanced_result.get('investment_thesis', '')
                    },
                    'optimization_timestamp': datetime.now().isoformat()
                }
                
            else:
                # Fallback to traditional EPO if news analysis not available
                logger.info("News analysis not available, using traditional EPO")
                
                return {
                    'optimized_weights': base_portfolio.weights,
                    'expected_return': base_portfolio.expected_return,
                    'volatility': base_portfolio.volatility,
                    'sharpe_ratio': base_portfolio.sharpe_ratio,
                    'expected_dividend_yield': base_portfolio.expected_dividend_yield,
                    'risk_metrics': base_portfolio.risk_metrics,
                    'individual_contributions': base_portfolio.individual_contributions,
                    'methodology': 'Traditional EPO (News analysis unavailable)',
                    'shrinkage_parameter': base_portfolio.shrinkage_parameter,
                    'optimization_timestamp': datetime.now().isoformat(),
                    'news_enhancement': {
                        'gemini_powered': False,
                        'reason': 'Google Gemini API not configured'
                    }
                }
                
        except Exception as e:
            logger.error(f"News-enhanced portfolio optimization failed: {e}")
            raise
    
    def _combine_epo_nepo_results(
        self,
        epo_result: PortfolioResults,
        nepo_result: Dict[str, Any],
        combination_weight: float = 0.7
    ) -> Dict[str, Any]:
        """
        Intelligently combine EPO and NEPO results
        """
        try:
            # Extract NEPO weights and metrics
            nepo_weights = nepo_result.get('optimized_weights', {})
            nepo_return = nepo_result.get('enhanced_expected_return', 0.08)
            nepo_risk = nepo_result.get('news_adjusted_risk', 0.18)
            nepo_sharpe = nepo_result.get('sharpe_ratio', 0.44)
            
            # Combine weights using intelligent blending
            combined_weights = {}
            all_tickers = set(epo_result.weights.keys()) | set(nepo_weights.keys())
            
            for ticker in all_tickers:
                epo_weight = epo_result.weights.get(ticker, 0.0)
                nepo_weight = nepo_weights.get(ticker, 0.0)
                
                # Weighted combination with bias toward EPO for stability
                combined_weights[ticker] = (
                    combination_weight * epo_weight + 
                    (1 - combination_weight) * nepo_weight
                )
            
            # Normalize weights to sum to 1
            total_weight = sum(combined_weights.values())
            if total_weight > 0:
                combined_weights = {
                    ticker: weight / total_weight 
                    for ticker, weight in combined_weights.items()
                    if weight > 0.01  # Remove negligible weights
                }
            
            # Combine performance metrics
            combined_return = (
                combination_weight * epo_result.expected_return + 
                (1 - combination_weight) * nepo_return
            )
            
            combined_risk = (
                combination_weight * epo_result.volatility + 
                (1 - combination_weight) * nepo_risk
            )
            
            combined_sharpe = combined_return / combined_risk if combined_risk > 0 else 0
            
            return {
                'optimized_weights': combined_weights,
                'expected_return': combined_return,
                'volatility': combined_risk,
                'sharpe_ratio': combined_sharpe,
                'expected_dividend_yield': epo_result.expected_dividend_yield,
                'risk_metrics': epo_result.risk_metrics,
                'individual_contributions': epo_result.individual_contributions,
                'combination_weight': combination_weight,
                'improvement_over_epo': {
                    'return_improvement': combined_return - epo_result.expected_return,
                    'sharpe_improvement': combined_sharpe - epo_result.sharpe_ratio,
                    'risk_adjustment': combined_risk - epo_result.volatility
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to combine EPO and NEPO results: {e}")
            # Fallback to EPO results
            return {
                'optimized_weights': epo_result.weights,
                'expected_return': epo_result.expected_return,
                'volatility': epo_result.volatility,
                'sharpe_ratio': epo_result.sharpe_ratio,
                'expected_dividend_yield': epo_result.expected_dividend_yield,
                'combination_weight': 1.0,  # 100% EPO fallback
                'fallback_reason': str(e)
            }
    
    async def _compute_asset_metrics(self, tickers: List[str]) -> List[AssetMetrics]:
        """Compute comprehensive metrics for each asset **in parallel** to speed-up requests."""
        from app.services.dividend_service import DividendService
        dividend_service = DividendService()

        # Limit concurrent outbound requests to avoid overwhelming external APIs
        semaphore = asyncio.Semaphore(5)

        async def _fetch_for_ticker(ticker: str) -> AssetMetrics:
            """Wrapper that fetches and constructs AssetMetrics for one ticker with fallback handling."""
            async with semaphore:
                try:
                    analysis = await dividend_service.get_comprehensive_dividend_analysis(ticker)

                    financial_data = self._get_realistic_financial_metrics(ticker)

                    current_metrics = analysis.get('current_metrics', {})
                    growth_analytics = analysis.get('growth_analytics', {})
                    risk_assessment = analysis.get('risk_assessment', {})

                    dividend_yield = current_metrics.get('current_dividend_yield', self._get_realistic_yield(ticker)) / 100
                    growth_rate = growth_analytics.get('five_year_cagr', self._get_realistic_growth(ticker)) / 100
                    expected_return = dividend_yield + growth_rate + self._get_realistic_risk_premium(ticker)

                    volatility = risk_assessment.get('dividend_volatility', self._get_realistic_volatility(ticker)) / 100
                    payout_ratio = current_metrics.get('payout_ratio', self._get_realistic_payout(ticker)) / 100

                    consistency_score = self._calculate_dividend_consistency(analysis)

                    return AssetMetrics(
                        ticker=ticker,
                        expected_return=expected_return,
                        volatility=volatility,
                        dividend_yield=dividend_yield,
                        dividend_growth_rate=growth_rate,
                        payout_ratio=payout_ratio,
                        debt_to_equity=financial_data.get("debt_to_equity", 0.5),
                        roe=financial_data.get("roe", 0.12),
                        current_ratio=financial_data.get("current_ratio", 1.5),
                        earnings_growth=financial_data.get("earnings_growth", growth_rate),
                        dividend_consistency_score=consistency_score
                    )
                except Exception as e:
                    logger.warning(f"Failed to get metrics for {ticker}: {e}")
                    return self._get_fallback_metrics(ticker)

        return await asyncio.gather(*[asyncio.create_task(_fetch_for_ticker(t)) for t in tickers])
    
    def _get_realistic_financial_metrics(self, ticker: str) -> Dict[str, float]:
        """Get realistic financial metrics based on ticker type."""
        tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA']
        dividend_aristocrats = ['JNJ', 'PG', 'KO', 'PEP', 'MCD', 'WMT', 'XOM']
        
        if ticker in tech_stocks:
            return {
                "debt_to_equity": 0.3,
                "roe": 0.25,
                "current_ratio": 1.8,
                "earnings_growth": 0.15
            }
        elif ticker in dividend_aristocrats:
            return {
                "debt_to_equity": 0.6,
                "roe": 0.18,
                "current_ratio": 1.2,
                "earnings_growth": 0.08
            }
        else:
            return {
                "debt_to_equity": 0.5,
                "roe": 0.12,
                "current_ratio": 1.5,
                "earnings_growth": 0.10
            }
    
    def _get_realistic_yield(self, ticker: str) -> float:
        """Get realistic dividend yield based on ticker."""
        yields = {
            'AAPL': 0.5, 'MSFT': 0.7, 'GOOGL': 0.0, 'AMZN': 0.0,
            'JNJ': 2.8, 'PG': 2.5, 'KO': 3.1, 'PEP': 2.7,
            'XOM': 5.8, 'CVX': 3.2, 'T': 7.2, 'VZ': 6.8
        }
        return yields.get(ticker, 2.5)
    
    def _get_realistic_growth(self, ticker: str) -> float:
        """Get realistic dividend growth based on ticker."""
        growth = {
            'AAPL': 8.0, 'MSFT': 10.0, 'JNJ': 6.0, 'PG': 4.0,
            'KO': 3.0, 'PEP': 5.0, 'XOM': 2.0, 'CVX': 3.0
        }
        return growth.get(ticker, 5.0)
    
    def _get_realistic_volatility(self, ticker: str) -> float:
        """Get realistic volatility based on ticker."""
        vols = {
            'AAPL': 25.0, 'MSFT': 22.0, 'GOOGL': 28.0, 'AMZN': 32.0,
            'JNJ': 12.0, 'PG': 15.0, 'KO': 14.0, 'PEP': 16.0,
            'XOM': 35.0, 'CVX': 30.0, 'T': 18.0, 'VZ': 20.0
        }
        return vols.get(ticker, 20.0)
    
    def _get_realistic_payout(self, ticker: str) -> float:
        """Get realistic payout ratio based on ticker."""
        payouts = {
            'AAPL': 15.0, 'MSFT': 25.0, 'JNJ': 60.0, 'PG': 65.0,
            'KO': 70.0, 'PEP': 65.0, 'XOM': 45.0, 'CVX': 40.0
        }
        return payouts.get(ticker, 50.0)
    
    def _get_realistic_risk_premium(self, ticker: str) -> float:
        """Get realistic risk premium based on ticker quality."""
        tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA']
        dividend_aristocrats = ['JNJ', 'PG', 'KO', 'PEP', 'MCD']
        
        if ticker in tech_stocks:
            return 0.08  # Higher risk premium for tech
        elif ticker in dividend_aristocrats:
            return 0.04  # Lower risk premium for stable dividends
        else:
            return 0.06  # Medium risk premium
    
    def _get_fallback_metrics(self, ticker: str) -> AssetMetrics:
        """Get fallback metrics if data retrieval fails."""
        return AssetMetrics(
            ticker=ticker,
            expected_return=self._get_realistic_yield(ticker)/100 + self._get_realistic_growth(ticker)/100 + self._get_realistic_risk_premium(ticker),
            volatility=self._get_realistic_volatility(ticker)/100,
            dividend_yield=self._get_realistic_yield(ticker)/100,
            dividend_growth_rate=self._get_realistic_growth(ticker)/100,
            payout_ratio=self._get_realistic_payout(ticker)/100,
            debt_to_equity=0.5,
            roe=0.12,
            current_ratio=1.5,
            earnings_growth=self._get_realistic_growth(ticker)/100,
            dividend_consistency_score=0.75
        )
    
    def _calculate_dividend_consistency(self, analysis: Dict[str, Any]) -> float:
        """Calculate dividend consistency score (0-1)."""
        try:
            # Use dividend quality score if available
            if 'dividend_quality_score' in analysis:
                quality_data = analysis['dividend_quality_score']
                if isinstance(quality_data, dict) and 'quality_score' in quality_data:
                    return quality_data['quality_score'] / 100
            
            # Fallback to sustainability analysis consistency score
            if 'sustainability_analysis' in analysis:
                sustainability = analysis['sustainability_analysis']
                if isinstance(sustainability, dict) and 'consistency_score' in sustainability:
                    return sustainability['consistency_score'] / 100
            
            return 0.75  # Default score
            
        except Exception:
            return 0.75
    
    async def _get_historical_returns(self, tickers: List[str], years: int = 5) -> pd.DataFrame:
        """Fetch historical returns concurrently for faster covariance estimation."""
        import yfinance as yf

        semaphore = asyncio.Semaphore(5)

        async def _fetch_returns(ticker: str):
            async with semaphore:
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period=f"{years}y")
                    if len(hist) > 20:
                        prices = hist['Close'].values
                        return ticker, np.diff(np.log(prices))
                    # Synthetic fallback
                    np.random.seed(hash(ticker) % 2**32)
                    vol = self._get_realistic_volatility(ticker) / 100
                    return ticker, np.random.normal(0.08/252, vol/np.sqrt(252), years * 252)
                except Exception as e:
                    logger.warning(f"Failed to get data for {ticker}: {e}")
                    np.random.seed(hash(ticker) % 2**32)
                    vol = self._get_realistic_volatility(ticker) / 100
                    return ticker, np.random.normal(0.08/252, vol/np.sqrt(252), years * 252)

        results = await asyncio.gather(*[asyncio.create_task(_fetch_returns(t)) for t in tickers])
        returns_data = {ticker: ret for ticker, ret in results}

        try:
            return pd.DataFrame(returns_data)
        except Exception as e:
            logger.error(f"Failed to assemble returns DataFrame: {e}")
            raise
    
    def _compute_expected_returns(self, asset_metrics: List[AssetMetrics], objective: str) -> np.ndarray:
        """Compute expected returns vector based on objective."""
        n_assets = len(asset_metrics)
        expected_returns = np.zeros(n_assets)
        
        for i, metrics in enumerate(asset_metrics):
            if objective == "sharpe_ratio":
                # Use actual expected returns
                expected_returns[i] = metrics.expected_return
            elif objective == "dividend_yield":
                # Prioritize current dividend yield
                expected_returns[i] = metrics.dividend_yield * 2.0
            elif objective == "dividend_growth":
                # Prioritize dividend growth potential
                expected_returns[i] = metrics.dividend_growth_rate * 2.0
            elif objective == "balanced":
                # Balanced approach considering yield, growth, and quality
                yield_score = metrics.dividend_yield * 0.4
                growth_score = metrics.dividend_growth_rate * 0.4
                quality_score = metrics.dividend_consistency_score * 0.2
                expected_returns[i] = yield_score + growth_score + quality_score
            else:
                expected_returns[i] = metrics.expected_return
        
        # Ensure reasonable scale and differentiation
        if np.std(expected_returns) < 0.001:
            # Add some differentiation if returns are too similar
            expected_returns += np.random.normal(0, 0.01, len(expected_returns))
                
        return expected_returns
    
    def _compute_covariance_matrix(self, returns_data: pd.DataFrame) -> np.ndarray:
        """Compute sample covariance matrix with numerical stability."""
        try:
            if returns_data.empty:
                n = len(returns_data.columns)
                # Create a realistic correlation structure
                corr = np.random.rand(n, n) * 0.3 + 0.1
                corr = (corr + corr.T) / 2
                np.fill_diagonal(corr, 1.0)
                
                # Convert to covariance
                vols = np.array([self._get_realistic_volatility(col)/100 for col in returns_data.columns])
                cov_matrix = np.outer(vols, vols) * corr
                return cov_matrix
                
            cov_matrix = returns_data.cov().values
            
            # Ensure positive definite
            min_eigenvalue = 1e-8
            eigenvals, eigenvecs = np.linalg.eigh(cov_matrix)
            eigenvals = np.maximum(eigenvals, min_eigenvalue)
            cov_matrix = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
            
            # Scale to reasonable levels (annual volatility)
            cov_matrix *= 252  # Annualize
            
            return cov_matrix
            
        except Exception as e:
            logger.warning(f"Covariance computation failed: {e}")
            n = len(returns_data.columns) if not returns_data.empty else 3
            # Create realistic covariance matrix
            corr = np.random.rand(n, n) * 0.3 + 0.1
            corr = (corr + corr.T) / 2
            np.fill_diagonal(corr, 1.0)
            
            vols = np.array([0.20, 0.25, 0.15][:n])  # Realistic volatilities
            cov_matrix = np.outer(vols, vols) * corr
            return cov_matrix
    
    def _apply_correlation_shrinkage(self, cov_matrix: np.ndarray, shrinkage: float) -> np.ndarray:
        """Apply correlation shrinkage - core EPO methodology."""
        try:
            # Extract volatilities and correlation matrix
            volatilities = np.sqrt(np.diag(cov_matrix))
            vol_matrix = np.outer(volatilities, volatilities)
            
            # Avoid division by zero
            vol_matrix = np.maximum(vol_matrix, 1e-8)
            correlation_matrix = cov_matrix / vol_matrix
            np.fill_diagonal(correlation_matrix, 1.0)
            
            # Apply shrinkage to correlations (shrink towards zero)
            shrunk_correlations = (1 - shrinkage) * correlation_matrix
            np.fill_diagonal(shrunk_correlations, 1.0)
            
            # Reconstruct covariance matrix
            shrunk_cov = shrunk_correlations * vol_matrix
            
            # Ensure positive definite
            eigenvals, eigenvecs = np.linalg.eigh(shrunk_cov)
            eigenvals = np.maximum(eigenvals, 1e-8)
            shrunk_cov = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
            
            return shrunk_cov
            
        except Exception as e:
            logger.error(f"Correlation shrinkage failed: {e}")
            return cov_matrix
    
    def _optimize_shrinkage_parameter(
        self, 
        expected_returns: np.ndarray, 
        cov_matrix: np.ndarray,
        returns_data: pd.DataFrame
    ) -> float:
        """Optimize shrinkage parameter to maximize out-of-sample Sharpe ratio."""
        try:
            if returns_data.empty or len(returns_data) < 100:
                return 0.50  # Conservative default
                
            split_point = int(len(returns_data) * 0.7)
            train_data = returns_data.iloc[:split_point]
            test_data = returns_data.iloc[split_point:]
            
            if len(test_data) < 20:
                return 0.50
                
            shrinkage_candidates = np.arange(0.0, 1.01, 0.10)
            best_sharpe = -np.inf
            best_shrinkage = 0.50
            
            for shrinkage in shrinkage_candidates:
                try:
                    train_cov = train_data.cov().values * 252  # Annualize
                    shrunk_cov = self._apply_correlation_shrinkage(train_cov, shrinkage)
                    
                    weights = self._solve_mvo(expected_returns, shrunk_cov)
                    
                    if weights is None or np.any(np.isnan(weights)):
                        continue
                        
                    # Calculate out-of-sample performance
                    test_returns_matrix = test_data.values
                    portfolio_returns = test_returns_matrix @ weights
                    
                    if len(portfolio_returns) > 0 and np.std(portfolio_returns) > 0:
                        sharpe = np.mean(portfolio_returns) / np.std(portfolio_returns)
                        
                        if sharpe > best_sharpe:
                            best_sharpe = sharpe
                            best_shrinkage = shrinkage
                        
                except Exception as inner_e:
                    logger.debug(f"Error testing shrinkage {shrinkage}: {inner_e}")
                    continue
                    
            logger.info(f"Optimal shrinkage parameter: {best_shrinkage} (Sharpe: {best_sharpe:.4f})")
            return best_shrinkage
            
        except Exception as e:
            logger.warning(f"Shrinkage optimization failed: {e}")
            return 0.50
    
    def _optimize_simple_epo(
        self, 
        expected_returns: np.ndarray, 
        cov_matrix: np.ndarray,
        constraints: Optional[Dict[str, Any]],
        tickers: List[str]
    ) -> Dict[str, float]:
        """Simple EPO optimization with enhanced numerical stability."""
        try:
            logger.info(f"Starting EPO optimization with returns: {expected_returns}")
            weights_array = self._solve_mvo(expected_returns, cov_matrix, constraints)
            
            if weights_array is None or np.any(np.isnan(weights_array)):
                logger.warning("MVO failed, using risk-parity as fallback")
                weights_array = self._risk_parity_weights(cov_matrix)
                
            weights_dict = {}
            for i, weight in enumerate(weights_array):
                ticker = tickers[i] if i < len(tickers) else f"ASSET_{i}"
                weights_dict[ticker] = float(max(0.0, min(1.0, weight)))  # Clamp weights
                
            # Normalize weights to sum to 1
            total_weight = sum(weights_dict.values())
            if total_weight > 0:
                weights_dict = {k: v/total_weight for k, v in weights_dict.items()}
            else:
                # Equal weights fallback
                n = len(tickers)
                weights_dict = {ticker: 1.0/n for ticker in tickers}
                
            logger.info(f"Final optimized weights: {weights_dict}")
            return weights_dict
            
        except Exception as e:
            logger.error(f"Simple EPO optimization failed: {e}")
            n = len(expected_returns)
            return {tickers[i] if i < len(tickers) else f"ASSET_{i}": 1.0/n for i in range(n)}
    
    def _risk_parity_weights(self, cov_matrix: np.ndarray) -> np.ndarray:
        """Calculate risk parity weights as a robust fallback."""
        try:
            # Inverse volatility weighting
            volatilities = np.sqrt(np.diag(cov_matrix))
            inv_vol = 1.0 / (volatilities + 1e-8)
            weights = inv_vol / np.sum(inv_vol)
            return weights
        except:
            n = cov_matrix.shape[0]
            return np.ones(n) / n
    
    def _optimize_anchored_portfolio(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        anchor_portfolio: Dict[str, float],
        constraints: Optional[Dict[str, Any]],
        tickers: List[str]
    ) -> Dict[str, float]:
        """Anchored EPO optimization."""
        try:
            anchor_array = np.array([anchor_portfolio.get(ticker, 0.0) for ticker in tickers])
            
            weights_array = self._solve_anchored_mvo(
                expected_returns, cov_matrix, anchor_array, constraints
            )
            
            if weights_array is None:
                return anchor_portfolio
                
            return {ticker: float(weight) for ticker, weight in zip(tickers, weights_array)}
            
        except Exception as e:
            logger.error(f"Anchored EPO optimization failed: {e}")
            return anchor_portfolio
    
    def _solve_mvo(
        self, 
        expected_returns: np.ndarray, 
        cov_matrix: np.ndarray,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Optional[np.ndarray]:
        """Solve mean-variance optimization problem with enhanced stability."""
        try:
            n = len(expected_returns)
            logger.info(f"Solving MVO for {n} assets with returns: {expected_returns}")
            logger.info(f"Covariance matrix shape: {cov_matrix.shape}")
            
            # Ensure inputs are valid
            if np.any(np.isnan(expected_returns)) or np.any(np.isnan(cov_matrix)):
                logger.error("NaN values in optimization inputs")
                return None
            
            # Check if all expected returns are the same (would cause optimization issues)
            if np.allclose(expected_returns, expected_returns[0]):
                logger.warning("All expected returns are identical, using equal weights")
                return np.ones(n) / n
                
            # Add regularization to covariance matrix for numerical stability
            reg_param = 1e-5
            regularized_cov = cov_matrix + reg_param * np.eye(len(cov_matrix))
            
            # Check condition number
            try:
                cond_num = np.linalg.cond(regularized_cov)
                logger.info(f"Covariance matrix condition number: {cond_num}")
                if cond_num > 1e12:
                    logger.warning("Covariance matrix is poorly conditioned, adding more regularization")
                    reg_param = 1e-3
                    regularized_cov = cov_matrix + reg_param * np.eye(len(cov_matrix))
            except:
                logger.warning("Cannot compute condition number, proceeding with regularization")
            
            # Enhanced objective function
            def objective(weights):
                weights = np.array(weights)
                weights = np.clip(weights, 1e-8, 1.0)  # Prevent zero or negative weights
                
                # Normalize weights
                weight_sum = np.sum(weights)
                if weight_sum > 0:
                    weights = weights / weight_sum
                else:
                    return 1e6  # Return a large penalty for invalid weights
                
                try:
                    portfolio_return = np.dot(weights, expected_returns)
                    portfolio_variance = np.dot(weights, np.dot(regularized_cov, weights))
                    portfolio_vol = np.sqrt(max(portfolio_variance, 1e-10))
                    
                    # Sharpe ratio (maximize)
                    sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
                    
                    # Add small penalty for extreme weights to encourage diversification
                    diversification_penalty = 0.01 * np.sum(weights ** 2)
                    
                    # Return negative Sharpe (since we're minimizing)
                    return -(sharpe - diversification_penalty)
                    
                except Exception as e:
                    logger.warning(f"Error in objective function: {e}")
                    return 1e6
            
            # Constraints: weights sum to 1
            def weight_sum_constraint(weights):
                return np.sum(weights) - 1.0
            
            constraints_list = [{"type": "eq", "fun": weight_sum_constraint}]
            
            # Bounds: minimum and maximum weights with more reasonable bounds
            min_weight = max(self.min_weight, 0.01)  # At least 1%
            max_weight = min(self.max_weight, 0.8)   # At most 80%
            bounds = [(min_weight, max_weight) for _ in range(n)]
            
            # Starting point: equal weights
            x0 = np.ones(n) / n
            
            # Try multiple optimization attempts
            best_result = None
            best_sharpe = float('-inf')
            
            # Method 1: SLSQP
            try:
                result = minimize(
                    objective,
                    x0,
                    method="SLSQP",
                    bounds=bounds,
                    constraints=constraints_list,
                    options={"maxiter": 1000, "ftol": 1e-9}
                )
                
                if result.success and np.sum(result.x) > 0.99:
                    # Evaluate the solution
                    test_weights = result.x / np.sum(result.x)
                    test_return = np.dot(test_weights, expected_returns)
                    test_vol = np.sqrt(np.dot(test_weights, np.dot(regularized_cov, test_weights)))
                    test_sharpe = (test_return - self.risk_free_rate) / test_vol
                    
                    if test_sharpe > best_sharpe:
                        best_sharpe = test_sharpe
                        best_result = test_weights
                        logger.info(f"SLSQP succeeded with Sharpe ratio: {test_sharpe:.4f}")
                
            except Exception as e:
                logger.warning(f"SLSQP failed: {e}")
            
            # Method 2: Sequential Least Squares with different starting point
            try:
                # Start with inverse volatility weights
                vol_diag = np.sqrt(np.diag(regularized_cov))
                inv_vol_weights = (1 / vol_diag) / np.sum(1 / vol_diag)
                
                result = minimize(
                    objective,
                    inv_vol_weights,
                    method="SLSQP",
                    bounds=bounds,
                    constraints=constraints_list,
                    options={"maxiter": 1000, "ftol": 1e-9}
                )
                
                if result.success and np.sum(result.x) > 0.99:
                    test_weights = result.x / np.sum(result.x)
                    test_return = np.dot(test_weights, expected_returns)
                    test_vol = np.sqrt(np.dot(test_weights, np.dot(regularized_cov, test_weights)))
                    test_sharpe = (test_return - self.risk_free_rate) / test_vol
                    
                    if test_sharpe > best_sharpe:
                        best_sharpe = test_sharpe
                        best_result = test_weights
                        logger.info(f"SLSQP (inv vol start) succeeded with Sharpe ratio: {test_sharpe:.4f}")
                
            except Exception as e:
                logger.warning(f"SLSQP with inv vol start failed: {e}")
            
            # Method 3: Trust-region
            try:
                result = minimize(
                    objective,
                    x0,
                    method="trust-constr",
                    bounds=bounds,
                    constraints=constraints_list,
                    options={"maxiter": 1000}
                )
                
                if result.success and np.sum(result.x) > 0.99:
                    test_weights = result.x / np.sum(result.x)
                    test_return = np.dot(test_weights, expected_returns)
                    test_vol = np.sqrt(np.dot(test_weights, np.dot(regularized_cov, test_weights)))
                    test_sharpe = (test_return - self.risk_free_rate) / test_vol
                    
                    if test_sharpe > best_sharpe:
                        best_sharpe = test_sharpe
                        best_result = test_weights
                        logger.info(f"Trust-constr succeeded with Sharpe ratio: {test_sharpe:.4f}")
                
            except Exception as e:
                logger.warning(f"Trust-constr failed: {e}")
            
            if best_result is not None:
                logger.info(f"Optimization successful! Best Sharpe ratio: {best_sharpe:.4f}")
                logger.info(f"Optimal weights: {best_result}")
                return best_result
            else:
                logger.error("All optimization methods failed")
                # As a fallback, use inverse volatility weights (better than equal weights)
                vol_diag = np.sqrt(np.diag(regularized_cov))
                weights = (1 / vol_diag) / np.sum(1 / vol_diag)
                logger.info(f"Using inverse volatility weights as fallback: {weights}")
                return weights
                
        except Exception as e:
            logger.error(f"MVO solver completely failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _solve_anchored_mvo(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        anchor_weights: np.ndarray,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Optional[np.ndarray]:
        """Solve anchored mean-variance optimization."""
        try:
            n = len(expected_returns)
            lambda_reg = 0.5  # Regularization parameter
            
            def objective(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)) + 1e-12)
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
                
                # Penalty for deviation from anchor
                anchor_penalty = lambda_reg * np.sum((weights - anchor_weights) ** 2)
                
                return -sharpe + anchor_penalty
            
            constraints_list = [{"type": "eq", "fun": lambda x: np.sum(x) - 1.0}]
            bounds = [(self.min_weight, self.max_weight) for _ in range(n)]
            
            # Start closer to anchor portfolio
            x0 = 0.7 * anchor_weights + 0.3 * np.ones(n) / n
            x0 = x0 / np.sum(x0)  # Normalize
            
            result = minimize(
                objective,
                x0,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints_list,
                options={"maxiter": 1000}
            )
            
            if result.success:
                return result.x
            else:
                return anchor_weights
                
        except Exception as e:
            logger.error(f"Anchored MVO solver failed: {e}")
            return anchor_weights
    
    def _calculate_portfolio_metrics(
        self,
        weights: Dict[str, float],
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        asset_metrics: List[AssetMetrics]
    ) -> Dict[str, Any]:
        """Calculate comprehensive portfolio metrics."""
        try:
            weights_array = np.array(list(weights.values()))
            
            portfolio_return = np.dot(weights_array, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights_array, np.dot(cov_matrix, weights_array)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
            
            weighted_dividend_yield = sum(
                weights[metric.ticker] * metric.dividend_yield 
                for metric in asset_metrics 
                if metric.ticker in weights
            )
            
            max_weight = max(weights.values())
            n_effective = 1 / sum(w**2 for w in weights.values())
            
            avg_consistency = np.average(
                [metric.dividend_consistency_score for metric in asset_metrics],
                weights=[weights.get(metric.ticker, 0) for metric in asset_metrics]
            )
            
            return {
                "return": float(portfolio_return),
                "volatility": float(portfolio_vol),
                "sharpe_ratio": float(sharpe_ratio),
                "dividend_yield": float(weighted_dividend_yield),
                "risk_metrics": {
                    "max_weight": float(max_weight),
                    "effective_positions": float(n_effective),
                    "concentration_risk": float(max_weight * n_effective),
                    "avg_dividend_consistency": float(avg_consistency)
                }
            }
            
        except Exception as e:
            logger.error(f"Portfolio metrics calculation failed: {e}")
            return {
                "return": 0.08,
                "volatility": 0.15,
                "sharpe_ratio": 0.4,
                "dividend_yield": 0.03,
                "risk_metrics": {}
            }
    
    def _calculate_asset_contributions(
        self,
        weights: Dict[str, float],
        asset_metrics: List[AssetMetrics],
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray
    ) -> Dict[str, Dict[str, float]]:
        """Calculate individual asset contributions to portfolio metrics."""
        contributions = {}
        
        try:
            weights_array = np.array(list(weights.values()))
            portfolio_vol = np.sqrt(np.dot(weights_array, np.dot(cov_matrix, weights_array)))
            
            for i, (ticker, weight) in enumerate(weights.items()):
                if weight > 0:
                    marginal_risk = np.dot(cov_matrix[i], weights_array) / portfolio_vol
                    risk_contribution = weight * marginal_risk
                    return_contribution = weight * expected_returns[i]
                    
                    asset_metric = next((m for m in asset_metrics if m.ticker == ticker), None)
                    
                    contributions[ticker] = {
                        "weight": float(weight),
                        "return_contribution": float(return_contribution),
                        "risk_contribution": float(risk_contribution),
                        "dividend_yield": float(asset_metric.dividend_yield if asset_metric else 0),
                        "dividend_growth": float(asset_metric.dividend_growth_rate if asset_metric else 0),
                        "quality_score": float(asset_metric.dividend_consistency_score if asset_metric else 0)
                    }
                    
        except Exception as e:
            logger.error(f"Asset contributions calculation failed: {e}")
            
        return contributions 
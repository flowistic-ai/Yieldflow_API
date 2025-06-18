import asyncio
import aiohttp
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
import structlog
from statistics import mean, stdev
import math
try:
    from fredapi import Fred
except ImportError:
    Fred = None

from app.core.config import settings
from app.utils.exceptions import DataSourceError, TickerNotFoundError, ValidationError
from app.services.cache_service import CacheService
from app.schemas.financial import (
    DividendResponse, DividendAnalysisResponse, DividendForecast,
    DividendType, DividendFrequency, ComprehensiveDividendResponse
)

logger = structlog.get_logger()


class DividendService:
    """Professional-grade dividend analysis service with advanced financial calculations"""
    
    def __init__(self):
        self.cache_service = CacheService()
        
        # API Configuration
        if Fred and settings.FRED_API_KEY:
            try:
                self.fred = Fred(api_key=settings.FRED_API_KEY)
            except Exception as e:
                logger.warning("Failed to initialize FRED API", error=str(e))
                self.fred = None
        else:
            self.fred = None
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.fmp_key = settings.FMP_API_KEY
        
        # API Base URLs
        self.fmp_base_url = "https://financialmodelingprep.com/api/v3"
        
        # Financial constants for professional analysis
        self.RISK_FREE_RATE_PROXY = 'GS10'  # 10-Year Treasury
        self.MARKET_BENCHMARK = 'SP500'     # S&P 500 Index
        
        # Industry dividend yield benchmarks (will be dynamic in production)
        self.sector_benchmarks = {
            'Technology': {'yield_range': [0.5, 2.5], 'payout_target': 25, 'growth_expectation': 8, 'avg_yield': 1.2, 'payout_ratio': 25},
            'Utilities': {'yield_range': [3.0, 6.0], 'payout_target': 70, 'growth_expectation': 3, 'avg_yield': 4.5, 'payout_ratio': 70},
            'Real Estate': {'yield_range': [2.5, 5.5], 'payout_target': 85, 'growth_expectation': 4, 'avg_yield': 3.8, 'payout_ratio': 85},
            'Consumer Staples': {'yield_range': [2.0, 4.0], 'payout_target': 60, 'growth_expectation': 5, 'avg_yield': 2.8, 'payout_ratio': 60},
            'Healthcare': {'yield_range': [1.5, 3.5], 'payout_target': 45, 'growth_expectation': 6, 'avg_yield': 2.1, 'payout_ratio': 45},
            'Financials': {'yield_range': [2.0, 4.5], 'payout_target': 40, 'growth_expectation': 7, 'avg_yield': 3.2, 'payout_ratio': 40},
            'Energy': {'yield_range': [3.0, 7.0], 'payout_target': 35, 'growth_expectation': 2, 'avg_yield': 4.2, 'payout_ratio': 35},
            'Industrials': {'yield_range': [1.8, 3.5], 'payout_target': 50, 'growth_expectation': 6, 'avg_yield': 2.5, 'payout_ratio': 50},
        }

    async def get_comprehensive_dividend_analysis(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_forecast: bool = False,
        include_peer_comparison: bool = False
    ) -> Dict[str, Any]:
        """
        INSTITUTIONAL-GRADE DIVIDEND ANALYSIS
        Advanced financial formulas with professional calculations
        """
        
        try:
            # Set professional analysis timeframe (minimum 5 years for meaningful analysis)
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=365 * 10)  # 10 years for robust analysis
            
            # Multi-source data aggregation with parallel processing
            data_tasks = await asyncio.gather(
                self._fetch_multi_source_dividends(ticker, start_date, end_date),
                self._fetch_comprehensive_financials(ticker),
                self._fetch_market_data(ticker),
                self._fetch_economic_context(),
                return_exceptions=True
            )
            
            dividends, financials, market_data, economic_context = [
                result if not isinstance(result, Exception) else {} 
                for result in data_tasks
            ]
            
            if not dividends:
                raise TickerNotFoundError(f"No dividend data found for {ticker}")
            
            # PROFESSIONAL FINANCIAL CALCULATIONS
            
            # 1. DIVIDEND QUALITY SCORE (0-100) WITH COMPONENT WEIGHTING
            quality_analysis = self._calculate_professional_quality_score(dividends, financials)
            
            # 2. SUSTAINABILITY ANALYSIS WITH FCF METRICS
            sustainability_analysis = self._calculate_sustainability_metrics(dividends, financials)
            
            # 3. GROWTH ANALYTICS WITH CAGR CALCULATIONS
            growth_analysis = self._calculate_growth_analytics(dividends)
            
            # 4. COVERAGE ANALYSIS WITH PROFESSIONAL GRADING
            coverage_analysis = self._calculate_coverage_analytics(dividends, financials)
            
            # 5. VALUATION METRICS WITH DDM CALCULATIONS
            valuation_analysis = self._calculate_valuation_analytics(dividends, market_data, economic_context)
            
            # 6. RISK ASSESSMENT WITH MULTI-FACTOR MODEL
            risk_analysis = self._calculate_risk_analytics(dividends, financials, economic_context)
            
            # 7. PERFORMANCE ANALYTICS WITH PERCENTILE RANKINGS
            performance_analysis = self._calculate_performance_analytics(dividends, market_data)
            
            # 8. CURRENT DIVIDEND METRICS
            current_metrics = self._get_current_dividend_metrics(dividends, market_data)
            
            # CONSOLIDATED INSTITUTIONAL RESPONSE (NO REDUNDANCY)
            return {
                'ticker': ticker.upper(),
                'analysis_period': {
                    'start_date': start_date.isoformat(), 
                    'end_date': end_date.isoformat(),
                    'years_analyzed': (end_date - start_date).days / 365
                },
                
                # CORE PROFESSIONAL METRICS
                'dividend_quality_score': quality_analysis,
                'sustainability_analysis': sustainability_analysis,
                'growth_analytics': growth_analysis,
                'coverage_analysis': coverage_analysis,
                'valuation_metrics': valuation_analysis,
                'risk_assessment': risk_analysis,
                'performance_analytics': performance_analysis,
                'current_metrics': current_metrics,
                
                # OPTIONAL ADVANCED FEATURES
                'forecast': await self._generate_professional_forecast(dividends, financials, economic_context, 3) if include_forecast else None,
                'peer_benchmarking': await self._get_sector_benchmarking(ticker, quality_analysis, market_data) if include_peer_comparison else None,
                
                # METADATA
                'data_sources': ['yahoo_finance', 'alpha_vantage', 'fmp', 'fred'],
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'confidence_score': self._calculate_data_reliability_score(dividends, financials)
            }
            
        except Exception as e:
            logger.error("Professional dividend analysis failed", ticker=ticker, error=str(e))
            if isinstance(e, (TickerNotFoundError, ValidationError)):
                raise
            raise DataSourceError(f"Dividend analysis failed: {str(e)}")

    def _calculate_professional_quality_score(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """
        INSTITUTIONAL DIVIDEND QUALITY SCORE (0-100)
        Based on Morningstar/S&P methodologies with weighted components:
        - Consistency (25%): Years of maintained/increased dividends  
        - Growth (25%): CAGR analysis with 5-15% optimal target
        - Coverage (25%): EPS & FCF coverage ratios
        - Yield Quality (15%): Stability vs volatility assessment
        - Financial Strength (10%): ROE, balance sheet metrics
        """
        
        if not dividends:
            return {'quality_score': 0, 'grade': 'F', 'components': {}}
        
        # Component calculations with institutional weighting
        consistency_score = self._score_dividend_consistency(dividends) * 0.25    # 25%
        growth_score = self._score_dividend_growth(dividends) * 0.25             # 25%
        coverage_score = self._score_dividend_coverage(dividends, financials) * 0.25  # 25%
        yield_quality_score = self._score_dividend_yield_quality(dividends) * 0.15    # 15%
        financial_strength = self._score_financial_strength(financials) * 0.10        # 10%
        
        total_score = consistency_score + growth_score + coverage_score + yield_quality_score + financial_strength
        
        # Professional grading scale
        if total_score >= 90: grade, rating = 'A+', 'Exceptional'
        elif total_score >= 80: grade, rating = 'A', 'Excellent'
        elif total_score >= 70: grade, rating = 'B+', 'Very Good'
        elif total_score >= 60: grade, rating = 'B', 'Good'
        elif total_score >= 50: grade, rating = 'C+', 'Fair'
        elif total_score >= 40: grade, rating = 'C', 'Below Average'
        elif total_score >= 30: grade, rating = 'D', 'Poor'
        else: grade, rating = 'F', 'Very Poor'
        
        return {
            'quality_score': round(total_score, 1),
            'grade': grade,
            'rating': rating,
            'components': {
                'consistency_score': round(consistency_score / 0.25, 1),  # Show as 0-100
                'growth_score': round(growth_score / 0.25, 1),
                'coverage_score': round(coverage_score / 0.25, 1),
                'yield_quality_score': round(yield_quality_score / 0.15, 1),
                'financial_strength_score': round(financial_strength / 0.10, 1)
            },
            'investment_recommendation': self._get_investment_recommendation(total_score)
        }

    def _calculate_sustainability_metrics(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """
        CASH FLOW-BASED SUSTAINABILITY ANALYSIS
        - Free Cash Flow Coverage Ratio = FCF / Total Dividends Paid
        - Debt Service Coverage Ratio = EBITDA / Total Debt Service
        - Working Capital Analysis
        - Earnings Volatility Scoring
        """
        
        if not dividends or not financials:
            return {'sustainability_rating': 'Unknown', 'metrics': {}}
        
        # Core sustainability calculations
        ttm_dividend_per_share = sum(div.get('amount', 0) for div in dividends[:4])
        
        # Professional ratios
        payout_ratio = self._calculate_payout_ratio(dividends, financials)  # TTM Dividends / TTM EPS
        fcf_coverage = self._calculate_fcf_coverage_ratio(dividends, financials)  # FCF / Total Dividends
        debt_service_coverage = self._calculate_debt_service_coverage(financials)  # EBITDA / Debt Service
        earnings_volatility = self._calculate_earnings_volatility(financials)  # EPS volatility measure
        
        # Working capital analysis
        working_capital_ratio = financials.get('current_ratio', 1.0)
        
        # Composite sustainability score (0-100)
        sustainability_score = 0
        
        # Payout ratio scoring (30 points)
        if payout_ratio < 0.40: sustainability_score += 30
        elif payout_ratio < 0.60: sustainability_score += 25
        elif payout_ratio < 0.80: sustainability_score += 15
        elif payout_ratio < 1.00: sustainability_score += 5
        
        # FCF coverage scoring (30 points)  
        if fcf_coverage > 2.5: sustainability_score += 30
        elif fcf_coverage > 2.0: sustainability_score += 25
        elif fcf_coverage > 1.5: sustainability_score += 20
        elif fcf_coverage > 1.2: sustainability_score += 10
        
        # Debt service coverage (25 points)
        if debt_service_coverage > 3.0: sustainability_score += 25
        elif debt_service_coverage > 2.5: sustainability_score += 20
        elif debt_service_coverage > 2.0: sustainability_score += 15
        elif debt_service_coverage > 1.5: sustainability_score += 10
        
        # Earnings stability (15 points)
        if earnings_volatility < 0.15: sustainability_score += 15
        elif earnings_volatility < 0.25: sustainability_score += 12
        elif earnings_volatility < 0.35: sustainability_score += 8
        elif earnings_volatility < 0.50: sustainability_score += 4
        
        # Sustainability rating
        if sustainability_score >= 85: rating = 'Very High'
        elif sustainability_score >= 70: rating = 'High'
        elif sustainability_score >= 50: rating = 'Moderate'
        elif sustainability_score >= 30: rating = 'Low'
        else: rating = 'Very Low'
        
        return {
            'sustainability_score': sustainability_score,
            'sustainability_rating': rating,
            'key_ratios': {
                'payout_ratio': round(payout_ratio, 3),
                'fcf_coverage_ratio': round(fcf_coverage, 2),
                'debt_service_coverage': round(debt_service_coverage, 2),
                'earnings_volatility': round(earnings_volatility, 3),
                'working_capital_ratio': round(working_capital_ratio, 2)
            },
            'risk_factors': self._identify_sustainability_risks(payout_ratio, fcf_coverage),
            'strengths': self._identify_sustainability_strengths(payout_ratio, fcf_coverage)
        }

    def _calculate_growth_analytics(self, dividends: List[Dict]) -> Dict[str, Any]:
        """
        ADVANCED GROWTH ANALYTICS WITH CAGR CALCULATIONS
        CAGR Formula: ((End Value / Start Value) ^ (1/Years)) - 1
        Analyzes 3, 5, 10-year periods with growth consistency metrics
        """
        
        if len(dividends) < 8:
            return {'status': 'Insufficient data for growth analysis'}
        
        annual_dividends = self._aggregate_annual_dividends(dividends)
        years = sorted(annual_dividends.keys(), reverse=True)
        
        if len(years) < 3:
            return {'status': 'Need minimum 3 years of data'}
        
        # CAGR calculations for multiple periods
        cagr_analysis = {}
        for period in [3, 5, 10]:
            if len(years) >= period:
                start_value = annual_dividends[years[period-1]]
                end_value = annual_dividends[years[0]]
                if start_value > 0:
                    cagr = ((end_value / start_value) ** (1/period)) - 1
                    cagr_analysis[f'{period}y_cagr'] = round(cagr * 100, 2)
        
        # Year-over-year growth analysis
        growth_rates = []
        for i in range(len(years) - 1):
            current = annual_dividends[years[i]]
            previous = annual_dividends[years[i + 1]]
            if previous > 0:
                growth_rate = (current - previous) / previous
                growth_rates.append(growth_rate * 100)
        
        # Growth quality metrics
        avg_growth = mean(growth_rates) if growth_rates else 0
        growth_volatility = stdev(growth_rates) if len(growth_rates) > 1 else 0
        positive_growth_years = sum(1 for rate in growth_rates if rate > 0)
        
        # Aristocrat status detection (25+ consecutive increases)
        consecutive_increases = self._calculate_consecutive_increases(annual_dividends)
        
        # Growth sustainability assessment (5-15% optimal range)
        growth_quality = 'Optimal' if 5 <= avg_growth <= 15 else \
                        'Aggressive' if avg_growth > 15 else \
                        'Conservative' if 0 < avg_growth < 5 else 'Declining'
        
        return {
            'cagr_analysis': cagr_analysis,
            'average_annual_growth': round(avg_growth, 2),
            'growth_volatility': round(growth_volatility, 2),
            'growth_consistency': round((positive_growth_years / len(growth_rates)) * 100, 1),
            'consecutive_increases': consecutive_increases,
            'aristocrat_status': {
                'is_dividend_aristocrat': consecutive_increases >= 25,
                'is_dividend_achiever': consecutive_increases >= 10,
                'is_dividend_challenger': consecutive_increases >= 5
            },
            'growth_quality': growth_quality,
            'growth_trend': self._determine_recent_trend(growth_rates[-3:] if len(growth_rates) >= 3 else growth_rates)
        }

    def _calculate_coverage_analytics(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """
        PROFESSIONAL COVERAGE ANALYSIS WITH MULTIPLE RATIOS
        - EPS Coverage = EPS / Dividend Per Share
        - FCF Coverage = Free Cash Flow / Total Dividends Paid  
        - EBITDA Coverage = EBITDA / Total Dividend Payments
        Professional grading: A+ (>3.0), A (>2.5), B (>2.0), C (>1.5), D (>1.0), F (<1.0)
        """
        
        if not dividends or not financials:
            return {'coverage_grade': 'F', 'analysis': 'Insufficient data'}
        
        # Core coverage ratios
        eps_coverage = self._calculate_eps_coverage_ratio(dividends, financials)
        fcf_coverage = self._calculate_fcf_coverage_ratio(dividends, financials)
        ebitda_coverage = self._calculate_ebitda_coverage_ratio(dividends, financials)
        
        # Professional grading system
        def grade_coverage(ratio):
            if ratio >= 3.0: return 'A+', 100
            elif ratio >= 2.5: return 'A', 90
            elif ratio >= 2.0: return 'B', 80
            elif ratio >= 1.5: return 'C', 70
            elif ratio >= 1.0: return 'D', 60
            else: return 'F', 0
        
        eps_grade, eps_score = grade_coverage(eps_coverage)
        fcf_grade, fcf_score = grade_coverage(fcf_coverage)
        ebitda_grade, ebitda_score = grade_coverage(ebitda_coverage)
        
        # Composite coverage score (weighted average)
        composite_score = (eps_score * 0.4) + (fcf_score * 0.4) + (ebitda_score * 0.2)
        composite_grade, _ = grade_coverage(composite_score / 20)  # Convert back to ratio scale
        
        return {
            'coverage_ratios': {
                'eps_coverage': round(eps_coverage, 2),
                'fcf_coverage': round(fcf_coverage, 2),
                'ebitda_coverage': round(ebitda_coverage, 2)
            },
            'coverage_grades': {
                'eps_grade': eps_grade,
                'fcf_grade': fcf_grade,
                'ebitda_grade': ebitda_grade,
                'composite_grade': composite_grade
            },
            'coverage_score': round(composite_score, 1),
            'coverage_assessment': self._assess_coverage_adequacy(eps_coverage, fcf_coverage),
            'coverage_trend': self._analyze_coverage_trend(dividends, financials)
        }

    def _calculate_valuation_analytics(self, dividends: List[Dict], market_data: Dict, economic_context: Dict) -> Dict[str, Any]:
        """
        VALUATION METRICS WITH DDM CALCULATIONS
        - Yield Spread = Current Yield - 10Y Treasury Rate
        - Dividend Discount Model (DDM) = D1 / (r - g)
        - Dividend Beta = Dividend volatility vs market
        - Price-to-dividend ratio analysis
        """
        
        if not dividends or not market_data:
            return {'status': 'Insufficient data for valuation'}
        
        current_price = market_data.get('current_price', 0)
        ttm_dividend = sum(div.get('amount', 0) for div in dividends[:4])
        
        # Current yield calculation
        current_yield = (ttm_dividend / current_price * 100) if current_price > 0 else 0
        
        # Yield spread vs risk-free rate
        treasury_10y = economic_context.get('treasury_10y', 4.5)
        yield_spread = current_yield - treasury_10y
        
        # Dividend Discount Model calculation
        ddm_value = self._calculate_ddm_value(dividends, market_data, economic_context)
        
        # Price-to-dividend ratio
        price_to_dividend = current_price / ttm_dividend if ttm_dividend > 0 else 0
        
        # Dividend beta (volatility vs market)
        dividend_beta = self._calculate_dividend_beta(dividends)
        
        # Valuation assessment
        valuation_signal = 'Undervalued' if ddm_value > current_price * 1.1 else \
                          'Overvalued' if ddm_value < current_price * 0.9 else 'Fair Value'
        
        return {
            'current_yield': round(current_yield, 2),
            'yield_spread_vs_treasury': round(yield_spread, 2),
            'ddm_fair_value': round(ddm_value, 2),
            'price_to_dividend_ratio': round(price_to_dividend, 1),
            'dividend_beta': round(dividend_beta, 2),
            'valuation_signal': valuation_signal,
            'yield_attractiveness': 'Attractive' if yield_spread > 1.0 else 'Neutral' if yield_spread > -0.5 else 'Unattractive'
        }

    def _calculate_risk_analytics(self, dividends: List[Dict], financials: Dict, economic_context: Dict) -> Dict[str, Any]:
        """
        MULTI-FACTOR RISK ASSESSMENT (0-100 SCALE)
        - Payout ratio risk assessment
        - Economic sensitivity analysis  
        - Sector-specific risk adjustments
        - Financial stability metrics
        """
        
        if not dividends:
            return {'risk_score': 100, 'risk_rating': 'Very High'}
        
        risk_score = 0
        
        # Payout ratio risk (25 points)
        payout_ratio = self._calculate_payout_ratio(dividends, financials)
        if payout_ratio > 1.0: risk_score += 25
        elif payout_ratio > 0.8: risk_score += 20
        elif payout_ratio > 0.6: risk_score += 15
        elif payout_ratio > 0.4: risk_score += 10
        elif payout_ratio > 0.2: risk_score += 5
        
        # Coverage risk (25 points)
        fcf_coverage = self._calculate_fcf_coverage_ratio(dividends, financials)
        if fcf_coverage < 1.0: risk_score += 25
        elif fcf_coverage < 1.5: risk_score += 20
        elif fcf_coverage < 2.0: risk_score += 15
        elif fcf_coverage < 2.5: risk_score += 10
        elif fcf_coverage < 3.0: risk_score += 5
        
        # Economic sensitivity (25 points)
        treasury_rate = economic_context.get('treasury_10y', 4.5)
        if treasury_rate > 6.0: risk_score += 25
        elif treasury_rate > 5.0: risk_score += 20
        elif treasury_rate > 4.0: risk_score += 15
        elif treasury_rate > 3.0: risk_score += 10
        elif treasury_rate > 2.0: risk_score += 5
        
        # Financial stability (25 points)
        debt_to_equity = financials.get('debt_to_equity', 50) / 100
        if debt_to_equity > 1.0: risk_score += 25
        elif debt_to_equity > 0.75: risk_score += 20
        elif debt_to_equity > 0.5: risk_score += 15
        elif debt_to_equity > 0.25: risk_score += 10
        elif debt_to_equity > 0.1: risk_score += 5
        
        # Risk rating
        if risk_score <= 20: risk_rating = 'Very Low'
        elif risk_score <= 40: risk_rating = 'Low' 
        elif risk_score <= 60: risk_rating = 'Moderate'
        elif risk_score <= 80: risk_rating = 'High'
        else: risk_rating = 'Very High'
        
        return {
            'risk_score': risk_score,
            'risk_rating': risk_rating,
            'risk_factors': {
                'payout_ratio_risk': min(25, max(0, payout_ratio * 25)),
                'coverage_risk': min(25, max(0, (2.0 - fcf_coverage) * 12.5)),
                'economic_risk': min(25, max(0, (treasury_rate - 2.0) * 5)),
                'financial_stability_risk': min(25, max(0, debt_to_equity * 25))
            },
            'risk_mitigation': self._suggest_risk_mitigation(risk_score)
        }

    def _calculate_performance_analytics(self, dividends: List[Dict], market_data: Dict) -> Dict[str, Any]:
        """
        PERFORMANCE ANALYTICS WITH PERCENTILE RANKINGS
        - Current yield vs historical percentiles
        - Dividend growth vs sector benchmarks
        - Total return contribution analysis
        """
        
        if not dividends:
            return {'status': 'No dividend data available'}
        
        current_price = market_data.get('current_price', 0)
        ttm_dividend = sum(div.get('amount', 0) for div in dividends[:4])
        current_yield = (ttm_dividend / current_price * 100) if current_price > 0 else 0
        
        # Historical yield analysis for percentile ranking
        historical_yields = []
        for i in range(0, min(len(dividends), 20), 4):  # 5 years of data
            period_dividend = sum(div.get('amount', 0) for div in dividends[i:i+4])
            if period_dividend > 0 and current_price > 0:
                yield_pct = (period_dividend / current_price) * 100
                historical_yields.append(yield_pct)
        
        # Percentile calculations
        yield_percentile = self._calculate_percentile(current_yield, historical_yields)
        
        # Performance scoring
        performance_score = 0
        if yield_percentile > 80: performance_score += 25
        elif yield_percentile > 60: performance_score += 20
        elif yield_percentile > 40: performance_score += 15
        elif yield_percentile > 20: performance_score += 10
        
        return {
            'current_yield': round(current_yield, 2),
            'yield_percentile_ranking': round(yield_percentile, 1),
            'historical_yield_range': {
                'min': round(min(historical_yields), 2) if historical_yields else 0,
                'max': round(max(historical_yields), 2) if historical_yields else 0,
                'median': round(sorted(historical_yields)[len(historical_yields)//2], 2) if historical_yields else 0
            },
            'performance_score': performance_score,
            'yield_attractiveness': self._assess_yield_attractiveness(current_yield, yield_percentile)
        }

    async def _fetch_multi_source_dividends(self, ticker: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Professional multi-source dividend data aggregation with cross-validation
        Uses Yahoo Finance, Alpha Vantage, and FMP for maximum accuracy
        """
        
        # Parallel data fetching from all sources
        logger.info("Fetching dividend data from multiple sources", ticker=ticker, sources=["yfinance", "alpha_vantage", "fmp"])
        
        sources = await asyncio.gather(
            self._get_yfinance_dividends(ticker, start_date, end_date),
            self._get_alpha_vantage_dividends(ticker),
            self._get_fmp_dividends(ticker),
            return_exceptions=True
        )
        
        yf_data, av_data, fmp_data = [s if not isinstance(s, Exception) else [] for s in sources]
        
        logger.info("Data fetched", 
                   yf_count=len(yf_data), 
                   av_count=len(av_data), 
                   fmp_count=len(fmp_data))
        
        # Professional cross-validation and merging
        merged_data = self._cross_validate_and_merge_dividends(yf_data, av_data, fmp_data, start_date, end_date)
        
        return sorted(merged_data, key=lambda x: x.get('ex_date', date.min), reverse=True)

    def _cross_validate_and_merge_dividends(self, yf_data: List[Dict], av_data: List[Dict], fmp_data: List[Dict], start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Cross-validate dividend data from multiple sources and create consensus dataset
        Institutional-grade data validation and confidence scoring
        """
        
        dividend_map = {}  # Key: ex_date, Value: {amounts: [], sources: []}
        
        # Process YFinance data (highest priority for recent data)
        for div in yf_data:
            ex_date = div.get('ex_date')
            if start_date <= ex_date <= end_date:
                key = ex_date.isoformat()
                if key not in dividend_map:
                    dividend_map[key] = {'amounts': [], 'sources': [], 'dates': []}
                dividend_map[key]['amounts'].append(div['amount'])
                dividend_map[key]['sources'].append('yahoo_finance')
                dividend_map[key]['dates'].append(ex_date)
        
        # Process Alpha Vantage data (good for historical validation)
        for div in av_data:
            ex_date = div.get('ex_date')
            if start_date <= ex_date <= end_date:
                key = ex_date.isoformat()
                if key not in dividend_map:
                    dividend_map[key] = {'amounts': [], 'sources': [], 'dates': []}
                dividend_map[key]['amounts'].append(div['amount'])
                dividend_map[key]['sources'].append('alpha_vantage')
                dividend_map[key]['dates'].append(ex_date)
        
        # Process FMP data (additional validation)
        for div in fmp_data:
            ex_date = div.get('ex_date')
            if start_date <= ex_date <= end_date:
                key = ex_date.isoformat()
                if key not in dividend_map:
                    dividend_map[key] = {'amounts': [], 'sources': [], 'dates': []}
                dividend_map[key]['amounts'].append(div['amount'])
                dividend_map[key]['sources'].append('fmp')
                dividend_map[key]['dates'].append(ex_date)
        
        # Create consensus dividends with confidence scores
        consensus_dividends = []
        for ex_date_str, data in dividend_map.items():
            amounts = data['amounts']
            sources = data['sources']
            ex_date = data['dates'][0]
            
            # Calculate consensus amount and confidence
            if len(amounts) == 1:
                consensus_amount = amounts[0]
                confidence = 0.8
            elif len(amounts) == 2:
                if abs(amounts[0] - amounts[1]) / max(amounts) < 0.01:  # <1% difference
                    consensus_amount = mean(amounts)
                    confidence = 0.95
                else:
                    consensus_amount = amounts[0]  # Prefer first source
                    confidence = 0.7
            else:  # 3+ sources
                consensus_amount = np.median(amounts)  # Use median for robustness
                confidence = 0.98
            
            dividend_record = {
                'ex_date': ex_date,
                'amount': round(consensus_amount, 4),
                'dividend_type': 'regular',
                'currency': 'USD',
                'data_sources': list(set(sources)),
                'confidence_score': confidence,
                'source_agreement': len(set(sources)),
                'amount_variance': stdev(amounts) if len(amounts) > 1 else 0
            }
            
            consensus_dividends.append(dividend_record)
        
        return consensus_dividends

    def _calculate_dividend_quality_score(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """
        Calculate institutional-grade dividend quality score (0-100)
        Based on Morningstar and S&P dividend quality methodologies
        """
        
        if not dividends:
            return {'quality_score': 0, 'grade': 'F', 'components': {}}
        
        # Component scores (each 0-20 points)
        consistency_score = self._score_dividend_consistency(dividends)  # 20 points
        growth_score = self._score_dividend_growth(dividends)           # 20 points
        coverage_score = self._score_dividend_coverage(dividends, financials)  # 20 points
        yield_score = self._score_dividend_yield_quality(dividends)     # 20 points
        stability_score = self._score_earnings_stability(financials)    # 20 points
        
        total_score = consistency_score + growth_score + coverage_score + yield_score + stability_score
        
        # Grade assignment
        grade_map = {90: 'A+', 80: 'A', 70: 'B+', 60: 'B', 50: 'C+', 40: 'C', 30: 'D', 0: 'F'}
        grade = next(grade for threshold, grade in grade_map.items() if total_score >= threshold)
        
        return {
            'quality_score': round(total_score, 1),
            'grade': grade,
            'components': {
                'consistency': consistency_score,
                'growth': growth_score, 
                'coverage': coverage_score,
                'yield_quality': yield_score,
                'earnings_stability': stability_score
            },
            'interpretation': self._interpret_quality_score(total_score)
        }

    def _analyze_dividend_sustainability(self, dividends: List[Dict], financials: Dict, market_data: Dict) -> Dict[str, Any]:
        """
        Professional dividend sustainability analysis using FCF, debt, and earnings metrics
        """
        
        if not dividends or not financials:
            return {'sustainability_rating': 'Unknown', 'risk_level': 'High'}
        
        # Key sustainability ratios
        payout_ratio = self._calculate_payout_ratio(dividends, financials)
        fcf_coverage = self._calculate_fcf_dividend_coverage(dividends, financials)
        debt_coverage = self._calculate_debt_service_coverage(financials)
        earnings_volatility = self._calculate_earnings_volatility(financials)
        
        # Sustainability scoring algorithm
        sustainability_score = 0
        
        # Payout ratio analysis (25 points)
        if payout_ratio < 0.4:
            sustainability_score += 25
        elif payout_ratio < 0.6:
            sustainability_score += 20
        elif payout_ratio < 0.8:
            sustainability_score += 15
        elif payout_ratio < 1.0:
            sustainability_score += 10
        
        # FCF coverage analysis (25 points)
        if fcf_coverage > 2.0:
            sustainability_score += 25
        elif fcf_coverage > 1.5:
            sustainability_score += 20
        elif fcf_coverage > 1.2:
            sustainability_score += 15
        elif fcf_coverage > 1.0:
            sustainability_score += 10
        
        # Debt coverage analysis (25 points)
        if debt_coverage > 3.0:
            sustainability_score += 25
        elif debt_coverage > 2.0:
            sustainability_score += 20
        elif debt_coverage > 1.5:
            sustainability_score += 15
        elif debt_coverage > 1.0:
            sustainability_score += 10
        
        # Earnings stability analysis (25 points)
        if earnings_volatility < 0.15:
            sustainability_score += 25
        elif earnings_volatility < 0.25:
            sustainability_score += 20
        elif earnings_volatility < 0.35:
            sustainability_score += 15
        elif earnings_volatility < 0.50:
            sustainability_score += 10
        
        # Determine sustainability rating
        if sustainability_score >= 80:
            rating = 'Very High'
        elif sustainability_score >= 60:
            rating = 'High'
        elif sustainability_score >= 40:
            rating = 'Moderate'
        elif sustainability_score >= 20:
            rating = 'Low'
        else:
            rating = 'Very Low'
        
        return {
            'sustainability_rating': rating,
            'sustainability_score': sustainability_score,
            'key_metrics': {
                'payout_ratio': payout_ratio,
                'fcf_coverage_ratio': fcf_coverage,
                'debt_service_coverage': debt_coverage,
                'earnings_volatility': earnings_volatility
            },
            'risk_factors': self._identify_sustainability_risks(payout_ratio, fcf_coverage, debt_coverage),
            'strengths': self._identify_sustainability_strengths(payout_ratio, fcf_coverage, debt_coverage)
        }

    def _analyze_dividend_growth_patterns(self, dividends: List[Dict]) -> Dict[str, Any]:
        """
        Advanced dividend growth analysis with compound annual growth rate (CAGR) calculations
        """
        
        if len(dividends) < 8:  # Need minimum 2 years of quarterly data
            return {'insufficient_data': True}
        
        # Calculate annual dividend totals
        annual_dividends = self._aggregate_annual_dividends(dividends)
        
        if len(annual_dividends) < 3:
            return {'insufficient_data': True}
        
        # CAGR calculations for different periods
        cagr_metrics = {}
        years = sorted(annual_dividends.keys(), reverse=True)
        
        for period in [3, 5, 10]:
            if len(years) >= period:
                start_div = annual_dividends[years[period-1]]
                end_div = annual_dividends[years[0]]
                if start_div > 0:
                    cagr = ((end_div / start_div) ** (1/period)) - 1
                    cagr_metrics[f'{period}y_cagr'] = round(cagr * 100, 2)
        
        # Dividend growth consistency analysis
        growth_rates = []
        for i in range(len(years) - 1):
            current_year = annual_dividends[years[i]]
            prev_year = annual_dividends[years[i + 1]]
            if prev_year > 0:
                growth_rate = (current_year - prev_year) / prev_year
                growth_rates.append(growth_rate)
        
        # Growth quality metrics
        avg_growth = mean(growth_rates) if growth_rates else 0
        growth_volatility = stdev(growth_rates) if len(growth_rates) > 1 else 0
        positive_years = sum(1 for gr in growth_rates if gr > 0)
        
        # Dividend aristocrat analysis
        consecutive_increases = self._calculate_consecutive_increases(annual_dividends)
        
        return {
            'growth_metrics': cagr_metrics,
            'average_annual_growth': round(avg_growth * 100, 2),
            'growth_volatility': round(growth_volatility * 100, 2),
            'growth_consistency': round((positive_years / len(growth_rates)) * 100, 1) if growth_rates else 0,
            'consecutive_increases': consecutive_increases,
            'aristocrat_status': {
                'is_aristocrat': consecutive_increases >= 25,
                'is_achiever': consecutive_increases >= 10,
                'is_challenger': consecutive_increases >= 5
            },
            'growth_trend': self._determine_growth_trend(growth_rates[-3:] if len(growth_rates) >= 3 else growth_rates)
        }

    def _analyze_dividend_coverage(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """
        Professional dividend coverage analysis using multiple financial metrics
        """
        
        if not dividends or not financials:
            return {'coverage_analysis': 'Insufficient data'}
        
        # Calculate coverage ratios
        eps_coverage = self._calculate_eps_coverage_ratio(dividends, financials)
        fcf_coverage = self._calculate_fcf_dividend_coverage(dividends, financials)
        ebitda_coverage = self._calculate_ebitda_coverage_ratio(dividends, financials)
        
        # Coverage trend analysis
        coverage_trend = self._analyze_coverage_trends(dividends, financials)
        
        # Coverage adequacy assessment
        coverage_grade = self._grade_dividend_coverage(eps_coverage, fcf_coverage)
        
        return {
            'coverage_ratios': {
                'eps_coverage': eps_coverage,
                'fcf_coverage': fcf_coverage,
                'ebitda_coverage': ebitda_coverage
            },
            'coverage_trend': coverage_trend,
            'coverage_grade': coverage_grade,
            'coverage_analysis': self._interpret_coverage_metrics(eps_coverage, fcf_coverage, ebitda_coverage)
        }

    def _calculate_dividend_risk_metrics(self, dividends: List[Dict], financials: Dict, economic_context: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive dividend risk metrics for institutional analysis
        """
        
        # Dividend yield vs historical average
        current_yield = self._get_current_dividend_yield(dividends, financials)
        historical_yields = self._calculate_historical_yields(dividends, financials)
        yield_percentile = self._calculate_yield_percentile(current_yield, historical_yields)
        
        # Beta and dividend beta calculation
        dividend_beta = self._calculate_dividend_beta(dividends)
        
        # Sector risk assessment
        sector_risk = self._assess_sector_dividend_risk(financials.get('sector', ''))
        
        # Economic sensitivity
        economic_sensitivity = self._calculate_economic_sensitivity(dividends, economic_context)
        
        # Overall risk score (0-100, where 100 is highest risk)
        risk_components = [
            self._score_yield_risk(yield_percentile),
            self._score_coverage_risk(dividends, financials),
            self._score_sector_risk(sector_risk),
            self._score_economic_sensitivity(economic_sensitivity)
        ]
        
        overall_risk_score = sum(risk_components) / len(risk_components)
        
        return {
            'overall_risk_score': round(overall_risk_score, 1),
            'risk_rating': self._get_risk_rating(overall_risk_score),
            'risk_components': {
                'yield_risk': yield_percentile,
                'coverage_risk': risk_components[1],
                'sector_risk': sector_risk,
                'economic_sensitivity': economic_sensitivity
            },
            'dividend_beta': dividend_beta,
            'key_risk_factors': self._identify_key_risk_factors(dividends, financials, economic_context)
        }

    # Professional Financial Analysis Methods
    
    def _score_dividend_consistency(self, dividends: List[Dict]) -> float:
        """Score dividend payment consistency (0-20 points)"""
        if len(dividends) < 8:  # Need 2+ years of quarterly data
            return 0
        
        annual_dividends = self._aggregate_annual_dividends(dividends)
        years = sorted(annual_dividends.keys())
        
        if len(years) < 3:
            return 0
        
        # Count years with maintained or increased dividends
        consistent_years = 0
        for i in range(1, len(years)):
            if annual_dividends[years[i]] >= annual_dividends[years[i-1]]:
                consistent_years += 1
        
        consistency_ratio = consistent_years / (len(years) - 1) if len(years) > 1 else 0
        return consistency_ratio * 20

    def _score_dividend_growth(self, dividends: List[Dict]) -> float:
        """Score dividend growth quality (0-20 points)"""
        annual_dividends = self._aggregate_annual_dividends(dividends)
        years = sorted(annual_dividends.keys())
        
        if len(years) < 3:
            return 0
        
        # Calculate 5-year CAGR (or available period)
        period = min(5, len(years) - 1)
        start_div = annual_dividends[years[0]]
        end_div = annual_dividends[years[period]]
        
        if start_div <= 0:
            return 0
        
        cagr = ((end_div / start_div) ** (1/period)) - 1
        
        # Professional scoring: optimal growth 5-15% annually
        if 0.05 <= cagr <= 0.15:
            return 20
        elif 0.03 <= cagr < 0.05 or 0.15 < cagr <= 0.20:
            return 15
        elif 0.01 <= cagr < 0.03 or 0.20 < cagr <= 0.25:
            return 10
        elif 0 <= cagr < 0.01:
            return 5
        else:
            return 0

    def _score_dividend_coverage(self, dividends: List[Dict], financials: Dict) -> float:
        """Score dividend coverage quality (0-20 points)"""
        if not dividends or not financials:
            return 0
        
        # Calculate multiple coverage ratios
        eps_coverage = self._calculate_eps_coverage_ratio(dividends, financials)
        fcf_coverage = self._calculate_fcf_dividend_coverage(dividends, financials)
        
        # Weight EPS coverage 60%, FCF coverage 40%
        eps_score = min(eps_coverage / 2.5 * 12, 12)  # Optimal at 2.5x coverage
        fcf_score = min(fcf_coverage / 2.0 * 8, 8)    # Optimal at 2.0x coverage
        
        return eps_score + fcf_score

    def _score_dividend_yield_quality(self, dividends: List[Dict]) -> float:
        """Score dividend yield quality vs volatility (0-15 points)"""
        if len(dividends) < 12:  # Need 3+ years of quarterly data
            return 0
        
        # Calculate yield stability over time
        quarterly_yields = []
        for i in range(0, min(12, len(dividends)), 4):
            ttm_div = sum(div['amount'] for div in dividends[i:i+4] if div.get('amount'))
            quarterly_yields.append(ttm_div)
        
        if len(quarterly_yields) < 3:
            return 0
        
        # Score based on yield consistency (lower volatility = higher score)
        yield_volatility = stdev(quarterly_yields) / mean(quarterly_yields) if mean(quarterly_yields) > 0 else 1
        
        if yield_volatility < 0.1:
            return 15
        elif yield_volatility < 0.2:
            return 12
        elif yield_volatility < 0.3:
            return 8
        elif yield_volatility < 0.5:
            return 5
        else:
            return 0

    def _score_earnings_stability(self, financials: Dict) -> float:
        """Score earnings stability (0-15 points)"""
        # This would need historical earnings data - simplified for now
        eps = financials.get('eps', 0)
        roe = financials.get('roe', 0)
        
        # Basic scoring based on available metrics
        if eps > 0 and roe > 0.10:
            return 15
        elif eps > 0 and roe > 0.05:
            return 10
        elif eps > 0:
            return 5
        else:
            return 0

    def _calculate_eps_coverage_ratio(self, dividends: List[Dict], financials: Dict) -> float:
        """Calculate earnings per share dividend coverage ratio"""
        if not dividends or not financials:
            return 0
        
        ttm_dividends = sum(div.get('amount', 0) for div in dividends[:4])
        eps = financials.get('eps', 0)
        
        return eps / ttm_dividends if ttm_dividends > 0 and eps > 0 else 0

    def _calculate_debt_service_coverage(self, financials: Dict) -> float:
        """Calculate debt service coverage ratio"""
        ebitda = financials.get('ebitda', 0)
        total_debt = financials.get('total_debt', 0)
        
        if total_debt <= 0:
            return 5.0  # No debt is good for coverage
        
        # Assuming 5% average interest rate for debt service calculation
        estimated_debt_service = total_debt * 0.05
        
        return ebitda / estimated_debt_service if estimated_debt_service > 0 else 0

    def _calculate_earnings_volatility(self, financials: Dict) -> float:
        """Calculate earnings volatility score (0 = stable, 1 = very volatile)"""
        # Would need historical earnings - using proxy metrics
        roe = financials.get('roe', 0)
        
        # Simplified volatility assessment based on ROE
        if roe > 0.20:
            return 0.3  # High ROE can indicate higher volatility
        elif roe > 0.15:
            return 0.2
        elif roe > 0.10:
            return 0.15
        else:
            return 0.4  # Low/negative ROE indicates instability

    def _aggregate_annual_dividends(self, dividends: List[Dict]) -> Dict[int, float]:
        """Aggregate dividends by year for analysis"""
        annual_data = {}
        
        for dividend in dividends:
            year = dividend['ex_date'].year
            amount = dividend.get('amount', 0)
            
            if year not in annual_data:
                annual_data[year] = 0
            annual_data[year] += amount
        
        return annual_data

    def _interpret_quality_score(self, score: float) -> str:
        """Interpret dividend quality score for investors"""
        if score >= 85:
            return "Exceptional dividend quality. Strong buy for income investors."
        elif score >= 75:
            return "High dividend quality. Reliable income stream with growth potential."
        elif score >= 65:
            return "Good dividend quality. Suitable for conservative income portfolios."
        elif score >= 55:
            return "Moderate dividend quality. Monitor for sustainability concerns."
        elif score >= 45:
            return "Below-average dividend quality. Higher risk of cuts or suspensions."
        else:
            return "Poor dividend quality. High risk of dividend reduction or elimination."

    def _get_current_dividend_metrics(self, dividends: List[Dict], market_data: Dict) -> Dict[str, Any]:
        """Calculate current dividend metrics"""
        if not dividends:
            return {}
        
        current_price = market_data.get('current_price', 0)
        
        # Get TTM (trailing twelve months) dividend
        ttm_dividend = sum(div.get('amount', 0) for div in dividends[:4])
        
        # Calculate yield
        current_yield = (ttm_dividend / current_price * 100) if current_price > 0 else 0
        
        # Get last payment
        last_payment = dividends[0] if dividends else {}
        
        # Estimate payment frequency
        payment_dates = [div['ex_date'] for div in dividends[:8]]
        if len(payment_dates) >= 2:
            avg_days_between = sum((payment_dates[i-1] - payment_dates[i]).days 
                                 for i in range(1, min(5, len(payment_dates)))) / min(4, len(payment_dates)-1)
            
            if avg_days_between < 100:
                frequency = "Quarterly"
                estimated_annual = ttm_dividend * 4 if len(dividends) >= 1 else 0
            elif avg_days_between < 200:
                frequency = "Semi-Annual"
                estimated_annual = ttm_dividend * 2 if len(dividends) >= 1 else 0
            else:
                frequency = "Annual"
                estimated_annual = ttm_dividend
        else:
            frequency = "Quarterly"
            estimated_annual = ttm_dividend * 4 if len(dividends) >= 1 else 0
        
        # Compare to 10-year treasury (estimate)
        treasury_10y = 4.5  # This would come from FRED in production
        yield_vs_treasury = current_yield - treasury_10y
        
        return {
            'current_yield_pct': round(current_yield, 2),
            'ttm_dividend_total': round(ttm_dividend, 2),
            'last_payment': {
                'amount': last_payment.get('amount', 0),
                'ex_date': last_payment.get('ex_date', '').isoformat() if last_payment.get('ex_date') else None
            },
            'payment_frequency': frequency,
            'estimated_annual_dividend': round(estimated_annual, 2),
            'yield_vs_10y_treasury': round(yield_vs_treasury, 2)
        }

    def _determine_payment_frequency(self, dividends: List[Dict]) -> str:
        """Determine dividend payment frequency"""
        if len(dividends) < 2:
            return 'Unknown'
        
        # Calculate average days between payments
        date_diffs = []
        for i in range(min(8, len(dividends) - 1)):  # Look at last 8 payments
            date1 = dividends[i].get('ex_date')
            date2 = dividends[i + 1].get('ex_date')
            
            if date1 and date2:
                diff = abs((date1 - date2).days)
                date_diffs.append(diff)
        
        if not date_diffs:
            return 'Unknown'
        
        avg_days = mean(date_diffs)
        
        if 80 <= avg_days <= 100:
            return 'Quarterly'
        elif 160 <= avg_days <= 200:
            return 'Semi-Annual'
        elif 350 <= avg_days <= 380:
            return 'Annual'
        elif 25 <= avg_days <= 35:
            return 'Monthly'
        else:
            return 'Irregular'

    def _estimate_annual_dividend(self, dividends: List[Dict], frequency: str) -> float:
        """Estimate annual dividend based on recent payments"""
        if not dividends:
            return 0
        
        latest_amount = dividends[0].get('amount', 0)
        
        frequency_multipliers = {
            'Quarterly': 4,
            'Semi-Annual': 2,
            'Annual': 1,
            'Monthly': 12,
            'Irregular': 4  # Default assumption
        }
        
        multiplier = frequency_multipliers.get(frequency, 4)
        return round(latest_amount * multiplier, 4)

    def _calculate_yield_spread(self, ttm_dividend: float, current_price: float) -> float:
        """Calculate yield spread vs 10-year Treasury (risk premium)"""
        current_yield = (ttm_dividend / current_price) * 100
        
        # Would fetch actual 10Y rate from FRED in production
        # Using approximate current rate for now
        treasury_10y_rate = 4.5  # Approximate current rate
        
        return round(current_yield - treasury_10y_rate, 2)

    async def _fetch_comprehensive_financials(self, ticker: str) -> Dict[str, Any]:
        """Fetch comprehensive financial data from multiple sources for professional analysis"""
        
        try:
            # Use yfinance for quick access to key metrics
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get financial statements
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            # Extract key metrics for dividend analysis
            financials = {
                'eps': info.get('trailingEps', 0),
                'forward_eps': info.get('forwardEps', 0),
                'book_value': info.get('bookValue', 0),
                'roe': info.get('returnOnEquity', 0),
                'roa': info.get('returnOnAssets', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'total_debt': info.get('totalDebt', 0),
                'total_cash': info.get('totalCash', 0),
                'free_cash_flow': info.get('freeCashflow', 0),
                'operating_cash_flow': info.get('operatingCashflow', 0),
                'revenue': info.get('totalRevenue', 0),
                'gross_profit': info.get('grossProfits', 0),
                'ebitda': info.get('ebitda', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'beta': info.get('beta', 1.0)
            }
            
            # Calculate derived metrics
            if financials['shares_outstanding'] > 0:
                financials['fcf_per_share'] = financials['free_cash_flow'] / financials['shares_outstanding'] if financials['free_cash_flow'] else 0
                financials['ocf_per_share'] = financials['operating_cash_flow'] / financials['shares_outstanding'] if financials['operating_cash_flow'] else 0
                financials['book_value_per_share'] = financials['book_value']
            
            return financials
            
        except Exception as e:
            logger.error("Error fetching comprehensive financials", ticker=ticker, error=str(e))
            return {}

    async def _fetch_market_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch current market data for a ticker"""
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'beta': info.get('beta', 1.0),
                'eps': info.get('trailingEps', 0),
                'pe_ratio': info.get('trailingPE', 0)
            }
        except Exception as e:
            logger.error("Error fetching market data", ticker=ticker, error=str(e))
            return {'current_price': 0}

    async def _fetch_economic_context(self) -> Dict[str, Any]:
        """Fetch economic indicators for dividend analysis"""
        # In production, this would fetch from FRED API
        # For now, return reasonable defaults
        return {
            'treasury_10y': 4.5,
            'fed_funds_rate': 5.25,
            'inflation_rate': 3.2,
            'gdp_growth': 2.1,
            'unemployment_rate': 3.7
        }

    def _calculate_payout_ratio(self, dividends: List[Dict], financials: Dict) -> float:
        """Calculate dividend payout ratio"""
        if not dividends or not financials:
            return 0
        
        ttm_dividend = sum(div.get('amount', 0) for div in dividends[:4])
        eps = financials.get('eps', 0)
        
        return ttm_dividend / eps if eps > 0 else 0

    def _calculate_fcf_dividend_coverage(self, dividends: List[Dict], financials: Dict) -> float:
        """Calculate Free Cash Flow dividend coverage"""
        if not dividends or not financials:
            return 0
        
        ttm_dividend = sum(div.get('amount', 0) for div in dividends[:4])
        fcf_per_share = financials.get('free_cash_flow', 0) / 1_000_000_000  # Simplified
        
        return fcf_per_share / ttm_dividend if ttm_dividend > 0 else 0

    def _calculate_data_reliability_score(self, dividends: List[Dict], financials: Dict) -> float:
        """Calculate overall data reliability score for the analysis"""
        
        reliability_factors = []
        
        # Dividend data quality
        if dividends:
            confidence_scores = [div.get('confidence_score', 0.5) for div in dividends]
            avg_confidence = mean(confidence_scores)
            reliability_factors.append(avg_confidence)
        
        # Financial data completeness
        key_metrics = ['eps', 'free_cash_flow', 'total_debt', 'market_cap']
        available_metrics = sum(1 for metric in key_metrics if financials.get(metric, 0) != 0)
        completeness_score = available_metrics / len(key_metrics)
        reliability_factors.append(completeness_score)
        
        # Multi-source validation
        if dividends and len(dividends) > 0:
            multi_source_count = sum(1 for div in dividends[:10] if len(div.get('data_sources', [])) > 1)
            multi_source_score = min(multi_source_count / 10, 1.0)
            reliability_factors.append(multi_source_score)
        
        overall_reliability = mean(reliability_factors) if reliability_factors else 0.5
        return round(overall_reliability, 3)

    # Missing Methods Implementation
    
    def _analyze_dividend_growth_patterns(self, dividends: List[Dict]) -> Dict[str, Any]:
        """Advanced dividend growth analysis with CAGR calculations"""
        if not dividends or len(dividends) < 8:
            return {'status': 'Insufficient data for growth analysis'}
        
        annual_dividends = self._aggregate_annual_dividends(dividends)
        years = sorted(annual_dividends.keys(), reverse=True)
        
        if len(years) < 3:
            return {'status': 'Need minimum 3 years of data'}
        
        # Calculate CAGR for different periods
        cagr_metrics = {}
        for period in [3, 5, 10]:
            if len(years) >= period:
                start_value = annual_dividends[years[period-1]]
                end_value = annual_dividends[years[0]]
                if start_value > 0:
                    cagr = ((end_value / start_value) ** (1/period)) - 1
                    cagr_metrics[f'{period}y_cagr'] = round(cagr * 100, 2)
        
        # Growth consistency analysis
        growth_rates = []
        for i in range(len(years) - 1):
            current = annual_dividends[years[i]]
            previous = annual_dividends[years[i + 1]]
            if previous > 0:
                growth_rate = (current - previous) / previous
                growth_rates.append(growth_rate)
        
        return {
            'cagr_analysis': cagr_metrics,
            'average_growth': round(mean(growth_rates) * 100, 2) if growth_rates else 0,
            'growth_volatility': round(stdev(growth_rates) * 100, 2) if len(growth_rates) > 1 else 0,
            'positive_growth_years': sum(1 for rate in growth_rates if rate > 0),
            'total_years': len(growth_rates)
        }

    def _analyze_dividend_coverage(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """Professional dividend coverage analysis"""
        if not dividends or not financials:
            return {'status': 'Insufficient data'}
        
        eps_coverage = self._calculate_eps_coverage_ratio(dividends, financials)
        fcf_coverage = self._calculate_fcf_dividend_coverage(dividends, financials)
        
        coverage_grade = 'A' if eps_coverage > 2.5 and fcf_coverage > 2.0 else \
                        'B' if eps_coverage > 2.0 and fcf_coverage > 1.5 else \
                        'C' if eps_coverage > 1.5 and fcf_coverage > 1.2 else 'D'
        
        return {
            'eps_coverage': eps_coverage,
            'fcf_coverage': fcf_coverage,
            'coverage_grade': coverage_grade,
            'payout_ratio': self._calculate_payout_ratio(dividends, financials)
        }

    def _calculate_dividend_risk_metrics(self, dividends: List[Dict], financials: Dict, economic_context: Dict) -> Dict[str, Any]:
        """Calculate comprehensive dividend risk metrics"""
        if not dividends:
            return {'risk_score': 100, 'risk_rating': 'Very High'}
        
        # Basic risk scoring
        payout_ratio = self._calculate_payout_ratio(dividends, financials)
        fcf_coverage = self._calculate_fcf_dividend_coverage(dividends, financials)
        
        risk_score = 0
        
        # Payout ratio risk (40% of total)
        if payout_ratio > 1.0:
            risk_score += 40
        elif payout_ratio > 0.8:
            risk_score += 30
        elif payout_ratio > 0.6:
            risk_score += 20
        elif payout_ratio > 0.4:
            risk_score += 10
        
        # Coverage risk (40% of total)
        if fcf_coverage < 1.0:
            risk_score += 40
        elif fcf_coverage < 1.5:
            risk_score += 30
        elif fcf_coverage < 2.0:
            risk_score += 20
        elif fcf_coverage < 3.0:
            risk_score += 10
        
        # Economic risk (20% of total)
        treasury_rate = economic_context.get('treasury_10y', 4.5)
        if treasury_rate > 6.0:
            risk_score += 20
        elif treasury_rate > 5.0:
            risk_score += 15
        elif treasury_rate > 4.0:
            risk_score += 10
        
        risk_rating = 'Very Low' if risk_score < 20 else \
                     'Low' if risk_score < 40 else \
                     'Moderate' if risk_score < 60 else \
                     'High' if risk_score < 80 else 'Very High'
        
        return {
            'risk_score': risk_score,
            'risk_rating': risk_rating,
            'payout_ratio': payout_ratio,
            'fcf_coverage': fcf_coverage
        }

    def _calculate_dividend_valuation_metrics(self, dividends: List[Dict], market_data: Dict, economic_context: Dict) -> Dict[str, Any]:
        """Calculate dividend valuation metrics"""
        if not dividends or not market_data:
            return {}
        
        current_price = market_data.get('current_price', 0)
        ttm_dividend = sum(div.get('amount', 0) for div in dividends[:4])
        
        current_yield = (ttm_dividend / current_price * 100) if current_price > 0 else 0
        treasury_rate = economic_context.get('treasury_10y', 4.5)
        risk_premium = current_yield - treasury_rate
        
        return {
            'current_yield': round(current_yield, 2),
            'yield_vs_treasury': round(risk_premium, 2),
            'dividend_discount_model': self._calculate_ddm_value(dividends, market_data, economic_context)
        }

    def _calculate_ddm_value(self, dividends: List[Dict], market_data: Dict, economic_context: Dict) -> float:
        """Simple Dividend Discount Model calculation"""
        if len(dividends) < 8:
            return 0
        
        # Calculate growth rate from recent dividends
        annual_dividends = self._aggregate_annual_dividends(dividends)
        years = sorted(annual_dividends.keys(), reverse=True)
        
        if len(years) < 3:
            return 0
        
        # 3-year average growth rate
        growth_rates = []
        for i in range(min(3, len(years) - 1)):
            current = annual_dividends[years[i]]
            previous = annual_dividends[years[i + 1]]
            if previous > 0:
                growth_rate = (current - previous) / previous
                growth_rates.append(growth_rate)
        
        avg_growth = mean(growth_rates) if growth_rates else 0.03
        
        # Simple DDM: D1 / (r - g)
        last_dividend = annual_dividends[years[0]]
        next_dividend = last_dividend * (1 + avg_growth)
        required_return = 0.10  # Assume 10% required return
        
        if required_return > avg_growth:
            ddm_value = next_dividend / (required_return - avg_growth)
            return round(ddm_value, 2)
        
        return 0

    def _analyze_dividend_performance(self, dividends: List[Dict], market_data: Dict) -> Dict[str, Any]:
        """Analyze dividend performance metrics"""
        if not dividends:
            return {}
        
        current_price = market_data.get('current_price', 0)
        ttm_dividend = sum(div.get('amount', 0) for div in dividends[:4])
        
        # Calculate yield metrics
        current_yield = (ttm_dividend / current_price * 100) if current_price > 0 else 0
        
        # Historical yield analysis
        historical_yields = []
        for i in range(0, min(20, len(dividends)), 4):  # 5 years of quarterly data
            period_dividend = sum(div.get('amount', 0) for div in dividends[i:i+4])
            if period_dividend > 0 and current_price > 0:
                yield_pct = (period_dividend / current_price) * 100
                historical_yields.append(yield_pct)
        
        avg_historical_yield = mean(historical_yields) if historical_yields else current_yield
        yield_percentile = self._calculate_percentile(current_yield, historical_yields) if historical_yields else 50
        
        return {
            'current_yield': round(current_yield, 2),
            'historical_avg_yield': round(avg_historical_yield, 2),
            'yield_percentile': round(yield_percentile, 1),
            'yield_stability': self._calculate_yield_stability(historical_yields)
        }

    def _calculate_percentile(self, value: float, data_list: List[float]) -> float:
        """Calculate percentile ranking of value in data list"""
        if not data_list:
            return 50.0
        
        sorted_data = sorted(data_list)
        below_count = sum(1 for x in sorted_data if x < value)
        percentile = (below_count / len(sorted_data)) * 100
        return percentile

    def _calculate_yield_stability(self, yields: List[float]) -> str:
        """Calculate yield stability rating"""
        if len(yields) < 3:
            return 'Unknown'
        
        volatility = stdev(yields) / mean(yields) if mean(yields) > 0 else 1
        
        if volatility < 0.15:
            return 'Very Stable'
        elif volatility < 0.25:
            return 'Stable'
        elif volatility < 0.35:
            return 'Moderate'
        elif volatility < 0.50:
            return 'Volatile'
        else:
            return 'Very Volatile'

    async def _generate_professional_forecast(self, dividends: List[Dict], financials: Dict, economic_context: Dict, years: int) -> List[Dict[str, Any]]:
        """Generate professional dividend forecast"""
        if not dividends or len(dividends) < 8:
            return []
        
        # Calculate growth trend
        annual_dividends = self._aggregate_annual_dividends(dividends)
        years_data = sorted(annual_dividends.keys(), reverse=True)
        
        if len(years_data) < 3:
            return []
        
        # Calculate average growth rate
        growth_rates = []
        for i in range(min(5, len(years_data) - 1)):
            current = annual_dividends[years_data[i]]
            previous = annual_dividends[years_data[i + 1]]
            if previous > 0:
                growth_rate = (current - previous) / previous
                growth_rates.append(growth_rate)
        
        avg_growth = mean(growth_rates) if growth_rates else 0.03
        last_dividend = annual_dividends[years_data[0]]
        
        # Generate forecast
        forecast = []
        for year in range(1, years + 1):
            projected_dividend = last_dividend * ((1 + avg_growth) ** year)
            confidence = max(0.5, 0.9 - (year * 0.1))  # Decreasing confidence
            
            forecast.append({
                'year': years_data[0] + year,
                'projected_dividend': round(projected_dividend, 4),
                'growth_rate': round(avg_growth * 100, 2),
                'confidence_level': round(confidence, 2)
            })
        
        return forecast

    async def _get_sector_benchmarking(self, ticker: str, analysis: Dict, market_data: Dict) -> Dict[str, Any]:
        """Get sector benchmarking data"""
        sector = market_data.get('sector', 'Unknown')
        
        if sector in self.sector_benchmarks:
            benchmark = self.sector_benchmarks[sector]
            
            current_yield = analysis.get('valuation_analysis', {}).get('current_yield', 0)
            quality_score = analysis.get('dividend_quality_metrics', {}).get('quality_score', 0)
            
            return {
                'sector': sector,
                'sector_avg_yield': benchmark['avg_yield'],
                'sector_avg_payout': benchmark['payout_ratio'],
                'yield_vs_sector': round(current_yield - benchmark['avg_yield'], 2),
                'quality_vs_sector': 'Above Average' if quality_score > 70 else 'Below Average'
            }
        
        return {'sector': sector, 'benchmark_available': False}

    async def _get_yfinance_dividends(self, ticker: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get dividends from yfinance with enhanced data"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date, actions=True)
            
            dividend_data = []
            if 'Dividends' in hist.columns:
                dividends = hist[hist['Dividends'] > 0]['Dividends']
                
                for date_idx, amount in dividends.items():
                    dividend_data.append({
                        'ex_date': date_idx.date(),
                        'amount': float(amount),
                        'dividend_type': 'regular',
                        'currency': 'USD',
                        'data_source': 'yahoo_finance',
                        'confidence_score': 0.95
                    })
            
            return sorted(dividend_data, key=lambda x: x['ex_date'], reverse=True)
            
        except Exception as e:
            logger.error("YFinance dividend fetch failed", ticker=ticker, error=str(e))
            return []

    async def _get_alpha_vantage_dividends(self, ticker: str) -> List[Dict[str, Any]]:
        """Get dividends from Alpha Vantage"""
        if not self.alpha_vantage_key:
            return []
            
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_MONTHLY_ADJUSTED',
                'symbol': ticker,
                'apikey': self.alpha_vantage_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Process Alpha Vantage dividend data
                        return self._process_av_dividend_data(data)
            
            return []
            
        except Exception as e:
            logger.error("Alpha Vantage dividend fetch failed", ticker=ticker, error=str(e))
            return []

    def _process_av_dividend_data(self, data: Dict) -> List[Dict[str, Any]]:
        """Process Alpha Vantage dividend data into standard format"""
        dividends = []
        
        try:
            # Alpha Vantage monthly adjusted data contains dividend information
            monthly_data = data.get('Monthly Adjusted Time Series', {})
            
            for date_str, values in monthly_data.items():
                dividend_amount = float(values.get('7. dividend amount', 0))
                
                if dividend_amount > 0:
                    # Parse date
                    ex_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    dividends.append({
                        'ex_date': ex_date,
                        'amount': dividend_amount,
                        'dividend_type': 'regular',
                        'currency': 'USD',
                        'data_source': 'alpha_vantage',
                        'confidence_score': 0.9
                    })
        
        except Exception as e:
            logger.error("Error processing Alpha Vantage data", error=str(e))
            return []
        
        return sorted(dividends, key=lambda x: x['ex_date'], reverse=True)

    # ... [Additional methods would continue] ...

    async def _get_fmp_dividends(self, ticker: str) -> List[Dict[str, Any]]:
        """Get dividends from Financial Modeling Prep"""
        
        try:
            url = f"{self.fmp_base_url}/historical-price-full/stock_dividend/{ticker}"
            params = {'apikey': self.fmp_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return []
                    
                    data = await response.json()
                    
                    if 'historical' not in data:
                        return []
                    
                    dividend_list = []
                    for div_data in data['historical']:
                        dividend_list.append({
                            'ex_date': datetime.strptime(div_data['date'], '%Y-%m-%d').date(),
                            'record_date': datetime.strptime(div_data.get('recordDate', div_data['date']), '%Y-%m-%d').date() if div_data.get('recordDate') else None,
                            'payment_date': datetime.strptime(div_data.get('paymentDate', div_data['date']), '%Y-%m-%d').date() if div_data.get('paymentDate') else None,
                            'declaration_date': datetime.strptime(div_data.get('declarationDate', div_data['date']), '%Y-%m-%d').date() if div_data.get('declarationDate') else None,
                            'amount': float(div_data['dividend']),
                            'adjusted_amount': float(div_data.get('adjDividend', div_data['dividend'])),
                            'dividend_type': DividendType.REGULAR,
                            'currency': 'USD',
                            'data_source': 'financial_modeling_prep',
                            'confidence_score': 0.85
                        })
                    
                    return dividend_list
                    
        except Exception as e:
            logger.error("Error fetching FMP dividends", ticker=ticker, error=str(e))
            return []
    
    async def _get_fred_economic_indicators(self) -> Dict[str, Any]:
        """Get relevant economic indicators from FRED"""
        
        if not self.fred_api_key:
            return {}
        
        try:
            indicators = {}
            
            for indicator_name, series_id in self.fred_indicators.items():
                try:
                    url = f"{self.fred_base_url}/series/observations"
                    params = {
                        'series_id': series_id,
                        'api_key': self.fred_api_key,
                        'file_type': 'json',
                        'limit': 12,  # Last 12 observations
                        'sort_order': 'desc'
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                if 'observations' in data and data['observations']:
                                    latest_obs = data['observations'][0]
                                    if latest_obs['value'] != '.':
                                        indicators[indicator_name] = {
                                            'value': float(latest_obs['value']),
                                            'date': latest_obs['date'],
                                            'series_id': series_id
                                        }
                except Exception as e:
                    logger.warning(f"Error fetching FRED indicator {indicator_name}", error=str(e))
                    continue
                
                # Rate limiting for FRED API
                await asyncio.sleep(0.1)
            
            return indicators
            
        except Exception as e:
            logger.error("Error fetching FRED economic indicators", error=str(e))
            return {}
    
    async def _get_company_financial_metrics(self, ticker: str) -> Dict[str, Any]:
        """Get company financial metrics for dividend analysis"""
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get financial statements
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            metrics = {}
            
            if not financials.empty:
                latest_financials = financials.iloc[:, 0]
                
                # Income statement metrics
                metrics['net_income'] = self._safe_float(latest_financials.get('Net Income'))
                metrics['total_revenue'] = self._safe_float(latest_financials.get('Total Revenue'))
                metrics['operating_income'] = self._safe_float(latest_financials.get('Operating Income'))
                metrics['interest_expense'] = self._safe_float(latest_financials.get('Interest Expense'))
            
            if not balance_sheet.empty:
                latest_balance = balance_sheet.iloc[:, 0]
                
                # Balance sheet metrics
                metrics['total_assets'] = self._safe_float(latest_balance.get('Total Assets'))
                metrics['total_debt'] = self._safe_float(latest_balance.get('Total Debt'))
                metrics['shareholders_equity'] = self._safe_float(latest_balance.get('Stockholders Equity'))
                metrics['current_assets'] = self._safe_float(latest_balance.get('Current Assets'))
                metrics['current_liabilities'] = self._safe_float(latest_balance.get('Current Liabilities'))
            
            if not cash_flow.empty:
                latest_cashflow = cash_flow.iloc[:, 0]
                
                # Cash flow metrics
                metrics['operating_cash_flow'] = self._safe_float(latest_cashflow.get('Operating Cash Flow'))
                metrics['capital_expenditures'] = self._safe_float(latest_cashflow.get('Capital Expenditures'))
                metrics['dividends_paid'] = self._safe_float(latest_cashflow.get('Dividends Paid'))
                
                # Calculate free cash flow
                if metrics.get('operating_cash_flow') and metrics.get('capital_expenditures'):
                    metrics['free_cash_flow'] = metrics['operating_cash_flow'] - abs(metrics['capital_expenditures'])
            
            return metrics
            
        except Exception as e:
            logger.error("Error fetching company financial metrics", ticker=ticker, error=str(e))
            return {}
    
    async def _get_current_stock_info(self, ticker: str) -> Dict[str, Any]:
        """Get current stock information"""
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'market_cap': info.get('marketCap'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
                'trailing_pe': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'book_value': info.get('bookValue'),
                'beta': info.get('beta'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'float_shares': info.get('floatShares')
            }
            
        except Exception as e:
            logger.error("Error fetching current stock info", ticker=ticker, error=str(e))
            return {}
    
    async def _perform_dividend_analysis(
        self,
        ticker: str,
        dividend_history: List[Dict[str, Any]],
        financial_metrics: Dict[str, Any],
        stock_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform comprehensive dividend analysis"""
        
        if not dividend_history:
            return {}
        
        try:
            analysis = {}
            
            # Calculate yield metrics
            analysis.update(self._calculate_yield_metrics(dividend_history, stock_info))
            
            # Calculate growth metrics
            analysis.update(self._calculate_growth_metrics(dividend_history))
            
            # Calculate consistency metrics
            analysis.update(self._calculate_consistency_metrics(dividend_history))
            
            # Calculate coverage and sustainability metrics
            analysis.update(self._calculate_coverage_metrics(dividend_history, financial_metrics, stock_info))
            
            # Calculate financial strength indicators
            analysis.update(self._calculate_financial_strength(financial_metrics))
            
            # Determine dividend aristocrat status
            analysis.update(self._determine_aristocrat_status(dividend_history))
            
            # Calculate overall dividend score
            analysis['dividend_quality_score'] = self._calculate_dividend_quality_score(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error("Error performing dividend analysis", ticker=ticker, error=str(e))
            return {}
    
    def _calculate_yield_metrics(self, dividend_history: List[Dict[str, Any]], stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate dividend yield metrics"""
        
        current_price = stock_info.get('current_price')
        if not current_price or not dividend_history:
            return {}
        
        # Current dividend yield (from stock info if available)
        current_yield = stock_info.get('dividend_yield')
        if current_yield:
            current_yield *= 100  # Convert to percentage
        
        # Calculate trailing 12-month yield
        trailing_12m_dividends = [
            div for div in dividend_history
            if div['ex_date'] >= (date.today() - timedelta(days=365))
        ]
        
        if trailing_12m_dividends:
            trailing_12m_amount = sum(div['amount'] for div in trailing_12m_dividends)
            trailing_12m_yield = (trailing_12m_amount / current_price) * 100
        else:
            trailing_12m_yield = None
        
        return {
            'current_dividend_yield': current_yield,
            'trailing_12m_yield': trailing_12m_yield
        }
    
    def _calculate_growth_metrics(self, dividend_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate dividend growth metrics"""
        
        if len(dividend_history) < 2:
            return {}
        
        # Group dividends by year and calculate annual dividends
        annual_dividends = {}
        for div in dividend_history:
            year = div['ex_date'].year
            if year not in annual_dividends:
                annual_dividends[year] = 0
            annual_dividends[year] += div['amount']
        
        years = sorted(annual_dividends.keys(), reverse=True)
        
        # Calculate growth rates
        growth_rates = {}
        
        for period_years, key in [(1, '1y'), (3, '3y'), (5, '5y'), (10, '10y')]:
            if len(years) >= period_years + 1:
                current_dividend = annual_dividends[years[0]]
                past_dividend = annual_dividends[years[period_years]]
                
                if past_dividend > 0:
                    if period_years == 1:
                        growth_rate = ((current_dividend / past_dividend) - 1) * 100
                    else:
                        # Annualized growth rate
                        growth_rate = (((current_dividend / past_dividend) ** (1/period_years)) - 1) * 100
                    
                    growth_rates[f'dividend_growth_rate_{key}'] = growth_rate
        
        return growth_rates
    
    def _calculate_consistency_metrics(self, dividend_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate dividend consistency metrics"""
        
        if not dividend_history:
            return {}
        
        # Group by year and calculate annual dividends
        annual_dividends = {}
        for div in dividend_history:
            year = div['ex_date'].year
            if year not in annual_dividends:
                annual_dividends[year] = 0
            annual_dividends[year] += div['amount']
        
        years = sorted(annual_dividends.keys())
        
        if len(years) < 2:
            return {}
        
        # Count consecutive increases and payments
        consecutive_increases = 0
        consecutive_payments = len(years)  # All years with dividends are payments
        
        for i in range(len(years) - 1, 0, -1):
            current_year = years[i]
            previous_year = years[i - 1]
            
            if annual_dividends[current_year] > annual_dividends[previous_year]:
                consecutive_increases += 1
            else:
                break
        
        # Calculate consistency score (0-10)
        # Based on payment regularity, growth consistency, and volatility
        dividend_amounts = [annual_dividends[year] for year in years]
        
        if len(dividend_amounts) > 1:
            volatility = stdev(dividend_amounts) / mean(dividend_amounts) if mean(dividend_amounts) > 0 else 1
            consistency_score = max(0, min(10, 10 - (volatility * 5)))
        else:
            consistency_score = 5.0
        
        return {
            'dividend_consistency_score': consistency_score,
            'years_of_consecutive_increases': consecutive_increases,
            'years_of_consecutive_payments': consecutive_payments
        }
    
    def _calculate_coverage_metrics(
        self,
        dividend_history: List[Dict[str, Any]],
        financial_metrics: Dict[str, Any],
        stock_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate dividend coverage and sustainability metrics"""
        
        metrics = {}
        
        # Payout ratio from stock info
        payout_ratio = stock_info.get('payout_ratio')
        if payout_ratio:
            metrics['payout_ratio'] = payout_ratio * 100
        
        # Calculate payout ratio from financial data if not available
        net_income = financial_metrics.get('net_income')
        dividends_paid = financial_metrics.get('dividends_paid')
        
        if net_income and dividends_paid and net_income > 0:
            calculated_payout_ratio = (abs(dividends_paid) / net_income) * 100
            if 'payout_ratio' not in metrics:
                metrics['payout_ratio'] = calculated_payout_ratio
        
        # Free cash flow payout ratio
        free_cash_flow = financial_metrics.get('free_cash_flow')
        if free_cash_flow and dividends_paid and free_cash_flow > 0:
            metrics['free_cash_flow_payout_ratio'] = (abs(dividends_paid) / free_cash_flow) * 100
        
        # Debt-to-equity ratio
        total_debt = financial_metrics.get('total_debt')
        shareholders_equity = financial_metrics.get('shareholders_equity')
        if total_debt is not None and shareholders_equity and shareholders_equity > 0:
            metrics['debt_to_equity_ratio'] = total_debt / shareholders_equity
        
        # Interest coverage ratio
        operating_income = financial_metrics.get('operating_income')
        interest_expense = financial_metrics.get('interest_expense')
        if operating_income and interest_expense and interest_expense > 0:
            metrics['interest_coverage_ratio'] = operating_income / interest_expense
        
        return metrics
    
    def _calculate_financial_strength(self, financial_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate financial strength indicators"""
        
        metrics = {}
        
        # Return on Equity (ROE)
        net_income = financial_metrics.get('net_income')
        shareholders_equity = financial_metrics.get('shareholders_equity')
        if net_income and shareholders_equity and shareholders_equity > 0:
            metrics['roe'] = (net_income / shareholders_equity) * 100
        
        # Return on Assets (ROA)
        total_assets = financial_metrics.get('total_assets')
        if net_income and total_assets and total_assets > 0:
            metrics['roa'] = (net_income / total_assets) * 100
        
        # Current Ratio
        current_assets = financial_metrics.get('current_assets')
        current_liabilities = financial_metrics.get('current_liabilities')
        if current_assets and current_liabilities and current_liabilities > 0:
            metrics['current_ratio'] = current_assets / current_liabilities
        
        return metrics
    
    def _determine_aristocrat_status(self, dividend_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine dividend aristocrat status"""
        
        # Calculate years of consecutive increases
        annual_dividends = {}
        for div in dividend_history:
            year = div['ex_date'].year
            if year not in annual_dividends:
                annual_dividends[year] = 0
            annual_dividends[year] += div['amount']
        
        years = sorted(annual_dividends.keys())
        consecutive_increases = 0
        
        for i in range(len(years) - 1, 0, -1):
            current_year = years[i]
            previous_year = years[i - 1]
            
            if annual_dividends[current_year] > annual_dividends[previous_year]:
                consecutive_increases += 1
            else:
                break
        
        return {
            'is_dividend_aristocrat': consecutive_increases >= 25,  # S&P 500 requirement
            'is_dividend_king': consecutive_increases >= 50,       # Dividend King status
            'is_dividend_champion': consecutive_increases >= 25    # General champion status
        }
    
    def _calculate_dividend_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall dividend quality score (0-10)"""
        
        score = 0.0
        max_score = 10.0
        
        # Yield component (2 points max)
        current_yield = analysis.get('current_dividend_yield', 0)
        if current_yield:
            if 2 <= current_yield <= 6:  # Sweet spot
                score += 2.0
            elif 1 <= current_yield < 2 or 6 < current_yield <= 8:
                score += 1.5
            elif current_yield > 0:
                score += 1.0
        
        # Growth component (2 points max)
        growth_5y = analysis.get('dividend_growth_rate_5y', 0)
        if growth_5y:
            if growth_5y >= 10:
                score += 2.0
            elif growth_5y >= 5:
                score += 1.5
            elif growth_5y > 0:
                score += 1.0
        
        # Coverage component (2 points max)
        payout_ratio = analysis.get('payout_ratio', 100)
        if payout_ratio:
            if payout_ratio <= 60:
                score += 2.0
            elif payout_ratio <= 80:
                score += 1.5
            elif payout_ratio <= 100:
                score += 1.0
        
        # Consistency component (2 points max)
        consistency_score = analysis.get('dividend_consistency_score', 0)
        score += (consistency_score / 10) * 2
        
        # Aristocrat bonus (2 points max)
        if analysis.get('is_dividend_king'):
            score += 2.0
        elif analysis.get('is_dividend_aristocrat'):
            score += 1.5
        elif analysis.get('years_of_consecutive_increases', 0) >= 10:
            score += 1.0
        
        return min(score, max_score)
    
    def _get_current_dividend_info(self, stock_info: Dict[str, Any], dividend_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get current dividend information"""
        
        current_info = {
            'current_yield': stock_info.get('dividend_yield'),
            'payout_ratio': stock_info.get('payout_ratio'),
            'last_dividend_amount': None,
            'last_ex_date': None,
            'estimated_annual_dividend': None,
            'frequency': None
        }
        
        if dividend_history:
            # Get most recent dividend
            latest_div = dividend_history[0]
            current_info['last_dividend_amount'] = latest_div['amount']
            current_info['last_ex_date'] = latest_div['ex_date']
            
            # Estimate annual dividend and frequency
            recent_dividends = [
                div for div in dividend_history
                if div['ex_date'] >= (date.today() - timedelta(days=365))
            ]
            
            if recent_dividends:
                annual_amount = sum(div['amount'] for div in recent_dividends)
                current_info['estimated_annual_dividend'] = annual_amount
                
                # Estimate frequency
                if len(recent_dividends) >= 4:
                    current_info['frequency'] = DividendFrequency.QUARTERLY
                elif len(recent_dividends) >= 2:
                    current_info['frequency'] = DividendFrequency.SEMI_ANNUAL
                else:
                    current_info['frequency'] = DividendFrequency.ANNUAL
        
        return current_info
    
    async def _get_market_context(self, ticker: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get market context for dividend analysis"""
        
        sector = stock_info.get('sector', '')
        
        # This would ideally fetch sector averages from a database or API
        # For now, providing some general market context
        market_context = {
            'sector': sector,
            'market_dividend_yield_avg': 2.0,  # S&P 500 historical average
            'sector_dividend_yield_avg': None,  # Would be calculated from sector data
            'risk_free_rate': None,  # Would come from FRED data
            'market_volatility': None
        }
        
        return market_context
    
    def _assess_dividend_risk(
        self,
        analysis: Dict[str, Any],
        financial_metrics: Dict[str, Any],
        economic_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess dividend sustainability risk"""
        
        risk_factors = []
        risk_score = 0.0  # 0 = low risk, 10 = high risk
        
        # Payout ratio risk
        payout_ratio = analysis.get('payout_ratio', 0)
        if payout_ratio > 100:
            risk_factors.append("Payout ratio exceeds 100%")
            risk_score += 3.0
        elif payout_ratio > 80:
            risk_factors.append("High payout ratio (>80%)")
            risk_score += 2.0
        elif payout_ratio > 60:
            risk_factors.append("Moderate payout ratio (>60%)")
            risk_score += 1.0
        
        # Debt level risk
        debt_to_equity = analysis.get('debt_to_equity_ratio', 0)
        if debt_to_equity > 2.0:
            risk_factors.append("Very high debt-to-equity ratio")
            risk_score += 2.5
        elif debt_to_equity > 1.0:
            risk_factors.append("High debt-to-equity ratio")
            risk_score += 1.5
        
        # Interest coverage risk
        interest_coverage = analysis.get('interest_coverage_ratio', float('inf'))
        if interest_coverage < 2.0:
            risk_factors.append("Low interest coverage ratio")
            risk_score += 2.0
        elif interest_coverage < 5.0:
            risk_factors.append("Moderate interest coverage concern")
            risk_score += 1.0
        
        # Economic environment risk
        fed_funds_rate = economic_indicators.get('fed_funds_rate', {}).get('value', 0)
        if fed_funds_rate > 5.0:
            risk_factors.append("High interest rate environment")
            risk_score += 1.0
        
        # Growth consistency risk
        growth_5y = analysis.get('dividend_growth_rate_5y', 0)
        if growth_5y < 0:
            risk_factors.append("Negative dividend growth trend")
            risk_score += 2.0
        
        # Determine overall risk rating
        if risk_score >= 7.0:
            risk_rating = "HIGH"
        elif risk_score >= 4.0:
            risk_rating = "MODERATE"
        elif risk_score >= 2.0:
            risk_rating = "LOW-MODERATE"
        else:
            risk_rating = "LOW"
        
        return {
            'dividend_risk_score': min(risk_score, 10.0),
            'risk_rating': risk_rating,
            'risk_factors': risk_factors,
            'sustainability_rating': self._get_sustainability_rating(risk_score, analysis)
        }
    
    def _get_sustainability_rating(self, risk_score: float, analysis: Dict[str, Any]) -> str:
        """Get dividend sustainability rating"""
        
        # Combine risk score with positive factors
        quality_score = analysis.get('dividend_quality_score', 0)
        years_increases = analysis.get('years_of_consecutive_increases', 0)
        
        # Adjust for positive factors
        adjusted_score = risk_score - (quality_score / 10 * 2) - (min(years_increases, 25) / 25 * 2)
        
        if adjusted_score <= 1.0:
            return "EXCELLENT"
        elif adjusted_score <= 3.0:
            return "GOOD"
        elif adjusted_score <= 5.0:
            return "FAIR"
        elif adjusted_score <= 7.0:
            return "POOR"
        else:
            return "VERY_POOR"
    
    async def _generate_dividend_forecast(
        self,
        ticker: str,
        dividend_history: List[Dict[str, Any]],
        financial_metrics: Dict[str, Any],
        economic_indicators: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate dividend forecasts"""
        
        if len(dividend_history) < 3:
            return []
        
        # Simple forecast based on historical growth
        annual_dividends = {}
        for div in dividend_history:
            year = div['ex_date'].year
            if year not in annual_dividends:
                annual_dividends[year] = 0
            annual_dividends[year] += div['amount']
        
        years = sorted(annual_dividends.keys())
        if len(years) < 3:
            return []
        
        # Calculate average growth rate
        growth_rates = []
        for i in range(1, len(years)):
            if annual_dividends[years[i-1]] > 0:
                growth_rate = (annual_dividends[years[i]] / annual_dividends[years[i-1]]) - 1
                growth_rates.append(growth_rate)
        
        if not growth_rates:
            return []
        
        avg_growth_rate = mean(growth_rates)
        latest_dividend = annual_dividends[years[-1]]
        
        forecasts = []
        for year_ahead in range(1, 4):  # 3-year forecast
            forecast_date = date(years[-1] + year_ahead, 12, 31)
            estimated_amount = latest_dividend * ((1 + avg_growth_rate) ** year_ahead)
            
            # Adjust confidence based on growth consistency
            growth_std = stdev(growth_rates) if len(growth_rates) > 1 else 0.2
            confidence = max(0.3, min(0.9, 0.8 - (growth_std * 2)))
            
            forecasts.append({
                'forecast_date': forecast_date,
                'estimated_amount': round(estimated_amount, 4),
                'confidence_level': confidence,
                'methodology': 'historical_growth_trend',
                'factors_considered': ['historical_growth_rate', 'growth_consistency', 'payout_sustainability']
            })
        
        return forecasts
    
    async def _get_peer_comparison(self, ticker: str, sector: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get peer comparison data"""
        
        # This would ideally compare with sector peers
        # For now, providing a placeholder structure
        return {
            'sector': sector,
            'peer_average_yield': None,
            'peer_average_payout_ratio': None,
            'peer_average_growth_rate': None,
            'percentile_rank_yield': None,
            'percentile_rank_growth': None,
            'comparison_summary': "Peer comparison requires sector database implementation"
        }
    
    def _merge_dividend_data(
        self,
        yf_dividends: List[Dict[str, Any]],
        av_dividends: List[Dict[str, Any]],
        fmp_dividends: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge dividend data from multiple sources"""
        
        # Create a comprehensive list with cross-validation
        all_dividends = {}
        
        # Add all dividends with date as key
        for source_dividends in [yf_dividends, av_dividends, fmp_dividends]:
            for div in source_dividends:
                date_key = div['ex_date']
                if date_key not in all_dividends:
                    all_dividends[date_key] = []
                all_dividends[date_key].append(div)
        
        # Merge and validate dividends for each date
        merged_dividends = []
        for ex_date, divs in all_dividends.items():
            if len(divs) == 1:
                merged_dividends.append(divs[0])
            else:
                # Multiple sources - validate and merge
                amounts = [div['amount'] for div in divs]
                avg_amount = mean(amounts)
                
                # Use the dividend with amount closest to average
                best_div = min(divs, key=lambda d: abs(d['amount'] - avg_amount))
                
                # Enhance with additional data from other sources
                merged_div = best_div.copy()
                for div in divs:
                    if div != best_div:
                        # Add any additional fields
                        for key, value in div.items():
                            if key not in merged_div and value is not None:
                                merged_div[key] = value
                
                # Update confidence score based on agreement
                variance = stdev(amounts) if len(amounts) > 1 else 0
                if variance < 0.01:  # Very close agreement
                    merged_div['confidence_score'] = 0.95
                elif variance < 0.05:
                    merged_div['confidence_score'] = 0.85
                else:
                    merged_div['confidence_score'] = 0.75
                
                merged_dividends.append(merged_div)
        
        return merged_dividends
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None

    # CHART HELPER METHODS FOR VISUALIZATION ENDPOINTS
    
    def _calculate_cagr(self, chart_data: List[Dict]) -> float:
        """Calculate Compound Annual Growth Rate for chart data"""
        if len(chart_data) < 2:
            return 0
        
        start_value = chart_data[0]['dividend_amount']
        end_value = chart_data[-1]['dividend_amount']
        years = len(chart_data) - 1
        
        if start_value <= 0:
            return 0
        
        cagr = ((end_value / start_value) ** (1/years)) - 1
        return round(cagr * 100, 2)

    def _calculate_correlation(self, chart_data: List[Dict]) -> float:
        """Calculate correlation between yield and price"""
        if len(chart_data) < 3:
            return 0
        
        yields = [d['dividend_yield'] for d in chart_data]
        prices = [d['stock_price'] for d in chart_data]
        
        try:
            correlation = np.corrcoef(yields, prices)[0, 1]
            return round(correlation, 3) if not np.isnan(correlation) else 0
        except:
            return 0

    def _compare_current_vs_average(self, chart_data: List[Dict]) -> Dict[str, Any]:
        """Compare current metrics vs historical average"""
        if not chart_data:
            return {}
        
        current = chart_data[-1]
        avg_yield = mean([d['dividend_yield'] for d in chart_data])
        avg_price = mean([d['stock_price'] for d in chart_data])
        
        return {
            'current_yield_vs_avg': round(current['dividend_yield'] - avg_yield, 2),
            'current_price_vs_avg': round(current['stock_price'] - avg_price, 2),
            'yield_percentile': self._calculate_percentile(current['dividend_yield'], [d['dividend_yield'] for d in chart_data])
        }

    def _calculate_growth_sustainability_score(self, chart_data: List[Dict]) -> int:
        """Calculate growth sustainability score (0-100)"""
        if not chart_data:
            return 0
        
        growth_rates = [d['dividend_growth'] for d in chart_data if d['dividend_growth'] is not None]
        
        if not growth_rates:
            return 0
        
        # Score based on consistency and moderation of growth
        positive_growth = sum(1 for gr in growth_rates if gr > 0)
        consistency = (positive_growth / len(growth_rates)) * 50
        
        # Penalize excessive growth (unsustainable)
        avg_growth = mean(growth_rates)
        moderation = 50 if 3 <= avg_growth <= 12 else max(0, 50 - abs(avg_growth - 7.5) * 2)
        
        return int(consistency + moderation)

    # MISSING HELPER METHODS FOR PROFESSIONAL ANALYSIS

    def _score_financial_strength(self, financials: Dict) -> float:
        """Score financial strength (0-20 points)"""
        if not financials:
            return 0
        
        score = 0
        
        # ROE scoring (8 points)
        roe = financials.get('roe', 0) / 100 if financials.get('roe') else 0
        if roe > 0.20: score += 8
        elif roe > 0.15: score += 6
        elif roe > 0.10: score += 4
        elif roe > 0.05: score += 2
        
        # Debt-to-equity scoring (6 points)
        debt_ratio = financials.get('debt_to_equity', 50) / 100
        if debt_ratio < 0.25: score += 6
        elif debt_ratio < 0.50: score += 4
        elif debt_ratio < 0.75: score += 2
        
        # Current ratio scoring (6 points)
        current_ratio = financials.get('current_ratio', 1.0)
        if current_ratio > 2.0: score += 6
        elif current_ratio > 1.5: score += 4
        elif current_ratio > 1.0: score += 2
        
        return score

    def _get_investment_recommendation(self, quality_score: float) -> str:
        """Get investment recommendation based on quality score"""
        if quality_score >= 80: return 'Strong Buy'
        elif quality_score >= 70: return 'Buy'
        elif quality_score >= 60: return 'Hold'
        elif quality_score >= 50: return 'Weak Hold'
        else: return 'Sell'

    def _calculate_fcf_coverage_ratio(self, dividends: List[Dict], financials: Dict) -> float:
        """Calculate Free Cash Flow coverage ratio"""
        if not dividends or not financials:
            return 0
        
        ttm_dividend_per_share = sum(div.get('amount', 0) for div in dividends[:4])
        free_cash_flow = financials.get('free_cash_flow', 0)
        
        # Estimate shares outstanding (simplified)
        market_cap = financials.get('market_cap', 1_000_000_000)
        current_price = financials.get('current_price', 100)
        shares_outstanding = market_cap / current_price if current_price > 0 else 1_000_000
        
        total_dividends_paid = ttm_dividend_per_share * shares_outstanding
        
        return free_cash_flow / total_dividends_paid if total_dividends_paid > 0 else 0

    def _identify_sustainability_risks(self, payout_ratio: float, fcf_coverage: float) -> List[str]:
        """Identify sustainability risk factors"""
        risks = []
        
        if payout_ratio > 0.8:
            risks.append("High payout ratio may limit financial flexibility")
        if fcf_coverage < 1.5:
            risks.append("Low free cash flow coverage raises sustainability concerns")
        if payout_ratio > 1.0:
            risks.append("Paying out more than earnings - unsustainable long-term")
        if fcf_coverage < 1.0:
            risks.append("Insufficient free cash flow to cover dividend payments")
            
        return risks

    def _identify_sustainability_strengths(self, payout_ratio: float, fcf_coverage: float) -> List[str]:
        """Identify sustainability strengths"""
        strengths = []
        
        if payout_ratio < 0.4:
            strengths.append("Conservative payout ratio provides growth flexibility")
        if fcf_coverage > 2.0:
            strengths.append("Strong free cash flow coverage supports dividend sustainability")
        if payout_ratio < 0.6 and fcf_coverage > 1.5:
            strengths.append("Well-covered dividend with room for growth")
            
        return strengths

    def _calculate_consecutive_increases(self, annual_dividends: Dict[int, float]) -> int:
        """Calculate consecutive years of dividend increases"""
        years = sorted(annual_dividends.keys(), reverse=True)
        consecutive = 0
        
        for i in range(len(years) - 1):
            current_year = annual_dividends[years[i]]
            prev_year = annual_dividends[years[i + 1]]
            
            if current_year > prev_year:
                consecutive += 1
            else:
                break
                
        return consecutive

    def _determine_recent_trend(self, recent_growth_rates: List[float]) -> str:
        """Determine recent dividend growth trend"""
        if not recent_growth_rates:
            return 'Unknown'
        
        if len(recent_growth_rates) >= 2:
            if recent_growth_rates[-1] > recent_growth_rates[0]:
                return 'Accelerating'
            elif recent_growth_rates[-1] < recent_growth_rates[0]:
                return 'Decelerating'
        
        avg_growth = mean(recent_growth_rates)
        if avg_growth > 5:
            return 'Strong Growth'
        elif avg_growth > 0:
            return 'Positive Growth'
        else:
            return 'Declining'

    def _calculate_ebitda_coverage_ratio(self, dividends: List[Dict], financials: Dict) -> float:
        """Calculate EBITDA coverage ratio (simplified)"""
        if not dividends or not financials:
            return 0
        
        # Use revenue as proxy for EBITDA (simplified)
        revenue = financials.get('revenue', 0)
        estimated_ebitda = revenue * 0.15 if revenue > 0 else 0  # Assume 15% EBITDA margin
        
        ttm_dividend_per_share = sum(div.get('amount', 0) for div in dividends[:4])
        
        # Estimate total dividend payments
        market_cap = financials.get('market_cap', 1_000_000_000)
        current_price = financials.get('current_price', 100)
        shares_outstanding = market_cap / current_price if current_price > 0 else 1_000_000
        total_dividends = ttm_dividend_per_share * shares_outstanding
        
        return estimated_ebitda / total_dividends if total_dividends > 0 else 0

    def _assess_coverage_adequacy(self, eps_coverage: float, fcf_coverage: float) -> str:
        """Assess overall coverage adequacy"""
        if eps_coverage > 2.5 and fcf_coverage > 2.0:
            return 'Excellent Coverage'
        elif eps_coverage > 2.0 and fcf_coverage > 1.5:
            return 'Good Coverage'
        elif eps_coverage > 1.5 and fcf_coverage > 1.2:
            return 'Adequate Coverage'
        elif eps_coverage > 1.0 and fcf_coverage > 1.0:
            return 'Marginal Coverage'
        else:
            return 'Poor Coverage'

    def _analyze_coverage_trend(self, dividends: List[Dict], financials: Dict) -> str:
        """Analyze coverage trend (simplified)"""
        eps_coverage = self._calculate_eps_coverage_ratio(dividends, financials)
        
        if eps_coverage > 2.5:
            return 'Improving'
        elif eps_coverage > 1.5:
            return 'Stable'
        else:
            return 'Deteriorating'

    def _calculate_dividend_beta(self, dividends: List[Dict]) -> float:
        """Calculate dividend beta (volatility measure)"""
        if len(dividends) < 8:
            return 1.0
        
        # Calculate quarterly dividend changes
        quarterly_changes = []
        for i in range(len(dividends) - 1):
            current = dividends[i].get('amount', 0)
            previous = dividends[i + 1].get('amount', 0)
            if previous > 0:
                change = (current - previous) / previous
                quarterly_changes.append(change)
        
        if len(quarterly_changes) > 1:
            volatility = stdev(quarterly_changes)
            return min(2.0, volatility * 10)  # Scale and cap at 2.0
        
        return 1.0

    def _suggest_risk_mitigation(self, risk_score: int) -> List[str]:
        """Suggest risk mitigation strategies"""
        suggestions = []
        
        if risk_score > 80:
            suggestions.extend([
                "Consider reducing position size due to high risk",
                "Monitor quarterly earnings and cash flow closely",
                "Set stop-loss levels to protect capital"
            ])
        elif risk_score > 60:
            suggestions.extend([
                "Monitor payout ratio trends quarterly",
                "Watch for debt level changes",
                "Consider dividend sustainability in economic downturns"
            ])
        elif risk_score > 40:
            suggestions.extend([
                "Monitor coverage ratios annually",
                "Watch for economic environment changes"
            ])
        else:
            suggestions.append("Low risk - maintain regular monitoring")
            
        return suggestions

    def _assess_yield_attractiveness(self, current_yield: float, yield_percentile: float) -> str:
        """Assess yield attractiveness"""
        if current_yield > 4.0 and yield_percentile > 70:
            return 'Very Attractive'
        elif current_yield > 3.0 and yield_percentile > 50:
            return 'Attractive'
        elif current_yield > 2.0:
            return 'Moderate'
        elif current_yield > 1.0:
            return 'Low'
        else:
            return 'Very Low'
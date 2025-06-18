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
from fredapi import Fred

from app.core.config import settings
from app.utils.exceptions import DataSourceError, TickerNotFoundError, ValidationError
from app.services.cache_service import CacheService

logger = structlog.get_logger()


class ProfessionalDividendService:
    """
    Professional-grade dividend analysis service with advanced financial calculations
    Used by institutional investors and financial professionals
    """
    
    def __init__(self):
        self.cache_service = CacheService()
        
        # Multi-API configuration for maximum data accuracy
        self.fred = Fred(api_key=settings.FRED_API_KEY) if settings.FRED_API_KEY else None
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.fmp_key = settings.FMP_API_KEY
        
        # Professional benchmarks and constants
        self.RISK_FREE_RATE_PROXY = 'GS10'  # 10-Year Treasury
        self.MARKET_DIVIDEND_YIELD = 'SP500'
        
        # Sector dividend benchmarks (institutional-grade)
        self.sector_benchmarks = {
            'Technology': {'yield_range': [0.5, 2.5], 'payout_target': 25, 'growth_expectation': 8},
            'Utilities': {'yield_range': [3.0, 6.0], 'payout_target': 70, 'growth_expectation': 3},
            'Real Estate': {'yield_range': [2.5, 5.5], 'payout_target': 85, 'growth_expectation': 4},
            'Consumer Staples': {'yield_range': [2.0, 4.0], 'payout_target': 60, 'growth_expectation': 5},
            'Healthcare': {'yield_range': [1.5, 3.5], 'payout_target': 45, 'growth_expectation': 6},
            'Financials': {'yield_range': [2.0, 4.5], 'payout_target': 40, 'growth_expectation': 7},
            'Energy': {'yield_range': [3.0, 7.0], 'payout_target': 35, 'growth_expectation': 2},
            'Industrials': {'yield_range': [1.8, 3.5], 'payout_target': 50, 'growth_expectation': 6},
        }

    async def get_professional_dividend_analysis(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_forecast: bool = False,
        include_peer_comparison: bool = False
    ) -> Dict[str, Any]:
        """
        Institutional-grade dividend analysis with advanced financial metrics
        Returns actionable insights used by professional investors
        """
        
        try:
            # Professional analysis requires minimum 5-year dataset
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=365 * 10)
            
            # Multi-source data aggregation with parallel processing
            data_results = await asyncio.gather(
                self._aggregate_multi_source_dividends(ticker, start_date, end_date),
                self._fetch_comprehensive_financials(ticker),
                self._fetch_market_data(ticker),
                self._fetch_economic_indicators(),
                return_exceptions=True
            )
            
            dividends, financials, market_data, economic_data = [
                result if not isinstance(result, Exception) else {} 
                for result in data_results
            ]
            
            if not dividends:
                raise TickerNotFoundError(f"No dividend data available for {ticker}")
            
            # Professional Dividend Analytics Suite
            dividend_analytics = {
                # Core Quality Assessment (Institutional Standard)
                'dividend_quality_score': self._calculate_institutional_quality_score(dividends, financials),
                
                # Sustainability Analysis (Cash Flow Based)
                'sustainability_metrics': self._analyze_dividend_sustainability(dividends, financials),
                
                # Growth Pattern Analysis (CAGR & Consistency)
                'growth_analytics': self._analyze_dividend_growth_dynamics(dividends),
                
                # Coverage Analysis (Multiple Ratios)
                'coverage_analysis': self._perform_coverage_analysis(dividends, financials),
                
                # Risk Assessment (Multi-factor Model)
                'risk_metrics': self._calculate_comprehensive_risk_metrics(dividends, financials, economic_data),
                
                # Valuation Metrics (Yield Analysis)
                'valuation_analysis': self._perform_dividend_valuation_analysis(dividends, market_data, economic_data),
                
                # Performance vs Benchmarks
                'performance_analytics': self._analyze_dividend_performance_metrics(dividends, market_data)
            }
            
            # Current State Metrics (Non-redundant)
            current_metrics = self._get_current_state_metrics(dividends, market_data, financials)
            
            # Optional Advanced Analytics
            forecast_data = None
            if include_forecast:
                forecast_data = await self._generate_institutional_forecast(dividends, financials, economic_data)
            
            peer_analysis = None
            if include_peer_comparison:
                peer_analysis = await self._perform_sector_peer_analysis(ticker, dividend_analytics, market_data)
            
            return {
                'ticker': ticker.upper(),
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'years_analyzed': round((end_date - start_date).days / 365.25, 1)
                },
                'dividend_analytics': dividend_analytics,
                'current_metrics': current_metrics,
                'forecast': forecast_data,
                'peer_analysis': peer_analysis,
                'data_quality': {
                    'sources_used': ['yahoo_finance', 'alpha_vantage', 'fmp', 'fred'],
                    'reliability_score': self._calculate_data_reliability(dividends, financials),
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("Professional dividend analysis failed", ticker=ticker, error=str(e))
            if isinstance(e, (TickerNotFoundError, ValidationError)):
                raise
            raise DataSourceError(f"Professional dividend analysis failed: {str(e)}")

    def _calculate_institutional_quality_score(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """
        Calculate institutional-grade dividend quality score using Morningstar methodology
        Components: Consistency (25%), Growth (25%), Coverage (25%), Yield Quality (15%), Financial Strength (10%)
        """
        
        if not dividends:
            return {'quality_score': 0, 'grade': 'F', 'investment_recommendation': 'Avoid'}
        
        # Component calculations (professional formulas)
        consistency_score = self._calculate_dividend_consistency_score(dividends)  # 0-25
        growth_score = self._calculate_dividend_growth_score(dividends)           # 0-25  
        coverage_score = self._calculate_coverage_quality_score(dividends, financials)  # 0-25
        yield_score = self._calculate_yield_quality_score(dividends, financials)   # 0-15
        strength_score = self._calculate_financial_strength_score(financials)     # 0-10
        
        total_score = consistency_score + growth_score + coverage_score + yield_score + strength_score
        
        # Professional grade assignment
        if total_score >= 85:
            grade, recommendation = 'A+', 'Strong Buy'
        elif total_score >= 75:
            grade, recommendation = 'A', 'Buy'
        elif total_score >= 65:
            grade, recommendation = 'B+', 'Moderate Buy'
        elif total_score >= 55:
            grade, recommendation = 'B', 'Hold'
        elif total_score >= 45:
            grade, recommendation = 'C+', 'Weak Hold'
        elif total_score >= 35:
            grade, recommendation = 'C', 'Sell'
        else:
            grade, recommendation = 'D/F', 'Strong Sell'
        
        return {
            'quality_score': round(total_score, 1),
            'grade': grade,
            'investment_recommendation': recommendation,
            'component_scores': {
                'consistency': consistency_score,
                'growth': growth_score,
                'coverage': coverage_score,
                'yield_quality': yield_score,
                'financial_strength': strength_score
            },
            'score_interpretation': self._interpret_quality_score(total_score),
            'key_strengths': self._identify_dividend_strengths(dividends, financials),
            'key_concerns': self._identify_dividend_concerns(dividends, financials)
        }

    def _analyze_dividend_sustainability(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """
        Professional sustainability analysis using cash flow and balance sheet metrics
        Key focus: Can the company maintain/grow dividends through economic cycles?
        """
        
        if not dividends or not financials:
            return {'sustainability_rating': 'Insufficient Data', 'confidence': 'Low'}
        
        # Calculate key sustainability ratios
        metrics = {
            'free_cash_flow_coverage': self._calculate_fcf_coverage_ratio(dividends, financials),
            'earnings_coverage': self._calculate_earnings_coverage_ratio(dividends, financials),
            'debt_service_coverage': self._calculate_debt_service_coverage_ratio(financials),
            'interest_coverage': self._calculate_interest_coverage_ratio(financials),
            'working_capital_ratio': self._calculate_working_capital_ratio(financials),
            'earnings_volatility': self._calculate_earnings_volatility_score(financials)
        }
        
        # Sustainability scoring algorithm (institutional methodology)
        sustainability_score = 0
        
        # FCF Coverage (30% weight) - Most important for sustainability
        fcf_coverage = metrics['free_cash_flow_coverage']
        if fcf_coverage >= 2.0:
            sustainability_score += 30
        elif fcf_coverage >= 1.5:
            sustainability_score += 25
        elif fcf_coverage >= 1.2:
            sustainability_score += 20
        elif fcf_coverage >= 1.0:
            sustainability_score += 15
        elif fcf_coverage >= 0.8:
            sustainability_score += 10
        
        # Earnings Coverage (25% weight)
        earnings_coverage = metrics['earnings_coverage']
        if earnings_coverage >= 2.5:
            sustainability_score += 25
        elif earnings_coverage >= 2.0:
            sustainability_score += 20
        elif earnings_coverage >= 1.5:
            sustainability_score += 15
        elif earnings_coverage >= 1.2:
            sustainability_score += 10
        
        # Debt Management (25% weight)
        debt_score = min(metrics['debt_service_coverage'] / 3.0 * 12.5, 12.5)
        interest_score = min(metrics['interest_coverage'] / 5.0 * 12.5, 12.5)
        sustainability_score += debt_score + interest_score
        
        # Earnings Stability (20% weight)
        stability_score = max(0, 20 - (metrics['earnings_volatility'] * 40))
        sustainability_score += stability_score
        
        # Determine sustainability rating
        if sustainability_score >= 80:
            rating = 'Very High'
            confidence = 'High'
        elif sustainability_score >= 65:
            rating = 'High'
            confidence = 'High'
        elif sustainability_score >= 50:
            rating = 'Moderate'
            confidence = 'Medium'
        elif sustainability_score >= 35:
            rating = 'Low'
            confidence = 'Medium'
        else:
            rating = 'Very Low'
            confidence = 'High'
        
        return {
            'sustainability_rating': rating,
            'sustainability_score': round(sustainability_score, 1),
            'confidence_level': confidence,
            'key_metrics': metrics,
            'risk_factors': self._identify_sustainability_risks(metrics),
            'competitive_advantages': self._identify_sustainability_strengths(metrics),
            'sustainability_outlook': self._assess_sustainability_outlook(metrics, dividends)
        }

    def _analyze_dividend_growth_dynamics(self, dividends: List[Dict]) -> Dict[str, Any]:
        """
        Advanced dividend growth analysis with compound annual growth rates and consistency metrics
        """
        
        if len(dividends) < 8:  # Need minimum 2 years of data
            return {'status': 'Insufficient data for growth analysis'}
        
        # Aggregate to annual dividend payments
        annual_dividends = self._calculate_annual_dividend_totals(dividends)
        years = sorted(annual_dividends.keys(), reverse=True)
        
        if len(years) < 3:
            return {'status': 'Insufficient annual data'}
        
        # Calculate Compound Annual Growth Rates (CAGR) for multiple periods
        cagr_analysis = {}
        for period in [3, 5, 10, len(years)]:
            if len(years) >= period:
                start_value = annual_dividends[years[period-1]]
                end_value = annual_dividends[years[0]]
                
                if start_value > 0:
                    cagr = ((end_value / start_value) ** (1/period)) - 1
                    cagr_analysis[f'{period}_year_cagr'] = round(cagr * 100, 2)
        
        # Year-over-year growth analysis
        yoy_growth_rates = []
        for i in range(len(years) - 1):
            current = annual_dividends[years[i]]
            previous = annual_dividends[years[i + 1]]
            if previous > 0:
                growth_rate = (current - previous) / previous
                yoy_growth_rates.append(growth_rate)
        
        # Growth quality metrics
        avg_growth = mean(yoy_growth_rates) if yoy_growth_rates else 0
        growth_volatility = stdev(yoy_growth_rates) if len(yoy_growth_rates) > 1 else 0
        positive_growth_years = sum(1 for rate in yoy_growth_rates if rate > 0)
        growth_consistency = (positive_growth_years / len(yoy_growth_rates)) * 100 if yoy_growth_rates else 0
        
        # Dividend aristocrat/achiever status
        consecutive_increases = self._calculate_consecutive_increases(annual_dividends)
        
        # Growth trend analysis (last 3 years)
        recent_trend = self._analyze_recent_growth_trend(yoy_growth_rates[-3:] if len(yoy_growth_rates) >= 3 else yoy_growth_rates)
        
        return {
            'cagr_analysis': cagr_analysis,
            'growth_statistics': {
                'average_annual_growth': round(avg_growth * 100, 2),
                'growth_volatility': round(growth_volatility * 100, 2),
                'growth_consistency_pct': round(growth_consistency, 1),
                'positive_growth_years': positive_growth_years,
                'total_years_analyzed': len(yoy_growth_rates)
            },
            'dividend_aristocrat_status': {
                'consecutive_increases': consecutive_increases,
                'is_dividend_aristocrat': consecutive_increases >= 25,  # S&P 500 standard
                'is_dividend_achiever': consecutive_increases >= 10,    # Broader market standard
                'is_dividend_challenger': consecutive_increases >= 5,   # Emerging dividend grower
                'aristocrat_progress': f"{consecutive_increases}/25 years"
            },
            'growth_quality_assessment': {
                'trend_direction': recent_trend['direction'],
                'trend_strength': recent_trend['strength'],
                'growth_predictability': self._assess_growth_predictability(yoy_growth_rates),
                'growth_sustainability': self._assess_growth_sustainability(avg_growth, growth_volatility)
            }
        }

    def _perform_coverage_analysis(self, dividends: List[Dict], financials: Dict) -> Dict[str, Any]:
        """
        Professional dividend coverage analysis using multiple financial metrics
        """
        
        if not dividends or not financials:
            return {'status': 'Insufficient data for coverage analysis'}
        
        # Calculate key coverage ratios
        coverage_ratios = {
            'earnings_coverage': self._calculate_earnings_coverage_ratio(dividends, financials),
            'free_cash_flow_coverage': self._calculate_fcf_coverage_ratio(dividends, financials),
            'operating_cash_flow_coverage': self._calculate_ocf_coverage_ratio(dividends, financials),
            'ebitda_coverage': self._calculate_ebitda_coverage_ratio(dividends, financials),
            'book_value_coverage': self._calculate_book_value_coverage_ratio(dividends, financials)
        }
        
        # Calculate payout ratios
        payout_ratios = {
            'earnings_payout_ratio': 1 / coverage_ratios['earnings_coverage'] if coverage_ratios['earnings_coverage'] > 0 else 0,
            'fcf_payout_ratio': 1 / coverage_ratios['free_cash_flow_coverage'] if coverage_ratios['free_cash_flow_coverage'] > 0 else 0,
            'ocf_payout_ratio': 1 / coverage_ratios['operating_cash_flow_coverage'] if coverage_ratios['operating_cash_flow_coverage'] > 0 else 0
        }
        
        # Coverage trend analysis (3-year trend)
        coverage_trend = self._analyze_coverage_trends(dividends, financials)
        
        # Coverage quality assessment
        coverage_grade = self._assess_coverage_quality(coverage_ratios)
        
        # Risk assessment based on coverage
        coverage_risk = self._assess_coverage_risk(coverage_ratios, payout_ratios)
        
        return {
            'coverage_ratios': coverage_ratios,
            'payout_ratios': payout_ratios,
            'coverage_trend': coverage_trend,
            'coverage_grade': coverage_grade,
            'coverage_risk_assessment': coverage_risk,
            'coverage_interpretation': self._interpret_coverage_metrics(coverage_ratios),
            'recommendations': self._generate_coverage_recommendations(coverage_ratios, coverage_trend)
        }

    # Helper methods for calculations
    def _calculate_dividend_consistency_score(self, dividends: List[Dict]) -> float:
        """Calculate consistency score (0-25 points)"""
        if len(dividends) < 4:
            return 0
        
        annual_dividends = self._calculate_annual_dividend_totals(dividends)
        years = sorted(annual_dividends.keys())
        
        if len(years) < 2:
            return 0
        
        # Count years with dividend increases or maintained payments
        consistent_years = 0
        for i in range(1, len(years)):
            if annual_dividends[years[i]] >= annual_dividends[years[i-1]]:
                consistent_years += 1
        
        consistency_ratio = consistent_years / (len(years) - 1) if len(years) > 1 else 0
        return consistency_ratio * 25

    def _calculate_dividend_growth_score(self, dividends: List[Dict]) -> float:
        """Calculate growth quality score (0-25 points)"""
        annual_dividends = self._calculate_annual_dividend_totals(dividends)
        years = sorted(annual_dividends.keys())
        
        if len(years) < 3:
            return 0
        
        # Calculate 5-year CAGR if available, otherwise use available period
        period = min(5, len(years) - 1)
        start_div = annual_dividends[years[0]]
        end_div = annual_dividends[years[period]]
        
        if start_div <= 0:
            return 0
        
        cagr = ((end_div / start_div) ** (1/period)) - 1
        
        # Score based on CAGR (target: 5-15% annual growth)
        if 0.05 <= cagr <= 0.15:
            return 25
        elif 0.03 <= cagr < 0.05 or 0.15 < cagr <= 0.20:
            return 20
        elif 0.01 <= cagr < 0.03 or 0.20 < cagr <= 0.25:
            return 15
        elif 0 <= cagr < 0.01 or cagr > 0.25:
            return 10
        else:
            return 0

    def _calculate_fcf_coverage_ratio(self, dividends: List[Dict], financials: Dict) -> float:
        """Calculate free cash flow dividend coverage ratio"""
        if not dividends or not financials:
            return 0
        
        ttm_dividends = sum(div.get('amount', 0) for div in dividends[:4])
        shares_outstanding = financials.get('shares_outstanding', 0)
        fcf_per_share = financials.get('free_cash_flow', 0) / shares_outstanding if shares_outstanding > 0 else 0
        
        return fcf_per_share / ttm_dividends if ttm_dividends > 0 else 0

    def _calculate_earnings_coverage_ratio(self, dividends: List[Dict], financials: Dict) -> float:
        """Calculate earnings dividend coverage ratio"""
        if not dividends or not financials:
            return 0
        
        ttm_dividends = sum(div.get('amount', 0) for div in dividends[:4])
        eps = financials.get('eps', 0)
        
        return eps / ttm_dividends if ttm_dividends > 0 else 0

    # Additional helper methods would continue...
    async def _aggregate_multi_source_dividends(self, ticker: str, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Aggregate dividend data from all sources with validation"""
        # Implement multi-source aggregation
        return []
    
    async def _fetch_comprehensive_financials(self, ticker: str) -> Dict[str, Any]:
        """Fetch comprehensive financial data from multiple sources"""
        # Implement comprehensive financial data fetching
        return {}
    
    async def _fetch_market_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch current market data"""
        # Implement market data fetching
        return {}
    
    async def _fetch_economic_indicators(self) -> Dict[str, Any]:
        """Fetch relevant economic indicators from FRED"""
        # Implement FRED data fetching
        return {}

    def _calculate_annual_dividend_totals(self, dividends: List[Dict]) -> Dict[int, float]:
        """Calculate total dividends per year"""
        annual_totals = {}
        
        for dividend in dividends:
            ex_date = dividend.get('ex_date')
            amount = dividend.get('amount', 0)
            
            if ex_date and amount:
                year = ex_date.year if hasattr(ex_date, 'year') else ex_date
                annual_totals[year] = annual_totals.get(year, 0) + amount
        
        return annual_totals 
"""
Professional Investment Assistant - Focused on Accuracy and Speed

This module provides a streamlined, accurate investment assistant that prioritizes:
1. Real data over AI complexity
2. Speed over flashy features  
3. Professional-grade analysis
4. Clear, actionable insights
"""

import re
import asyncio
import yfinance as yf
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog
import pandas as pd

logger = structlog.get_logger()

@dataclass
class StockData:
    """Clean, reliable stock data structure"""
    ticker: str
    name: str
    price: float
    dividend_yield: float
    pe_ratio: float
    market_cap: float
    sector: str
    beta: float
    dividend_per_share: float
    payout_ratio: float
    score: float = 0.0

@dataclass
class ScreeningCriteria:
    """Clear screening criteria"""
    min_dividend_yield: Optional[float] = None
    max_dividend_yield: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_pe_ratio: Optional[float] = None
    max_pe_ratio: Optional[float] = None
    sectors: Optional[List[str]] = None
    min_market_cap: Optional[float] = None

@dataclass
class AssistantResponse:
    """Simple, clear response format"""
    success: bool
    data: Optional[Dict[str, Any]]
    message: str
    suggestions: List[str]
    processing_time: float

class ProfessionalInvestmentAssistant:
    """
    Professional Investment Assistant
    
    Focus: Accuracy, Speed, Reliability
    - Real-time data from Yahoo Finance (proven reliable)
    - Fast responses (< 1 second for screening)
    - Clear parameter extraction  
    - Professional-grade analysis
    """
    
    def __init__(self):
        # Core dividend-paying stocks universe (validated tickers)
        self.dividend_universe = [
            # Dividend Aristocrats & High-Quality Dividend Stocks
            'AAPL', 'MSFT', 'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'HD', 'VZ', 'T',
            'CVX', 'XOM', 'JPM', 'BAC', 'ABBV', 'PFE', 'MRK', 'MMM', 'CAT', 'IBM',
            'TXN', 'AVGO', 'QCOM', 'INTC', 'CSCO', 'UNH', 'LLY', 'TMO', 'COST',
            'NEE', 'SO', 'DUK', 'AEP', 'D', 'EXC', 'SRE', 'PEG', 'ES', 'FE',
            # REITs
            'VNQ', 'O', 'AMT', 'PLD', 'EXR', 'PSA', 'DLR', 'EQIX', 'CCI', 'SPG',
            # ETFs
            'VYM', 'SCHD', 'DVY', 'SPHD', 'JEPI', 'FDVV', 'VIG', 'DGRO', 'HDV'
        ]
        
        # Cache for performance
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def process_query(self, query: str) -> AssistantResponse:
        """Process investment query with focus on accuracy and speed"""
        start_time = datetime.now()
        
        try:
            # Extract intent and criteria
            intent, criteria = self._parse_query(query)
            
            if intent == "screen":
                result = await self._screen_stocks(criteria)
            elif intent == "analyze":
                tickers = self._extract_tickers(query)
                if tickers:
                    result = await self._analyze_stocks(tickers)
                else:
                    result = self._create_error_response("Please specify stock tickers to analyze (e.g., AAPL, MSFT)")
            else:
                result = self._create_fallback_response(query)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error("Query processing failed", error=str(e))
            processing_time = (datetime.now() - start_time).total_seconds()
            return AssistantResponse(
                success=False,
                data=None,
                message=f"Error processing query: {str(e)}",
                suggestions=["Try a simpler query", "Check your internet connection"],
                processing_time=processing_time
            )
    
    def _parse_query(self, query: str) -> Tuple[str, ScreeningCriteria]:
        """Extract intent and criteria from query"""
        query_lower = query.lower().strip()
        
        # Determine intent
        if any(word in query_lower for word in ['find', 'search', 'screen', 'filter', 'show', 'get']):
            intent = "screen"
        elif any(word in query_lower for word in ['analyze', 'analysis', 'evaluate', 'assess']):
            intent = "analyze"
        else:
            intent = "screen"  # Default
        
        # Extract criteria
        criteria = ScreeningCriteria()
        
        # Dividend yield patterns (improved)
        yield_patterns = [
            (r'yield.*?(?:above|over|at least)\s*([\d.]+)%?', 'min'),
            (r'yield.*?(?:below|under|less than)\s*([\d.]+)%?', 'max'),
            (r'(?:above|over|at least)\s*([\d.]+)%?\s*yield', 'min'),
            (r'(?:below|under|less than)\s*([\d.]+)%?\s*yield', 'max'),
            (r'dividend.*?(?:above|over)\s*([\d.]+)%?', 'min'),
            (r'dividend.*?(?:below|under|less than)\s*([\d.]+)%?', 'max'),
        ]
        
        for pattern, yield_type in yield_patterns:
            match = re.search(pattern, query_lower)
            if match:
                yield_val = float(match.group(1))
                if yield_val > 1:  # Convert percentage to decimal
                    yield_val = yield_val / 100
                
                if yield_type == 'min':
                    criteria.min_dividend_yield = yield_val
                else:
                    criteria.max_dividend_yield = yield_val
                break
        
        # Price patterns
        price_patterns = [
            (r'price.*?(?:under|below|less than)\s*\$?([\d,]+)', 'max'),
            (r'(?:under|below|less than)\s*\$?([\d,]+)', 'max'),
            (r'price.*?(?:above|over)\s*\$?([\d,]+)', 'min'),
            (r'(?:above|over)\s*\$?([\d,]+)', 'min'),
        ]
        
        for pattern, price_type in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                price = float(match.group(1).replace(',', ''))
                if price_type == 'max':
                    criteria.max_price = price
                else:
                    criteria.min_price = price
                break
        
        # P/E ratio patterns
        pe_patterns = [
            (r'pe.*?(?:under|below|less than)\s*([\d.]+)', 'max'),
            (r'p/e.*?(?:under|below|less than)\s*([\d.]+)', 'max'),
            (r'(?:under|below|less than)\s*([\d.]+)\s*pe', 'max'),
        ]
        
        for pattern, pe_type in pe_patterns:
            match = re.search(pattern, query_lower)
            if match:
                pe_val = float(match.group(1))
                if pe_type == 'max':
                    criteria.max_pe_ratio = pe_val
                else:
                    criteria.min_pe_ratio = pe_val
                break
        
        # Sector detection
        sector_map = {
            'tech': 'Technology',
            'healthcare': 'Healthcare', 
            'finance': 'Financial Services',
            'energy': 'Energy',
            'utility': 'Utilities',
            'consumer': 'Consumer',
            'industrial': 'Industrials',
            'reit': 'Real Estate'
        }
        
        for keyword, sector in sector_map.items():
            if keyword in query_lower:
                criteria.sectors = [sector]
                break
        
        return intent, criteria
    
    async def _screen_stocks(self, criteria: ScreeningCriteria) -> AssistantResponse:
        """Fast, accurate stock screening"""
        try:
            # Get real stock data efficiently
            stock_data = await self._fetch_stock_data_batch(self.dividend_universe)
            
            # Apply filters
            filtered_stocks = []
            for stock in stock_data:
                if self._passes_criteria(stock, criteria):
                    filtered_stocks.append(stock)
            
            # Sort by score (dividend yield weighted by quality)
            filtered_stocks.sort(key=lambda x: x.score, reverse=True)
            
            if not filtered_stocks:
                return AssistantResponse(
                    success=False,
                    data=None,
                    message="No stocks found matching your criteria.",
                    suggestions=[
                        "Try broader criteria (lower yield requirements)",
                        "Consider different sectors", 
                        "Expand price range"
                    ],
                    processing_time=0
                )
            
            # Format results
            results = []
            for stock in filtered_stocks[:15]:  # Limit to top 15
                results.append({
                    'ticker': stock.ticker,
                    'company_name': stock.name,
                    'current_price': round(stock.price, 2),
                    'dividend_yield': round(stock.dividend_yield * 100, 2) if stock.dividend_yield < 1 else round(stock.dividend_yield, 2),  # Handle both decimal and percentage formats
                    'pe_ratio': round(stock.pe_ratio, 1) if stock.pe_ratio > 0 else 'N/A',
                    'market_cap': stock.market_cap,
                    'sector': stock.sector,
                    'annual_dividend': round(stock.dividend_per_share, 2),
                    'payout_ratio': round(stock.payout_ratio, 1) if stock.payout_ratio > 0 else 'N/A',
                    'quality_score': round(stock.score, 2)
                })
            
            return AssistantResponse(
                success=True,
                data={
                    'screening_results': results,
                    'total_found': len(filtered_stocks),
                    'criteria_used': self._format_criteria(criteria)
                },
                message=f"Found {len(filtered_stocks)} dividend stocks matching your criteria.",
                suggestions=[
                    "Review dividend sustainability metrics",
                    "Consider diversification across sectors",
                    "Analyze individual stock fundamentals"
                ],
                processing_time=0
            )
            
        except Exception as e:
            logger.error("Stock screening failed", error=str(e))
            return self._create_error_response(f"Screening failed: {str(e)}")
    
    async def _fetch_stock_data_batch(self, tickers: List[str]) -> List[StockData]:
        """Efficiently fetch real stock data using yfinance"""
        cache_key = f"batch_data_{hash(tuple(tickers))}"
        
        # Check cache
        if cache_key in self._cache:
            cache_time, data = self._cache[cache_key]
            if (datetime.now() - cache_time).seconds < self._cache_ttl:
                return data
        
        stock_data = []
        
        # Fetch in batches for speed
        batch_size = 10
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            try:
                # Use yfinance for reliable, fast data
                tickers_str = ' '.join(batch)
                data = yf.download(tickers_str, period='1d', interval='1d', group_by='ticker', 
                                 auto_adjust=True, prepost=True, threads=True, progress=False)
                
                for ticker in batch:
                    try:
                        stock = yf.Ticker(ticker)
                        info = stock.info
                        
                        # Extract key metrics with fallbacks
                        price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
                        dividend_yield = info.get('dividendYield', 0) or 0
                        pe_ratio = info.get('trailingPE', 0) or info.get('forwardPE', 0) or 0
                        market_cap = info.get('marketCap', 0) or 0
                        sector = info.get('sector', 'Unknown')
                        beta = info.get('beta', 1.0) or 1.0
                        dividend_per_share = info.get('dividendRate', 0) or 0
                        payout_ratio = info.get('payoutRatio', 0) or 0
                        
                        # Calculate quality score
                        score = self._calculate_quality_score(dividend_yield, pe_ratio, payout_ratio, market_cap)
                        
                        stock_data.append(StockData(
                            ticker=ticker,
                            name=info.get('longName', ticker),
                            price=price,
                            dividend_yield=dividend_yield,
                            pe_ratio=pe_ratio,
                            market_cap=market_cap,
                            sector=sector,
                            beta=beta,
                            dividend_per_share=dividend_per_share,
                            payout_ratio=payout_ratio,
                            score=score
                        ))
                        
                    except Exception as e:
                        logger.warning(f"Failed to fetch {ticker}: {e}")
                        continue
            
            except Exception as e:
                logger.warning(f"Batch fetch failed for {batch}: {e}")
                continue
        
        # Cache results
        self._cache[cache_key] = (datetime.now(), stock_data)
        return stock_data
    
    def _passes_criteria(self, stock: StockData, criteria: ScreeningCriteria) -> bool:
        """Check if stock passes screening criteria"""
        if criteria.min_dividend_yield and stock.dividend_yield < criteria.min_dividend_yield:
            return False
        if criteria.max_dividend_yield and stock.dividend_yield > criteria.max_dividend_yield:
            return False
        if criteria.min_price and stock.price < criteria.min_price:
            return False
        if criteria.max_price and stock.price > criteria.max_price:
            return False
        if criteria.min_pe_ratio and stock.pe_ratio > 0 and stock.pe_ratio < criteria.min_pe_ratio:
            return False
        if criteria.max_pe_ratio and stock.pe_ratio > 0 and stock.pe_ratio > criteria.max_pe_ratio:
            return False
        if criteria.sectors and stock.sector not in criteria.sectors:
            return False
        if criteria.min_market_cap and stock.market_cap < criteria.min_market_cap:
            return False
        
        return True
    
    def _calculate_quality_score(self, dividend_yield: float, pe_ratio: float, 
                               payout_ratio: float, market_cap: float) -> float:
        """Calculate stock quality score for ranking"""
        score = 0.0
        
        # Dividend yield component (0-40 points)
        if dividend_yield > 0.06:  # 6%+
            score += 40
        elif dividend_yield > 0.04:  # 4-6%
            score += 30
        elif dividend_yield > 0.02:  # 2-4%
            score += 20
        elif dividend_yield > 0:
            score += 10
        
        # P/E ratio component (0-25 points) - prefer reasonable valuations
        if 10 <= pe_ratio <= 20:
            score += 25
        elif 8 <= pe_ratio <= 25:
            score += 20
        elif 5 <= pe_ratio <= 30:
            score += 15
        elif pe_ratio > 0:
            score += 10
        
        # Payout ratio component (0-20 points) - prefer sustainable payouts
        if 0.3 <= payout_ratio <= 0.7:  # 30-70% payout
            score += 20
        elif 0.2 <= payout_ratio <= 0.8:
            score += 15
        elif payout_ratio > 0:
            score += 10
        
        # Market cap component (0-15 points) - prefer larger, stable companies
        if market_cap > 50_000_000_000:  # $50B+
            score += 15
        elif market_cap > 10_000_000_000:  # $10B+
            score += 12
        elif market_cap > 2_000_000_000:  # $2B+
            score += 8
        elif market_cap > 0:
            score += 5
        
        return score
    
    def _extract_tickers(self, query: str) -> List[str]:
        """Extract valid stock tickers from query"""
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        potential_tickers = re.findall(ticker_pattern, query.upper())
        
        # Validate against our universe
        valid_tickers = [t for t in potential_tickers if t in self.dividend_universe]
        return valid_tickers[:10]  # Limit to 10
    
    async def _analyze_stocks(self, tickers: List[str]) -> AssistantResponse:
        """Analyze specific stocks"""
        try:
            stock_data = await self._fetch_stock_data_batch(tickers)
            
            analysis_results = []
            for stock in stock_data:
                analysis = {
                    'ticker': stock.ticker,
                    'name': stock.name,
                    'current_price': round(stock.price, 2),
                    'dividend_yield': round(stock.dividend_yield * 100, 2),
                    'pe_ratio': round(stock.pe_ratio, 1) if stock.pe_ratio > 0 else 'N/A',
                    'annual_dividend': round(stock.dividend_per_share, 2),
                    'payout_ratio': round(stock.payout_ratio * 100, 1) if stock.payout_ratio > 0 else 'N/A',
                    'market_cap': f"${stock.market_cap / 1_000_000_000:.1f}B" if stock.market_cap > 0 else 'N/A',
                    'sector': stock.sector,
                    'beta': round(stock.beta, 2),
                    'quality_score': round(stock.score, 1),
                    'assessment': self._get_assessment(stock)
                }
                analysis_results.append(analysis)
            
            return AssistantResponse(
                success=True,
                data={'analysis_results': analysis_results},
                message=f"Analysis complete for {len(analysis_results)} stocks.",
                suggestions=[
                    "Compare dividend sustainability metrics",
                    "Consider portfolio allocation weights",
                    "Review sector diversification"
                ],
                processing_time=0
            )
            
        except Exception as e:
            return self._create_error_response(f"Analysis failed: {str(e)}")
    
    def _get_assessment(self, stock: StockData) -> str:
        """Get simple assessment of stock quality"""
        if stock.score >= 70:
            return "Excellent dividend quality"
        elif stock.score >= 50:
            return "Good dividend potential"
        elif stock.score >= 30:
            return "Moderate dividend quality"
        else:
            return "Limited dividend appeal"
    
    def _format_criteria(self, criteria: ScreeningCriteria) -> Dict[str, Any]:
        """Format criteria for display"""
        formatted = {}
        if criteria.min_dividend_yield:
            formatted['min_dividend_yield'] = f"{criteria.min_dividend_yield * 100:.1f}%"
        if criteria.max_dividend_yield:
            formatted['max_dividend_yield'] = f"{criteria.max_dividend_yield * 100:.1f}%"
        if criteria.min_price:
            formatted['min_price'] = f"${criteria.min_price:.2f}"
        if criteria.max_price:
            formatted['max_price'] = f"${criteria.max_price:.2f}"
        if criteria.max_pe_ratio:
            formatted['max_pe_ratio'] = criteria.max_pe_ratio
        if criteria.sectors:
            formatted['sectors'] = criteria.sectors
        return formatted
    
    def _create_error_response(self, message: str) -> AssistantResponse:
        """Create error response"""
        return AssistantResponse(
            success=False,
            data=None,
            message=message,
            suggestions=[
                "Try simpler criteria",
                "Check your query format",
                "Verify stock tickers are valid"
            ],
            processing_time=0
        )
    
    def _create_fallback_response(self, query: str) -> AssistantResponse:
        """Create fallback response with helpful suggestions"""
        return AssistantResponse(
            success=True,
            data=None,
            message="I can help you screen dividend stocks or analyze specific stocks.",
            suggestions=[
                "Try: 'Find dividend stocks with yield above 4%'",
                "Try: 'Screen stocks with P/E below 15'", 
                "Try: 'Analyze AAPL MSFT JNJ'",
                "Try: 'Show me utility stocks under $100'"
            ],
            processing_time=0
        ) 
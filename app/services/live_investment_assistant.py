"""
Live Investment Assistant - Real-Time Market Data

This assistant fetches live market data for accurate, up-to-date results.
Solves the issue of outdated pre-cached data causing "incorrect results."
"""

import re
import asyncio
import yfinance as yf
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog
import time
from concurrent.futures import ThreadPoolExecutor
import requests

logger = structlog.get_logger()

@dataclass
class LiveStockData:
    """Live stock data structure"""
    ticker: str
    name: str
    price: float
    dividend_yield: float
    pe_ratio: float
    market_cap: float
    sector: str
    annual_dividend: float
    payout_ratio: float
    last_updated: datetime

@dataclass
class LiveResponse:
    """Live response format"""
    success: bool
    data: Optional[Dict[str, Any]]
    message: str
    suggestions: List[str]
    processing_time: float
    data_freshness: str

class LiveInvestmentAssistant:
    """
    Live Investment Assistant with Real-Time Data
    
    Fetches current market data for accurate results
    """
    
    def __init__(self):
        # Curated list of dividend-focused stocks for faster processing
        self.dividend_universe = [
            # High-quality dividend stocks
            'AAPL', 'MSFT', 'JNJ', 'PG', 'KO', 'PEP', 'WMT', 'HD', 'VZ', 'T',
            'CVX', 'XOM', 'JPM', 'BAC', 'ABBV', 'PFE', 'MRK', 'MMM', 'CAT', 'IBM',
            'TXN', 'AVGO', 'QCOM', 'INTC', 'CSCO', 'UNH', 'LLY', 'TMO', 'COST',
            # Utilities
            'NEE', 'SO', 'DUK', 'AEP', 'D', 'EXC', 'SRE', 'PEG', 'ES', 'FE',
            # REITs
            'O', 'AMT', 'PLD', 'EXR', 'PSA', 'DLR', 'EQIX', 'CCI', 'SPG',
            # ETFs
            'VYM', 'SCHD', 'DVY', 'SPHD', 'JEPI', 'FDVV', 'VIG', 'DGRO', 'HDV'
        ]
        
        # Cache for recent data (5 minutes TTL)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def _get_cached_stock_data(self, ticker: str) -> Optional[LiveStockData]:
        """Get cached stock data if still fresh"""
        if ticker in self.cache:
            data, timestamp = self.cache[ticker]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _cache_stock_data(self, ticker: str, data: LiveStockData):
        """Cache stock data with timestamp"""
        self.cache[ticker] = (data, time.time())
    
    def _fetch_live_stock_data(self, ticker: str) -> Optional[LiveStockData]:
        """Fetch live stock data from Yahoo Finance"""
        try:
            # Check cache first
            cached_data = self._get_cached_stock_data(ticker)
            if cached_data:
                return cached_data
            
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="5d")
            
            if hist.empty:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            
            # Get dividend info
            dividends = stock.dividends
            if not dividends.empty and len(dividends) >= 4:
                # Sum of last 4 quarters for annual dividend
                annual_dividend = float(dividends.tail(4).sum())
            else:
                annual_dividend = float(info.get('dividendRate', 0))
            
            # Calculate dividend yield
            dividend_yield = (annual_dividend / current_price * 100) if current_price > 0 else 0
            
            # Extract other data
            pe_ratio = info.get('trailingPE', 0) or 0
            market_cap = info.get('marketCap', 0) or 0
            sector = info.get('sector', 'Unknown')
            company_name = info.get('longName', ticker)
            
            # Calculate payout ratio
            earnings_per_share = info.get('trailingEps', 0) or 0
            payout_ratio = (annual_dividend / earnings_per_share * 100) if earnings_per_share > 0 else 0
            
            live_data = LiveStockData(
                ticker=ticker,
                name=company_name,
                price=current_price,
                dividend_yield=dividend_yield,
                pe_ratio=pe_ratio,
                market_cap=market_cap,
                sector=sector,
                annual_dividend=annual_dividend,
                payout_ratio=payout_ratio,
                last_updated=datetime.utcnow()
            )
            
            # Cache the data
            self._cache_stock_data(ticker, live_data)
            
            return live_data
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}", error=str(e))
            return None
    
    def _fetch_multiple_stocks(self, tickers: List[str]) -> List[LiveStockData]:
        """Fetch multiple stocks in parallel"""
        future_to_ticker = {
            self.executor.submit(self._fetch_live_stock_data, ticker): ticker 
            for ticker in tickers
        }
        
        results = []
        for future in future_to_ticker:
            try:
                data = future.result(timeout=30)  # 30 second timeout per stock
                if data:
                    results.append(data)
            except Exception as e:
                ticker = future_to_ticker[future]
                logger.error(f"Timeout/error fetching {ticker}", error=str(e))
        
        return results
    
    async def process_query(self, query: str) -> LiveResponse:
        """Process query with live market data"""
        start_time = time.time()
        
        try:
            intent, criteria = self._parse_query_fast(query)
            
            if intent == "screen":
                result = await self._screen_stocks_live(criteria)
            elif intent == "analyze":
                tickers = self._extract_tickers(query)
                if tickers:
                    result = await self._analyze_stocks_live(tickers)
                else:
                    result = LiveResponse(
                        False, None, "Please specify stock tickers (e.g., AAPL, MSFT)", 
                        ["Try: 'Analyze AAPL MSFT'", "Use valid ticker symbols"], 
                        0.0, "No data required"
                    )
            elif intent == "recommend":
                result = await self._provide_investment_guidance(criteria, query)
            else:
                result = LiveResponse(
                    True, None, "I can screen dividend stocks, analyze specific stocks, or provide investment guidance.",
                    ["Try: 'Find stocks with yield above 4%'", "Try: 'Analyze AAPL MSFT'", "Try: 'I have $1000 and want income'"], 
                    0.0, "No data required"
                )
            
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error("Live query processing failed", error=str(e))
            processing_time = time.time() - start_time
            return LiveResponse(
                False, None, f"Query failed: {str(e)}", 
                ["Try a simpler query", "Check ticker symbols"], 
                processing_time, "Error occurred"
            )
    
    def _parse_query_fast(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Fast parameter extraction"""
        query_lower = query.lower().strip()
        criteria = {}
        
        # Determine intent - look for investment guidance patterns first
        if any(phrase in query_lower for phrase in ['have $', 'have money', 'want to earn', 'want $', 'need income', 'monthly income', 'want monthly', 'realistic income', 'income from', 'what income', 'how much income']):
            intent = "recommend"
            
            # Determine if this is an exploratory query (what's realistic) vs goal-oriented (want specific amount)
            is_exploratory = any(phrase in query_lower for phrase in ['realistic income', 'what income', 'how much income', 'income from', 'what\'s realistic', 'realistic expectation'])
            criteria['query_type'] = 'exploratory' if is_exploratory else 'goal_oriented'
            
            # Extract investment amount - more flexible patterns
            investment_patterns = [
                r'have\s*\$?\s*([\d,]+)',  # "have $10000" or "have 10000"
                r'invest\s*\$?\s*([\d,]+)', # "invest $10000"
                r'with\s*\$?\s*([\d,]+)',   # "with $10000"
                r'\$\s*([\d,]+)\s*(?:to|and)',  # "$10000 to" or "$10000 and"
                r'from\s*\$?\s*([\d,]+)',   # "from $3000 investment"
                r'\$\s*([\d,]+)\s*investment'  # "$3000 investment"
            ]
            
            for pattern in investment_patterns:
                investment_match = re.search(pattern, query_lower)
                if investment_match:
                    criteria['initial_investment'] = float(investment_match.group(1).replace(',', ''))
                    break
            
            # Extract target income - more flexible patterns  
            income_patterns = [
                r'want\s*\$?\s*([\d,]+)\s*(?:monthly|per month|/month|month)',  # "want $100 monthly"
                r'earn\s*\$?\s*([\d,]+)\s*(?:monthly|per month|/month|month)',  # "earn $100 monthly"
                r'need\s*\$?\s*([\d,]+)\s*(?:monthly|per month|/month|month)',  # "need $100 monthly"
                r'\$\s*([\d,]+)\s*(?:monthly|per month|/month|month)',          # "$100 monthly"
                r'want\s*to\s*earn\s*\$?\s*([\d,]+)',                           # "want to earn $100"
                r'want\s*to\s*make\s*\$?\s*([\d,]+)'                            # "want to make $100"
            ]
            
            for pattern in income_patterns:
                income_match = re.search(pattern, query_lower)
                if income_match:
                    target_amount = float(income_match.group(1).replace(',', ''))
                    # Check if it's explicitly monthly or assume monthly if amount is reasonable
                    if 'monthly' in query_lower or 'month' in query_lower or target_amount < 2000:
                        criteria['target_annual_income'] = target_amount * 12
                        criteria['target_monthly_income'] = target_amount
                    else:
                        criteria['target_annual_income'] = target_amount
                        criteria['target_monthly_income'] = target_amount / 12
                    break
            
            # For exploratory queries like "realistic income from $3000", DON'T set a default target
            # For goal-oriented queries, keep the existing logic
            if 'initial_investment' in criteria and 'target_annual_income' not in criteria and criteria.get('query_type') == 'goal_oriented':
                # Set default target based on conservative 4% annual return
                default_annual = criteria['initial_investment'] * 0.04
                criteria['target_annual_income'] = default_annual
                criteria['target_monthly_income'] = default_annual / 12
            
        elif any(word in query_lower for word in ['analyze', 'analysis', 'evaluate', 'assess']):
            intent = "analyze"
        else:
            intent = "screen"
        
        # Extract dividend yield criteria
        yield_above_match = re.search(r'yield.*?(?:above|over|at least)\s*([\d.]+)%?', query_lower)
        if yield_above_match:
            criteria['min_dividend_yield'] = float(yield_above_match.group(1))
        
        yield_below_match = re.search(r'yield.*?(?:below|under|less than)\s*([\d.]+)%?', query_lower)
        if yield_below_match:
            criteria['max_dividend_yield'] = float(yield_below_match.group(1))
        
        div_yield_less_match = re.search(r'dividend yield.*?(?:less than|below|under)\s*([\d.]+)%?', query_lower)
        if div_yield_less_match:
            criteria['max_dividend_yield'] = float(div_yield_less_match.group(1))
        
        # Price criteria
        price_under_match = re.search(r'(?:price.*?)?(?:under|below|less than)\s*\$?([\d,]+)', query_lower)
        if price_under_match and 'yield' not in query_lower[:price_under_match.start()]:
            criteria['max_price'] = float(price_under_match.group(1).replace(',', ''))
        
        price_above_match = re.search(r'(?:price.*?)?(?:above|over)\s*\$?([\d,]+)', query_lower)
        if price_above_match and 'yield' not in query_lower[:price_above_match.start()]:
            criteria['min_price'] = float(price_above_match.group(1).replace(',', ''))
        
        # P/E ratio
        pe_match = re.search(r'pe.*?(?:below|under|less than)\s*([\d.]+)', query_lower)
        if pe_match:
            criteria['max_pe_ratio'] = float(pe_match.group(1))
        
        # Sector filtering
        sector_mappings = {
            'tech': 'Technology',
            'technology': 'Technology',
            'healthcare': 'Healthcare', 
            'health': 'Healthcare',
            'utility': 'Utilities',
            'utilities': 'Utilities',
            'energy': 'Energy',
            'finance': 'Financial Services',
            'financial': 'Financial Services',
            'reit': 'Real Estate',
            'real estate': 'Real Estate',
            'consumer': 'Consumer Defensive',
            'defensive': 'Consumer Defensive'
        }
        
        for keyword, sector in sector_mappings.items():
            if keyword in query_lower:
                criteria['sector'] = sector
                break
        
        return intent, criteria
    
    async def _screen_stocks_live(self, criteria: Dict[str, Any]) -> LiveResponse:
        """Screen stocks using live market data"""
        # Fetch live data for all stocks in universe
        logger.info("Fetching live market data for screening...")
        live_stocks = self._fetch_multiple_stocks(self.dividend_universe)
        
        if not live_stocks:
            return LiveResponse(
                False, None, "Unable to fetch market data at this time.",
                ["Try again in a few moments", "Check your internet connection"],
                0, "Data fetch failed"
            )
        
        # Apply filters
        filtered_stocks = []
        for stock in live_stocks:
            passes = True
            
            if 'min_dividend_yield' in criteria:
                if stock.dividend_yield < criteria['min_dividend_yield']:
                    passes = False
            
            if 'max_dividend_yield' in criteria:
                if stock.dividend_yield > criteria['max_dividend_yield']:
                    passes = False
            
            if 'min_price' in criteria:
                if stock.price < criteria['min_price']:
                    passes = False
            
            if 'max_price' in criteria:
                if stock.price > criteria['max_price']:
                    passes = False
            
            if 'max_pe_ratio' in criteria:
                if stock.pe_ratio > 0 and stock.pe_ratio > criteria['max_pe_ratio']:
                    passes = False
            
            if 'sector' in criteria:
                if stock.sector != criteria['sector']:
                    passes = False
            
            if passes:
                filtered_stocks.append(stock)
        
        # Sort by dividend yield descending
        filtered_stocks.sort(key=lambda x: x.dividend_yield, reverse=True)
        
        if not filtered_stocks:
            return LiveResponse(
                False, None, "No stocks found matching your criteria with current market data.",
                [
                    "Try broader criteria (lower yield requirements)",
                    "Consider different sectors",
                    "Expand price range"
                ],
                0, f"Live data from {len(live_stocks)} stocks"
            )
        
        # Format results with enhanced analysis
        results = []
        analysis_results = {}
        
        for stock in filtered_stocks[:15]:
            # Quality assessment based on current data
            assessment = "Limited dividend appeal"
            quality_score = 3.0
            
            if stock.dividend_yield > 6.0:
                assessment = "Excellent high-yield dividend"
                quality_score = 8.5
            elif stock.dividend_yield > 4.0:
                assessment = "Strong dividend quality"
                quality_score = 7.5
            elif stock.dividend_yield > 3.0:
                assessment = "Good dividend potential"
                quality_score = 6.5
            elif stock.dividend_yield > 2.0:
                assessment = "Moderate dividend quality"
                quality_score = 5.5
            else:
                assessment = "Limited dividend appeal"
                quality_score = 3.5
            
            # Generate strengths and risks based on actual data
            strengths = []
            risks = []
            
            # Dividend yield analysis
            if stock.dividend_yield > 5.0:
                strengths.append(f"High dividend yield of {stock.dividend_yield:.2f}%")
            elif stock.dividend_yield > 3.0:
                strengths.append(f"Solid dividend yield of {stock.dividend_yield:.2f}%")
            elif stock.dividend_yield < 2.0:
                risks.append(f"Low dividend yield of {stock.dividend_yield:.2f}%")
            
            # Payout ratio analysis
            if stock.payout_ratio > 0:
                if stock.payout_ratio < 60:
                    strengths.append(f"Conservative payout ratio of {stock.payout_ratio:.1f}%")
                elif stock.payout_ratio > 80:
                    risks.append(f"High payout ratio of {stock.payout_ratio:.1f}% may be unsustainable")
            
            # P/E ratio analysis
            if stock.pe_ratio > 0:
                if stock.pe_ratio < 15:
                    strengths.append(f"Attractive P/E ratio of {stock.pe_ratio:.1f}")
                elif stock.pe_ratio > 30:
                    risks.append(f"High P/E ratio of {stock.pe_ratio:.1f} indicates expensive valuation")
            
            # Market cap and stability
            if stock.market_cap > 100_000_000_000:  # $100B+
                strengths.append("Large-cap stability and established market position")
            elif stock.market_cap < 10_000_000_000:  # <$10B
                risks.append("Smaller market cap may indicate higher volatility")
            
            # Sector-specific insights
            if stock.sector == 'Utilities':
                strengths.append("Utilities sector provides defensive characteristics")
            elif stock.sector == 'Technology':
                risks.append("Technology sector may have lower dividend focus")
            elif stock.sector == 'Real Estate':
                strengths.append("REIT structure provides consistent income distribution")
            
            # Format for screening results table
            results.append({
                'ticker': stock.ticker,
                'company_name': stock.name,
                'current_price': round(stock.price, 2),
                'dividend_yield': round(stock.dividend_yield, 2),
                'pe_ratio': round(stock.pe_ratio, 1) if stock.pe_ratio > 0 else 'N/A',
                'market_cap': stock.market_cap,
                'sector': stock.sector,
                'annual_dividend': round(stock.annual_dividend, 2),
                'payout_ratio': round(stock.payout_ratio, 1) if stock.payout_ratio > 0 else 'N/A',
                'last_updated': stock.last_updated.isoformat()
            })
            
            # Format for detailed analysis
            analysis_results[stock.ticker] = {
                'ticker': stock.ticker,
                'name': stock.name,
                'current_price': round(stock.price, 2),
                'dividend_yield': round(stock.dividend_yield, 2),
                'pe_ratio': round(stock.pe_ratio, 1) if stock.pe_ratio > 0 else 'N/A',
                'annual_dividend': round(stock.annual_dividend, 2),
                'payout_ratio': round(stock.payout_ratio, 1) if stock.payout_ratio > 0 else 'N/A',
                'market_cap': f"${stock.market_cap / 1_000_000_000:.1f}B" if stock.market_cap > 0 else 'N/A',
                'sector': stock.sector,
                'assessment': assessment,
                'quality_score': quality_score,
                'strengths': strengths,
                'risks': risks,
                'last_updated': stock.last_updated.isoformat()
            }
        
        # Format criteria for display
        criteria_display = {}
        if 'min_dividend_yield' in criteria:
            criteria_display['min_dividend_yield'] = f"{criteria['min_dividend_yield']}%"
        if 'max_dividend_yield' in criteria:
            criteria_display['max_dividend_yield'] = f"{criteria['max_dividend_yield']}%"
        if 'min_price' in criteria:
            criteria_display['min_price'] = f"${criteria['min_price']}"
        if 'max_price' in criteria:
            criteria_display['max_price'] = f"${criteria['max_price']}"
        if 'max_pe_ratio' in criteria:
            criteria_display['max_pe_ratio'] = criteria['max_pe_ratio']
        if 'sector' in criteria:
            criteria_display['sector'] = criteria['sector']
        
        oldest_data = min(stock.last_updated for stock in filtered_stocks)
        data_age = datetime.utcnow() - oldest_data
        data_freshness = f"Live data (max {data_age.seconds//60} min old)"
        
        # Enhanced recommendations based on screening results
        enhanced_suggestions = [
            "All data is current market data",
            "Review dividend sustainability metrics", 
            "Consider diversification across sectors"
        ]
        
        # Add specific insights based on results
        if filtered_stocks:
            avg_yield = sum(stock.dividend_yield for stock in filtered_stocks[:5]) / min(5, len(filtered_stocks))
            high_yield_count = sum(1 for stock in filtered_stocks if stock.dividend_yield > 5.0)
            
            if avg_yield > 5.0:
                enhanced_suggestions.append(f"Average yield of top stocks is {avg_yield:.1f}% - consider risk factors")
            if high_yield_count > 0:
                enhanced_suggestions.append(f"Found {high_yield_count} high-yield stocks (>5%) - verify dividend sustainability")
            
            # Sector diversity check
            sectors = set(stock.sector for stock in filtered_stocks[:10])
            if len(sectors) > 3:
                enhanced_suggestions.append(f"Good sector diversity across {len(sectors)} sectors")
            else:
                enhanced_suggestions.append("Consider diversifying across more sectors")

        return LiveResponse(
            True,
            {
                'screening_results': results,
                'analysis_results': analysis_results,
                'total_found': len(filtered_stocks),
                'criteria_used': criteria_display,
                'data_source': 'Yahoo Finance (Live)',
                'stocks_analyzed': len(live_stocks),
                'average_yield': round(sum(stock.dividend_yield for stock in filtered_stocks[:10]) / min(10, len(filtered_stocks)), 2) if filtered_stocks else 0,
                'sector_diversity': len(set(stock.sector for stock in filtered_stocks[:10])) if filtered_stocks else 0
            },
            f"Found {len(filtered_stocks)} dividend stocks matching your criteria using live market data.",
            enhanced_suggestions,
            0, data_freshness
        )
    
    async def _analyze_stocks_live(self, tickers: List[str]) -> LiveResponse:
        """Analyze specific stocks using live market data"""
        # Fetch live data for requested stocks
        live_stocks = self._fetch_multiple_stocks(tickers)
        
        if not live_stocks:
            return LiveResponse(
                False, None, "Unable to fetch live market data for the requested stocks.",
                ["Check ticker symbols", "Try again in a few moments"],
                0, "Data fetch failed"
            )
        
        analysis_results = {}
        for stock in live_stocks:
            # Quality assessment based on current data
            assessment = "Limited dividend appeal"
            quality_score = 3.0  # Default low score
            
            if stock.dividend_yield > 4.0:
                assessment = "Excellent dividend quality"
                quality_score = 8.5
            elif stock.dividend_yield > 2.5:
                assessment = "Good dividend potential"
                quality_score = 7.0
            elif stock.dividend_yield > 1.0:
                assessment = "Moderate dividend quality"
                quality_score = 5.5
            else:
                assessment = "Limited dividend appeal"
                quality_score = 3.0
            
            # Generate strengths and risks based on actual data
            strengths = []
            risks = []
            
            # Dividend yield analysis
            if stock.dividend_yield > 4.0:
                strengths.append(f"High dividend yield of {stock.dividend_yield:.2f}%")
            elif stock.dividend_yield > 2.0:
                strengths.append(f"Solid dividend yield of {stock.dividend_yield:.2f}%")
            elif stock.dividend_yield < 1.0:
                risks.append(f"Low dividend yield of {stock.dividend_yield:.2f}%")
            
            # Payout ratio analysis
            if stock.payout_ratio > 0:
                if stock.payout_ratio < 60:
                    strengths.append(f"Conservative payout ratio of {stock.payout_ratio:.1f}%")
                elif stock.payout_ratio > 80:
                    risks.append(f"High payout ratio of {stock.payout_ratio:.1f}% may be unsustainable")
            
            # P/E ratio analysis
            if stock.pe_ratio > 0:
                if stock.pe_ratio < 15:
                    strengths.append(f"Attractive P/E ratio of {stock.pe_ratio:.1f}")
                elif stock.pe_ratio > 30:
                    risks.append(f"High P/E ratio of {stock.pe_ratio:.1f} indicates expensive valuation")
            
            # Market cap and stability
            if stock.market_cap > 100_000_000_000:  # $100B+
                strengths.append("Large-cap stability and established market position")
            elif stock.market_cap < 10_000_000_000:  # <$10B
                risks.append("Smaller market cap may indicate higher volatility")
            
            # Sector-specific insights
            if stock.sector == 'Utilities':
                strengths.append("Utilities sector provides defensive characteristics")
            elif stock.sector == 'Technology':
                risks.append("Technology sector may have lower dividend focus")
                
            analysis_results[stock.ticker] = {
                'ticker': stock.ticker,
                'name': stock.name,
                'current_price': round(stock.price, 2),
                'dividend_yield': round(stock.dividend_yield, 2),
                'pe_ratio': round(stock.pe_ratio, 1) if stock.pe_ratio > 0 else 'N/A',
                'annual_dividend': round(stock.annual_dividend, 2),
                'payout_ratio': round(stock.payout_ratio, 1) if stock.payout_ratio > 0 else 'N/A',
                'market_cap': f"${stock.market_cap / 1_000_000_000:.1f}B" if stock.market_cap > 0 else 'N/A',
                'sector': stock.sector,
                'assessment': assessment,
                'quality_score': quality_score,
                'strengths': strengths,
                'risks': risks,
                'last_updated': stock.last_updated.isoformat()
            }
        
        oldest_data = min(stock.last_updated for stock in live_stocks)
        data_age = datetime.utcnow() - oldest_data
        data_freshness = f"Live data (max {data_age.seconds//60} min old)"
        
        return LiveResponse(
            True,
            {
                'analysis_results': analysis_results,
                'data_source': 'Yahoo Finance (Live)'
            },
            f"Comprehensive dividend analysis completed for {len(analysis_results)} stocks using live market data. Each stock has been evaluated for dividend quality, sustainability metrics, and investment potential based on current financial fundamentals including yield, payout ratios, P/E valuations, and sector characteristics.",
            [
                "All data is current market data",
                "Compare dividend sustainability metrics",
                "Consider portfolio allocation weights"
            ],
            0, data_freshness
        )
    
    async def _provide_investment_guidance(self, criteria: Dict[str, Any], original_query: str) -> LiveResponse:
        """Provide concise investment guidance with max earnings and risk assessment"""
        initial_investment = criteria.get('initial_investment', 0)
        target_annual_income = criteria.get('target_annual_income', 0)
        target_monthly_income = criteria.get('target_monthly_income', 0)
        query_type = criteria.get('query_type', 'goal_oriented')
        
        if initial_investment > 0:
            if query_type == 'exploratory':
                # For exploratory queries, show realistic income ranges without specific targets
                return await self._provide_exploratory_guidance(initial_investment, original_query)
            elif target_annual_income > 0:
                # For goal-oriented queries with specific targets
                return await self._provide_goal_oriented_guidance(initial_investment, target_annual_income, target_monthly_income, original_query)
            else:
                # Fallback for goal-oriented queries without targets
                return await self._provide_exploratory_guidance(initial_investment, original_query)
        else:
            # General guidance without specific amounts
            return LiveResponse(
                True,
                {'general_guidance': True},
                "Specify your investment amount and target for precise recommendations.",
                [
                    "Try: 'I have $10000 and want $100 monthly'",
                    "Higher returns = Higher risk",
                    "Dividend yields: 3-7% realistic, 8-15% aggressive, >15% speculative"
                ],
                0, "General investment guidance"
            )
    
    async def _provide_exploratory_guidance(self, initial_investment: float, original_query: str) -> LiveResponse:
        """Provide exploratory guidance showing realistic income ranges for an investment amount"""
        # Define realistic yield ranges for different risk levels
        risk_scenarios = {
            'conservative': {'min_yield': 0.025, 'max_yield': 0.05, 'typical_yield': 0.04, 'label': 'Low (15%)'},
            'moderate': {'min_yield': 0.04, 'max_yield': 0.08, 'typical_yield': 0.06, 'label': 'Moderate (35%)'},
            'aggressive': {'min_yield': 0.08, 'max_yield': 0.15, 'typical_yield': 0.12, 'label': 'High (65%)'}
        }
        
        # Calculate income ranges for each scenario
        income_scenarios = {}
        for risk_level, params in risk_scenarios.items():
            min_annual = initial_investment * params['min_yield']
            max_annual = initial_investment * params['max_yield']
            typical_annual = initial_investment * params['typical_yield']
            
            income_scenarios[risk_level] = {
                'risk_label': params['label'],
                'min_monthly': round(min_annual / 12, 2),
                'max_monthly': round(max_annual / 12, 2),
                'typical_monthly': round(typical_annual / 12, 2),
                'min_annual': round(min_annual, 2),
                'max_annual': round(max_annual, 2),
                'typical_annual': round(typical_annual, 2)
            }
        
        # Define stock portfolios for each risk level
        portfolio_tickers = {
            'conservative': ['SCHD', 'VYM', 'JNJ', 'PG', 'KO', 'MSFT'],
            'moderate': ['VYM', 'SCHD', 'O', 'VZ', 'PFE', 'T'],
            'aggressive': ['O', 'MAIN', 'ARCC', 'QYLD', 'JEPI', 'AGNC']
        }
        
        # Generate portfolios for all risk levels
        portfolio_examples = {}
        for risk_level, tickers in portfolio_tickers.items():
            live_stocks = self._fetch_multiple_stocks(tickers)
            live_stocks.sort(key=lambda x: x.dividend_yield, reverse=True)
            top_picks = live_stocks[:6]
            
            dividend_picks = []
            for stock in top_picks:
                annual_from_stock = initial_investment * (stock.dividend_yield / 100)
                monthly_from_stock = annual_from_stock / 12
                dividend_picks.append({
                    'ticker': stock.ticker,
                    'yield': round(stock.dividend_yield, 1),
                    'monthly_income': round(monthly_from_stock, 2),
                    'annual_income': round(annual_from_stock, 2),
                    'price': round(stock.price, 2),
                    'name': stock.name
                })
            
            portfolio_examples[risk_level] = {
                'stocks': dividend_picks,
                'avg_yield': round(sum(pick['yield'] for pick in dividend_picks) / len(dividend_picks), 2) if dividend_picks else 0,
                'total_monthly': round(sum(pick['monthly_income'] for pick in dividend_picks), 2),
                'description': self._get_portfolio_description(risk_level)
            }
        
        # Calculate overall realistic estimate using conservative portfolio
        realistic_monthly = portfolio_examples['conservative']['total_monthly'] / len(portfolio_examples['conservative']['stocks']) if portfolio_examples['conservative']['stocks'] else income_scenarios['conservative']['typical_monthly']
        
        return LiveResponse(
            True,
            {
                'exploratory_guidance': {
                    'investment_amount': initial_investment,
                    'income_scenarios': income_scenarios,
                    'realistic_monthly_estimate': round(realistic_monthly, 2),
                    'portfolio_examples': portfolio_examples,
                    'analysis_type': 'realistic_income_exploration'
                }
            },
            f"With ${initial_investment:,}, realistic income ranges: ${income_scenarios['conservative']['min_monthly']}-${income_scenarios['conservative']['max_monthly']}/month (conservative), ${income_scenarios['moderate']['min_monthly']}-${income_scenarios['moderate']['max_monthly']}/month (moderate), ${income_scenarios['aggressive']['min_monthly']}-${income_scenarios['aggressive']['max_monthly']}/month (aggressive).",
            [
                f"Conservative: ${income_scenarios['conservative']['min_monthly']}-${income_scenarios['conservative']['max_monthly']}/month",
                f"Moderate: ${income_scenarios['moderate']['min_monthly']}-${income_scenarios['moderate']['max_monthly']}/month",
                f"Aggressive: ${income_scenarios['aggressive']['min_monthly']}-${income_scenarios['aggressive']['max_monthly']}/month",
                "Higher yields = Higher risk"
            ],
            0, "Realistic income exploration"
        )
    
    def _get_portfolio_description(self, risk_level: str) -> str:
        """Get description for each portfolio type"""
        descriptions = {
            'conservative': 'Blue-chip dividend stocks and ETFs with stable payouts and lower volatility',
            'moderate': 'Mix of dividend stocks, REITs, and moderate-yield investments with balanced risk',
            'aggressive': 'High-yield REITs, covered call ETFs, and dividend-focused investments with higher risk'
        }
        return descriptions.get(risk_level, 'Diversified dividend portfolio')
    
    async def _provide_goal_oriented_guidance(self, initial_investment: float, target_annual_income: float, target_monthly_income: float, original_query: str) -> LiveResponse:
        """Provide goal-oriented guidance for achieving specific income targets"""
        required_yield = target_annual_income / initial_investment
        
        # Determine risk level and maximum potential
        if required_yield <= 0.05:  # 5%
            risk_level = "Low (15%)"
            max_potential = initial_investment * 0.07  # 7% max with low risk
            strategy = "conservative"
        elif required_yield <= 0.08:  # 8%
            risk_level = "Moderate (35%)"
            max_potential = initial_investment * 0.12  # 12% max with moderate risk
            strategy = "balanced"
        elif required_yield <= 0.15:  # 15%
            risk_level = "High (65%)"
            max_potential = initial_investment * 0.18  # 18% max with high risk
            strategy = "aggressive"
        else:  # >15%
            risk_level = "Very High (85%)"
            max_potential = initial_investment * 0.25  # 25% max with very high risk
            strategy = "speculative"
        
        # Get direct dividend recommendations based on strategy
        if strategy == "conservative":
            target_tickers = ['SCHD', 'VYM', 'JNJ', 'PG', 'KO', 'MSFT']
        elif strategy == "balanced":
            target_tickers = ['VYM', 'SCHD', 'O', 'VZ', 'PFE', 'T', 'JNJ']
        elif strategy == "aggressive":
            target_tickers = ['O', 'MAIN', 'ARCC', 'VZ', 'T', 'PFE', 'QYLD']
        else:  # speculative
            target_tickers = ['QYLD', 'JEPI', 'MAIN', 'ARCC', 'O', 'T', 'AGNC']
        
        # Fetch live data for recommendations
        live_stocks = self._fetch_multiple_stocks(target_tickers)
        
        # Sort by yield descending and take top picks
        live_stocks.sort(key=lambda x: x.dividend_yield, reverse=True)
        top_picks = live_stocks[:6]
        
        # Calculate actual potential from top picks
        if top_picks:
            avg_yield = sum(stock.dividend_yield for stock in top_picks[:3]) / 3
            realistic_annual = initial_investment * (avg_yield / 100)
            realistic_monthly = realistic_annual / 12
        else:
            realistic_annual = max_potential * 0.6
            realistic_monthly = realistic_annual / 12
        
        # Build concise recommendation
        dividend_picks = []
        for stock in top_picks:
            annual_from_stock = initial_investment * (stock.dividend_yield / 100)
            monthly_from_stock = annual_from_stock / 12
            dividend_picks.append({
                'ticker': stock.ticker,
                'yield': round(stock.dividend_yield, 1),
                'monthly_income': round(monthly_from_stock, 2),
                'annual_income': round(annual_from_stock, 2)
            })
        
        return LiveResponse(
            True,
            {
                'concise_guidance': {
                    'investment_amount': initial_investment,
                    'target_monthly': target_monthly_income,
                    'required_yield': round(required_yield * 100, 1),
                    'risk_assessment': risk_level,
                    'max_potential_annual': round(max_potential, 2),
                    'max_potential_monthly': round(max_potential / 12, 2),
                    'realistic_annual': round(realistic_annual, 2),
                    'realistic_monthly': round(realistic_monthly, 2),
                    'strategy': strategy,
                    'dividend_picks': dividend_picks,
                    'analysis_type': 'goal_oriented_planning'
                }
            },
            f"With ${initial_investment:,}, max potential: ${max_potential/12:,.0f}/month at {risk_level} risk. Realistic: ${realistic_monthly:,.0f}/month.",
            [
                f"Risk Level: {risk_level}",
                f"Max Potential: ${max_potential/12:,.0f}/month",
                f"Realistic Expectation: ${realistic_monthly:,.0f}/month",
                f"Strategy: {strategy.title()} dividend approach"
            ],
            0, "Concise guidance"
        )

    def _extract_tickers(self, query: str) -> List[str]:
        """Extract valid stock tickers from query"""
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        potential_tickers = re.findall(ticker_pattern, query.upper())
        
        # Return unique tickers, limited to 10
        return list(set(potential_tickers))[:10] 
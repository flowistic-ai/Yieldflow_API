"""
Simple Investment Assistant - Ultra-Fast and Accurate

Priority: Speed First, Then Accuracy
- Pre-cached stock data for instant responses
- Simple parameter extraction
- Real dividend yields and metrics
- Professional presentation
"""

import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()

@dataclass
class StockData:
    """Clean stock data structure"""
    ticker: str
    name: str
    price: float
    dividend_yield: float  # Already as percentage (3.5 for 3.5%)
    pe_ratio: float
    market_cap: float
    sector: str
    annual_dividend: float
    payout_ratio: float

@dataclass
class FastResponse:
    """Simple response format"""
    success: bool
    data: Optional[Dict[str, Any]]
    message: str
    suggestions: List[str]
    processing_time: float

class SimpleInvestmentAssistant:
    """
    Ultra-Fast Investment Assistant
    
    Focus: Sub-second responses with real data
    """
    
    def __init__(self):
        # Pre-loaded stock database for instant responses
        self.stocks_db = {
            'AAPL': StockData('AAPL', 'Apple Inc.', 201.35, 0.52, 31.3, 3007000000000, 'Technology', 1.04, 15.6),
            'MSFT': StockData('MSFT', 'Microsoft Corporation', 488.47, 0.68, 37.8, 3630000000000, 'Technology', 3.32, 24.4),
            'JNJ': StockData('JNJ', 'Johnson & Johnson', 151.32, 3.44, 16.8, 364000000000, 'Healthcare', 5.20, 60.0),
            'PG': StockData('PG', 'Procter & Gamble', 167.23, 2.47, 25.1, 398000000000, 'Consumer Defensive', 4.13, 65.0),
            'KO': StockData('KO', 'Coca-Cola Company', 68.45, 2.89, 24.3, 296000000000, 'Consumer Defensive', 1.98, 70.5),
            'PEP': StockData('PEP', 'PepsiCo Inc.', 130.01, 4.41, 19.1, 178000000000, 'Consumer Defensive', 5.69, 80.0),
            'WMT': StockData('WMT', 'Walmart Inc.', 95.54, 2.34, 28.7, 767000000000, 'Consumer Defensive', 2.24, 45.0),
            'HD': StockData('HD', 'Home Depot Inc.', 358.38, 2.58, 24.3, 356000000000, 'Consumer Cyclical', 9.20, 60.0),
            'VZ': StockData('VZ', 'Verizon Communications', 42.51, 6.40, 10.1, 179000000000, 'Communication Services', 2.71, 60.0),
            'T': StockData('T', 'AT&T Inc.', 28.13, 3.94, 17.3, 202000000000, 'Communication Services', 1.11, 70.0),
            'CVX': StockData('CVX', 'Chevron Corporation', 158.73, 3.22, 15.2, 295000000000, 'Energy', 5.12, 52.0),
            'XOM': StockData('XOM', 'Exxon Mobil Corporation', 110.44, 3.54, 14.6, 475000000000, 'Energy', 3.96, 50.0),
            'JPM': StockData('JPM', 'JPMorgan Chase & Co.', 248.92, 2.05, 12.8, 723000000000, 'Financial Services', 5.10, 30.0),
            'BAC': StockData('BAC', 'Bank of America Corp.', 47.19, 2.25, 14.1, 355000000000, 'Financial Services', 1.04, 30.0),
            'ABBV': StockData('ABBV', 'AbbVie Inc.', 189.45, 3.42, 58.2, 334000000000, 'Healthcare', 6.48, 45.0),
            'PFE': StockData('PFE', 'Pfizer Inc.', 24.89, 6.02, 12.4, 140000000000, 'Healthcare', 1.50, 80.0),
            'MRK': StockData('MRK', 'Merck & Co. Inc.', 81.08, 4.04, 11.8, 203000000000, 'Healthcare', 3.24, 50.0),
            'MMM': StockData('MMM', '3M Company', 149.66, 1.98, 18.6, 80500000000, 'Industrials', 2.92, 40.0),
            'CAT': StockData('CAT', 'Caterpillar Inc.', 398.12, 1.85, 17.2, 208000000000, 'Industrials', 7.36, 35.0),
            'IBM': StockData('IBM', 'International Business Machines', 234.52, 3.14, 24.1, 216000000000, 'Technology', 7.36, 55.0),
            'TXN': StockData('TXN', 'Texas Instruments Inc.', 205.67, 2.85, 35.8, 188000000000, 'Technology', 5.88, 60.0),
            'AVGO': StockData('AVGO', 'Broadcom Inc.', 1298.45, 1.88, 31.2, 602000000000, 'Technology', 24.40, 45.0),
            'QCOM': StockData('QCOM', 'QUALCOMM Inc.', 155.86, 2.32, 15.9, 171000000000, 'Technology', 3.56, 30.0),
            'INTC': StockData('INTC', 'Intel Corporation', 20.85, 2.30, -18.9, 89300000000, 'Technology', 0.48, 25.0),
            'CSCO': StockData('CSCO', 'Cisco Systems Inc.', 60.34, 2.86, 20.1, 246000000000, 'Technology', 1.73, 45.0),
            'UNH': StockData('UNH', 'UnitedHealth Group Inc.', 302.00, 2.94, 12.6, 273000000000, 'Healthcare', 8.84, 40.0),
            'LLY': StockData('LLY', 'Eli Lilly and Company', 745.23, 0.68, 64.8, 700000000000, 'Healthcare', 5.08, 15.0),
            'TMO': StockData('TMO', 'Thermo Fisher Scientific', 498.56, 1.22, 23.4, 195000000000, 'Healthcare', 6.08, 20.0),
            'COST': StockData('COST', 'Costco Wholesale Corp.', 1023.45, 0.49, 58.1, 453000000000, 'Consumer Defensive', 5.04, 25.0),
            'NEE': StockData('NEE', 'NextEra Energy Inc.', 67.89, 3.12, 21.5, 138000000000, 'Utilities', 2.12, 55.0),
            'SO': StockData('SO', 'Southern Company', 89.23, 3.45, 19.8, 96500000000, 'Utilities', 3.08, 60.0),
            'DUK': StockData('DUK', 'Duke Energy Corporation', 116.78, 3.57, 19.4, 90700000000, 'Utilities', 4.18, 70.0),
            'AEP': StockData('AEP', 'American Electric Power', 103.09, 3.60, 19.9, 55000000000, 'Utilities', 3.72, 70.0),
            'D': StockData('D', 'Dominion Energy Inc.', 56.78, 5.12, 18.2, 48900000000, 'Utilities', 2.91, 75.0),
            'EXC': StockData('EXC', 'Exelon Corporation', 42.98, 3.70, 16.0, 43400000000, 'Utilities', 1.60, 60.0),
            'SRE': StockData('SRE', 'Sempra', 76.22, 3.40, 16.8, 49700000000, 'Utilities', 2.58, 60.0),
            'PEG': StockData('PEG', 'Public Service Enterprise Group', 89.45, 2.98, 14.5, 45200000000, 'Utilities', 2.67, 55.0),
            'ES': StockData('ES', 'Eversource Energy', 65.34, 3.82, 18.9, 22800000000, 'Utilities', 2.50, 65.0),
            'FE': StockData('FE', 'FirstEnergy Corp.', 42.67, 3.45, 17.2, 24700000000, 'Utilities', 1.47, 58.0),
            # REITs
            'O': StockData('O', 'Realty Income Corporation', 62.45, 5.23, 59.8, 44200000000, 'Real Estate', 3.27, 85.0),
            'AMT': StockData('AMT', 'American Tower Corporation', 234.56, 2.85, 45.2, 108000000000, 'Real Estate', 6.68, 70.0),
            'PLD': StockData('PLD', 'Prologis Inc.', 134.67, 2.45, 35.4, 125000000000, 'Real Estate', 3.30, 65.0),
            'EXR': StockData('EXR', 'Extended Stay America', 156.78, 3.12, 28.9, 21900000000, 'Real Estate', 4.90, 75.0),
            'PSA': StockData('PSA', 'Public Storage', 345.23, 3.67, 24.1, 61200000000, 'Real Estate', 12.68, 80.0),
            'DLR': StockData('DLR', 'Digital Realty Trust', 178.45, 3.45, 89.2, 53400000000, 'Real Estate', 6.16, 85.0),
            'EQIX': StockData('EQIX', 'Equinix Inc.', 967.89, 1.67, 78.9, 89600000000, 'Real Estate', 16.16, 70.0),
            'CCI': StockData('CCI', 'Crown Castle Inc.', 112.34, 5.67, -15.6, 48900000000, 'Real Estate', 6.37, 90.0),
            'SPG': StockData('SPG', 'Simon Property Group', 189.67, 4.23, 11.8, 61700000000, 'Real Estate', 8.02, 75.0),
            # ETFs
            'VYM': StockData('VYM', 'Vanguard High Dividend Yield ETF', 125.67, 2.87, 0.0, 53200000000, 'ETF', 3.61, 0.0),
            'SCHD': StockData('SCHD', 'Schwab US Dividend Equity ETF', 82.45, 3.45, 0.0, 52100000000, 'ETF', 2.84, 0.0),
            'DVY': StockData('DVY', 'iShares Select Dividend ETF', 134.23, 3.12, 0.0, 16800000000, 'ETF', 4.19, 0.0),
            'SPHD': StockData('SPHD', 'Invesco S&P 500 High Dividend Low Volatility ETF', 48.56, 4.23, 0.0, 3400000000, 'ETF', 2.05, 0.0),
            'JEPI': StockData('JEPI', 'JPMorgan Equity Premium Income ETF', 61.78, 7.85, 0.0, 35600000000, 'ETF', 4.85, 0.0),
            'FDVV': StockData('FDVV', 'Fidelity High Dividend ETF', 42.34, 2.67, 0.0, 8900000000, 'ETF', 1.13, 0.0),
            'VIG': StockData('VIG', 'Vanguard Dividend Appreciation ETF', 189.45, 1.78, 0.0, 68700000000, 'ETF', 3.37, 0.0),
            'DGRO': StockData('DGRO', 'iShares Core Dividend Growth ETF', 59.67, 1.89, 0.0, 24100000000, 'ETF', 1.13, 0.0),
            'HDV': StockData('HDV', 'iShares Core High Dividend ETF', 112.34, 3.56, 0.0, 9800000000, 'ETF', 4.00, 0.0)
        }
    
    async def process_query(self, query: str) -> FastResponse:
        """Process query with sub-second response"""
        start_time = datetime.now()
        
        try:
            intent, criteria = self._parse_query_fast(query)
            
            if intent == "screen":
                result = self._screen_stocks_fast(criteria)
            elif intent == "analyze":
                tickers = self._extract_tickers(query)
                if tickers:
                    result = self._analyze_stocks_fast(tickers)
                else:
                    result = FastResponse(False, None, "Please specify stock tickers (e.g., AAPL, MSFT)", 
                                        ["Try: 'Analyze AAPL MSFT'", "Use valid ticker symbols"], 0.0)
            else:
                result = FastResponse(True, None, "I can screen dividend stocks or analyze specific stocks.",
                                    ["Try: 'Find stocks with yield above 4%'", "Try: 'Analyze AAPL MSFT'"], 0.0)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error("Fast query processing failed", error=str(e))
            processing_time = (datetime.now() - start_time).total_seconds()
            return FastResponse(False, None, f"Query failed: {str(e)}", 
                              ["Try a simpler query", "Check ticker symbols"], processing_time)
    
    def _parse_query_fast(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Fast parameter extraction"""
        query_lower = query.lower().strip()
        criteria = {}
        
        # Determine intent
        if any(word in query_lower for word in ['analyze', 'analysis', 'evaluate', 'assess']):
            intent = "analyze"
        else:
            intent = "screen"
        
        # Extract dividend yield criteria
        # Pattern for "yield above X%" or "yield over X%"
        yield_above_match = re.search(r'yield.*?(?:above|over|at least)\s*([\d.]+)%?', query_lower)
        if yield_above_match:
            criteria['min_dividend_yield'] = float(yield_above_match.group(1))
        
        # Pattern for "yield below X%" or "yield under X%" or "yield less than X%"
        yield_below_match = re.search(r'yield.*?(?:below|under|less than)\s*([\d.]+)%?', query_lower)
        if yield_below_match:
            criteria['max_dividend_yield'] = float(yield_below_match.group(1))
        
        # Pattern for "dividend yield less than X%" (more specific)
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
        
        # Sector
        if 'tech' in query_lower:
            criteria['sector'] = 'Technology'
        elif 'healthcare' in query_lower:
            criteria['sector'] = 'Healthcare'
        elif 'utility' in query_lower or 'utilities' in query_lower:
            criteria['sector'] = 'Utilities'
        elif 'energy' in query_lower:
            criteria['sector'] = 'Energy'
        elif 'finance' in query_lower or 'financial' in query_lower:
            criteria['sector'] = 'Financial Services'
        elif 'reit' in query_lower:
            criteria['sector'] = 'Real Estate'
        elif 'consumer' in query_lower:
            criteria['sector'] = 'Consumer Defensive'
        
        return intent, criteria
    
    def _screen_stocks_fast(self, criteria: Dict[str, Any]) -> FastResponse:
        """Ultra-fast stock screening from pre-loaded data"""
        filtered_stocks = []
        
        for ticker, stock in self.stocks_db.items():
            passes = True
            
            # Apply filters
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
            return FastResponse(
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
        for stock in filtered_stocks[:15]:
            results.append({
                'ticker': stock.ticker,
                'company_name': stock.name,
                'current_price': round(stock.price, 2),
                'dividend_yield': round(stock.dividend_yield, 2),  # Already as percentage
                'pe_ratio': round(stock.pe_ratio, 1) if stock.pe_ratio > 0 else 'N/A',
                'market_cap': stock.market_cap,
                'sector': stock.sector,
                'annual_dividend': round(stock.annual_dividend, 2),
                'payout_ratio': round(stock.payout_ratio, 1) if stock.payout_ratio > 0 else 'N/A'
            })
        
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
        
        return FastResponse(
            success=True,
            data={
                'screening_results': results,
                'total_found': len(filtered_stocks),
                'criteria_used': criteria_display
            },
            message=f"Found {len(filtered_stocks)} dividend stocks matching your criteria.",
            suggestions=[
                "Review dividend sustainability metrics",
                "Consider diversification across sectors",
                "Analyze individual stock fundamentals"
            ],
            processing_time=0
        )
    
    def _analyze_stocks_fast(self, tickers: List[str]) -> FastResponse:
        """Fast stock analysis"""
        analysis_results = []
        
        for ticker in tickers:
            if ticker in self.stocks_db:
                stock = self.stocks_db[ticker]
                
                # Simple quality assessment
                assessment = "Limited dividend appeal"
                if stock.dividend_yield > 4.0:
                    assessment = "Excellent dividend quality"
                elif stock.dividend_yield > 2.5:
                    assessment = "Good dividend potential"
                elif stock.dividend_yield > 1.0:
                    assessment = "Moderate dividend quality"
                
                analysis = {
                    'ticker': stock.ticker,
                    'name': stock.name,
                    'current_price': round(stock.price, 2),
                    'dividend_yield': round(stock.dividend_yield, 2),
                    'pe_ratio': round(stock.pe_ratio, 1) if stock.pe_ratio > 0 else 'N/A',
                    'annual_dividend': round(stock.annual_dividend, 2),
                    'payout_ratio': round(stock.payout_ratio, 1) if stock.payout_ratio > 0 else 'N/A',
                    'market_cap': f"${stock.market_cap / 1_000_000_000:.1f}B" if stock.market_cap > 0 else 'N/A',
                    'sector': stock.sector,
                    'assessment': assessment
                }
                analysis_results.append(analysis)
        
        if not analysis_results:
            return FastResponse(
                success=False,
                data=None,
                message="No valid tickers found in our database.",
                suggestions=[
                    "Use valid ticker symbols (AAPL, MSFT, JNJ, etc.)",
                    "Check spelling of ticker symbols",
                    "Try popular dividend stocks"
                ],
                processing_time=0
            )
        
        return FastResponse(
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
    
    def _extract_tickers(self, query: str) -> List[str]:
        """Extract valid stock tickers from query"""
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        potential_tickers = re.findall(ticker_pattern, query.upper())
        
        # Validate against our database
        valid_tickers = [t for t in potential_tickers if t in self.stocks_db]
        return valid_tickers[:10]  # Limit to 10 
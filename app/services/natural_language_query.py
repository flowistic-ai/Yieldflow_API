import re
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import structlog

from app.services.ai_insights import AIInsightsService
from app.services.data_provider import DataProvider
from app.services.portfolio_optimizer import EnhancedPortfolioOptimizer
from app.services.dividend_service import DividendService
from app.services.financial_analyzer import FinancialAnalyzer
from app.services.ratio_calculator import RatioCalculator
from app.schemas.portfolio import (
    PortfolioOptimizationRequest, 
    OptimizationObjective, 
    ShrinkageMethod,
    PortfolioOptimizationResult
)
from app.core.config import settings

logger = structlog.get_logger()

@dataclass
class QueryIntent:
    """Represents the interpreted intent of a natural language query."""
    action: str  # screen, optimize, analyze, compare, recommend
    parameters: Dict[str, Any]
    confidence: float
    explanation: str
    requires_confirmation: bool = False

@dataclass
class QueryResponse:
    """Response to a natural language query."""
    success: bool
    data: Optional[Dict[str, Any]]
    explanation: str
    suggestions: List[str]
    visualization_config: Optional[Dict[str, Any]] = None
    confidence: float = 1.0

class NaturalLanguageQueryEngine:
    """
    Enhanced Natural Language Query Engine with comprehensive backend integration.
    
    Integrates multiple financial data sources:
    - YFinance: Real-time stock data and historical information
    - Alpha Vantage: Professional financial data and fundamentals  
    - Financial Modeling Prep (FMP): Detailed financial statements
    - FRED: Economic indicators and treasury rates
    - Google Gemini: AI-powered insights and analysis
    """
    
    def __init__(self):
        self.data_provider = DataProvider()
        self.ai_insights = AIInsightsService()
        # Initialize comprehensive financial services
        self.dividend_service = DividendService()
        self.financial_analyzer = FinancialAnalyzer()
        self.ratio_calculator = RatioCalculator()
        
        # Enhanced intent patterns for better classification
        self.intent_patterns = {
            'recommend_etf': [
                # ETF-specific patterns (highest priority for ETF queries)
                r'(?:best|good|recommend|suggest).*(?:etf|fund).*alternative',
                r'(?:etf|fund).*alternative',
                r'dividend.*(?:etf|fund)',
                r'(?:best|good).*(?:etf|fund)',
                r'alternative.*(?:etf|fund)',
                r'(?:reit|reits).*alternative',
                r'instead.*(?:etf|fund)'
            ],
            'recommend': [
                # Income-based patterns (highest priority)
                r'I need \$?(\d+(?:,\d+)?)\s*(monthly|annually|yearly)?\s*income',
                r'generate \$?(\d+(?:,\d+)?)\s*(monthly|annually|yearly)?\s*income',
                r'(\d+(?:,\d+)?)\s*dollars?\s*(monthly|annually|yearly)?\s*income',
                r'monthly income.*\$?(\d+(?:,\d+)?)',
                r'annual income.*\$?([\d,]+)',
                # Objective patterns
                r'(growth|income|aggressive|conservative|balanced)\s*(strategy|approach|investment)',
                r'recommend.*stocks',
                r'suggest.*investments',
                r'what.*should.*invest',
                r'best.*dividend.*stocks',
                r'good.*stocks.*for'
            ],
            'screen': [
                r'find.*stocks.*yield.*(\d+(?:\.\d+)?)%?',
                r'dividend.*yield.*above.*(\d+(?:\.\d+)?)%?',
                r'stocks.*paying.*(\d+(?:\.\d+)?)%?',
                r'screen.*dividend',
                r'filter.*stocks',
                r'show.*stocks.*with'
            ],
            'analyze': [
                r'analyze.*([A-Z]{1,5})',
                r'tell me about.*([A-Z]{1,5})', 
                r'what.*think.*([A-Z]{1,5})',
                r'research.*([A-Z]{1,5})',
                r'details.*([A-Z]{1,5})',
                r'information.*([A-Z]{1,5})'
            ],
            'optimize': [
                r'optimize.*portfolio',
                r'best.*allocation',
                r'portfolio.*optimization',
                r'efficient.*frontier',
                r'allocate.*funds'
            ],
            'compare': [
                r'compare.*([A-Z]{1,5}).*([A-Z]{1,5})',
                r'([A-Z]{1,5}).*vs.*([A-Z]{1,5})',
                r'which.*better.*([A-Z]{1,5}).*([A-Z]{1,5})',
                r'difference.*between'
            ]
        }
        
        # Parameter extraction patterns
        self.parameter_patterns = {
            'tickers': r'\b([A-Z]{2,5})\b(?=\s|,|$)',
            'yield_min': r'yield.*(above|over|minimum).*([\d\.]+)%?',
            'yield_max': r'yield.*(below|under|maximum).*([\d\.]+)%?',
            'price_min': r'price.*(above|over|minimum).*\$?([\d\.]+)',
            'price_max': r'price.*(below|under|maximum).*\$?([\d\.]+)',
            'market_cap': r'market cap.*(above|below|over|under).*\$?([\d\.]+)(b|billion|m|million|k|thousand)?',
            'sector': r'(technology|healthcare|finance|energy|utilities|consumer|industrial|materials|real estate|communication)',
            'time_horizon': r'([\d]+).*(year|month|day)',
            'risk_tolerance': r'(conservative|moderate|aggressive|low|medium|high).*(risk)',
            'income_goal': r'[\$]?([\d,]+).*(monthly|annually|yearly).*(income)',
            'growth_rate': r'([\d\.]+)%?.*(growth|return)',
            'objective': r'(income|growth|balanced|conservative|aggressive|dividend)'
        }
    
    async def process_query(self, query: str, user_context: Optional[Dict] = None) -> QueryResponse:
        """
        Enhanced query processing with comprehensive backend integration.
        """
        try:
            logger.info("Processing enhanced query", query=query, context=user_context)
            
            # Parse intent using enhanced patterns
            intent = await self._parse_query_intent(query, user_context)
            logger.info("Parsed intent", action=intent.action, confidence=intent.confidence)
            
            # Route to appropriate handler
            if intent.action == 'screen':
                response = await self._execute_enhanced_screening(intent, query)
            elif intent.action == 'optimize':
                response = await self._execute_optimization(intent, query)
            elif intent.action == 'analyze':
                response = await self._execute_analysis(intent, query)
            elif intent.action == 'compare':
                response = await self._execute_comparison(intent, query)
            elif intent.action == 'recommend_etf':
                response = await self._execute_etf_recommendation(intent, query)
            elif intent.action == 'recommend':
                response = await self._execute_enhanced_recommendation(intent, query)
            else:
                response = await self._handle_unclear_query(query)
            
            # Enhance response with AI insights using backend data
            if response.success:
                response = await self._enhance_response_with_backend_ai(response, query, intent)
            
            return response
            
        except Exception as e:
            logger.error("Query processing failed", query=query, error=str(e))
            return QueryResponse(
                success=False,
                data=None,
                explanation="I encountered an error processing your request. Please try rephrasing your question.",
                suggestions=[
                    "Try a simpler question",
                    "Check if ticker symbols are valid",
                    "Ask about specific dividend yields or stock analysis"
                ]
            )
    
    async def _parse_query_intent(self, query: str, user_context: Optional[Dict] = None) -> QueryIntent:
        """Enhanced intent parsing with better accuracy."""
        query_lower = query.lower()
        
        # Check patterns in priority order (recommend first for income queries)
        for action, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    parameters = await self._extract_enhanced_parameters(query, user_context)
                    return QueryIntent(
                        action=action,
                        parameters=parameters,
                        confidence=0.85,
                        explanation=f"Detected {action} intent from pattern: {pattern}"
                    )
        
        # Fallback to AI classification
        ai_action, confidence = await self._ai_intent_classification(query)
        parameters = await self._extract_enhanced_parameters(query, user_context)
        
        return QueryIntent(
            action=ai_action,
            parameters=parameters,
            confidence=confidence,
            explanation=f"AI classified as {ai_action} with {confidence:.1%} confidence"
        )
    
    async def _extract_enhanced_parameters(self, query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Enhanced parameter extraction with better income and yield detection."""
        parameters = {}
        query_lower = query.lower()
        
        # Enhanced income extraction with better patterns
        income_patterns = [
            r'\$?([\d,]+)\s*(monthly|annually|yearly)?\s*(?:income|month|year)',
            r'(?:need|want|generate)\s*\$?([\d,]+)\s*(monthly|annually|yearly)?',
            r'([\d,]+)\s*dollars?\s*(monthly|annually|yearly)?\s*(?:income|month|year)',
            r'monthly.*\$?([\d,]+)',
            r'annual.*\$?([\d,]+)'
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, query_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                period = match.group(2) if len(match.groups()) > 1 else None
                
                # Convert to annual if monthly
                if period and 'month' in period:
                    amount *= 12
                
                parameters['target_income'] = amount
                logger.info(f"Extracted income target: ${amount:,.0f} annually")
                break
        
        # Enhanced dividend yield extraction
        yield_patterns = [
            r'yield.*?(\d+(?:\.\d+)?)%?',
            r'(\d+(?:\.\d+)?)%?\s*yield',
            r'paying.*?(\d+(?:\.\d+)?)%?',
            r'above.*?(\d+(?:\.\d+)?)%?'
        ]
        
        for pattern in yield_patterns:
            match = re.search(pattern, query_lower)
            if match:
                yield_value = float(match.group(1))
                # Convert to decimal if percentage format
                if yield_value > 1:
                    yield_value = yield_value / 100
                parameters['min_dividend_yield'] = yield_value
                break
        
        # Risk tolerance detection
        if any(term in query_lower for term in ['low risk', 'conservative', 'safe', 'stable']):
            parameters['risk_tolerance'] = 'low'
        elif any(term in query_lower for term in ['high risk', 'aggressive', 'growth']):
            parameters['risk_tolerance'] = 'high'
        else:
            parameters['risk_tolerance'] = 'moderate'
        
        # Investment objectives
        if any(term in query_lower for term in ['growth', 'appreciation', 'capital gains']):
            parameters['objective'] = 'growth'
        elif any(term in query_lower for term in ['income', 'dividend', 'yield']):
            parameters['objective'] = 'income'
        else:
            parameters['objective'] = 'balanced'
        
        # Sector preferences
        sectors = ['technology', 'healthcare', 'finance', 'energy', 'utilities', 'consumer', 'industrial']
        for sector in sectors:
            if sector in query_lower:
                parameters['sector'] = sector.title()
                break
        
        # Extract REAL tickers only - avoid common words
        real_tickers = {
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK.B', 'UNH',
            'JNJ', 'V', 'PG', 'JPM', 'HD', 'CVX', 'MA', 'BAC', 'ABBV', 'PFE', 'AVGO', 'KO',
            'LLY', 'XOM', 'TMO', 'WMT', 'COST', 'DIS', 'DHR', 'VZ', 'MRK', 'ABT', 'NFLX',
            'ADBE', 'NKE', 'CRM', 'TXN', 'NEE', 'ORCL', 'LIN', 'ACN', 'RTX', 'QCOM', 'WFC',
            'PM', 'UPS', 'T', 'HON', 'LOW', 'MS', 'UNP', 'INTU', 'IBM', 'SPGI', 'GS', 'CAT',
            'AMD', 'SCHW', 'PLD', 'BLK', 'AMGN', 'BMY', 'MDT', 'DE', 'ELV', 'GE', 'CI',
            'SO', 'MMM', 'GILD', 'ZTS', 'TJX', 'C', 'MU', 'CVS', 'FIS', 'NOW', 'ISRG',
            'DUK', 'AMT', 'SYK', 'PYPL', 'TMUS', 'AON', 'EQIX', 'APD', 'MDLZ', 'CMG',
            'REGN', 'CL', 'ICE', 'PNC', 'USB', 'ECL', 'NSC', 'FISV', 'EMR', 'MCO'
        }
        
        # Find actual tickers in the query
        words = query.upper().split()
        found_tickers = []
        for word in words:
            clean_word = word.strip('.,!?()[]{}":;')
            if clean_word in real_tickers:
                found_tickers.append(clean_word)
        
        if found_tickers:
            parameters['tickers'] = found_tickers[:3]  # Limit to 3 tickers
        
        return parameters
    
    async def _ai_intent_classification(self, query: str) -> Tuple[str, float]:
        """Use AI to classify unclear queries."""
        try:
            prompt = f"""
            Classify this investment/portfolio query into one of these categories:
            1. screen - Finding stocks based on criteria
            2. optimize - Portfolio optimization/allocation
            3. analyze - Analysis of stocks/portfolios
            4. compare - Comparing investments
            5. recommend - Getting investment recommendations
            
            Query: "{query}"
            
            Respond with just the category name and confidence (0-1) separated by a comma.
            Example: screen,0.85
            """
            
            response = await self.ai_insights._query_llm(prompt)
            
            if ',' in response:
                action, confidence_str = response.strip().split(',')
                return action.strip(), float(confidence_str.strip())
            else:
                return 'unclear', 0.3
                
        except Exception as e:
            logger.warning("AI intent classification failed", error=str(e))
            return 'unclear', 0.3
    
    async def _execute_enhanced_screening(self, intent: QueryIntent, original_query: str) -> QueryResponse:
        """
        FAST & EFFICIENT SCREENING - Quick results without deep analysis
        """
        try:
            logger.info("Executing FAST dividend screening", query=original_query)
            
            # Extract screening criteria quickly
            yield_min = intent.parameters.get('yield_min', 4.0)  # Default 4% minimum
            price_max = intent.parameters.get('price_max', 200.0)  # Default max $200
            sector = intent.parameters.get('sector', None)
            
            # FAST SCREENING - Use pre-defined high-quality dividend stocks
            screening_results = await self._get_fast_dividend_stocks(yield_min, price_max, sector)
            
            if not screening_results:
                return QueryResponse(
                    success=True,
                    data={
                        'screening_results': [],
                        'total_found': 0,
                        'screening_criteria': {
                            'minimum_yield': yield_min,
                            'maximum_price': price_max,
                            'sector_filter': sector
                        }
                    },
                    explanation=f"No dividend stocks found matching your criteria (yield ≥ {yield_min}%). Try lowering the yield requirement or removing sector filters.",
                    suggestions=[
                        "Try a lower yield requirement (e.g., 3%)",
                        "Remove sector filters for broader results",
                        "Look for dividend growth stocks instead",
                        "Consider dividend ETFs for diversification"
                    ]
                )
            
            # Format results for display
            total_found = len(screening_results)
            
            explanation = f"Found {total_found} dividend stocks with yield ≥ {yield_min}%. "
            if sector:
                explanation += f"Filtered by {sector} sector. "
            explanation += "These are established dividend-paying companies with strong track records."
            
            return QueryResponse(
                success=True,
                data={
                    'screening_results': screening_results[:20],  # Limit to top 20
                    'total_found': total_found,
                    'screening_criteria': {
                        'minimum_yield': yield_min,
                        'maximum_price': price_max,
                        'sector_filter': sector
                    },
                    'screening_method': 'fast_curated_list'
                },
                explanation=explanation,
                suggestions=[
                    f"Analyze specific stocks like {screening_results[0]['ticker']} for detailed insights",
                    "Consider dividend growth rates for long-term investing",
                    "Check payout ratios for sustainability",
                    "Diversify across different sectors"
                ],
                confidence=0.9
            )
            
        except Exception as e:
            logger.error("Fast screening failed", error=str(e), query=original_query)
            return QueryResponse(
                success=False,
                data=None,
                explanation="I encountered an error while screening for dividend stocks. Please try rephrasing your request.",
                suggestions=[
                    "Try a simpler query like 'Show me dividend stocks'",
                    "Ask about specific stocks instead",
                    "Request portfolio optimization help"
                ]
            )

    async def _get_fast_dividend_stocks(self, yield_min: float, price_max: float, sector: str = None) -> List[Dict[str, Any]]:
        """
        FAST SCREENING - Pre-curated list of quality dividend stocks
        """
        # Pre-curated dividend stocks with approximate data (updated periodically)
        dividend_stocks = [
            # High-yield dividend stocks
            {'ticker': 'T', 'company_name': 'AT&T Inc.', 'dividend_yield': 6.8, 'current_price': 16.50, 'sector': 'Communication Services', 'market_cap': 118000000000},
            {'ticker': 'VZ', 'company_name': 'Verizon Communications', 'dividend_yield': 6.4, 'current_price': 39.85, 'sector': 'Communication Services', 'market_cap': 167000000000},
            {'ticker': 'KO', 'company_name': 'The Coca-Cola Company', 'dividend_yield': 3.2, 'current_price': 63.50, 'sector': 'Consumer Staples', 'market_cap': 275000000000},
            {'ticker': 'PEP', 'company_name': 'PepsiCo Inc.', 'dividend_yield': 2.8, 'current_price': 169.50, 'sector': 'Consumer Staples', 'market_cap': 234000000000},
            {'ticker': 'JNJ', 'company_name': 'Johnson & Johnson', 'dividend_yield': 3.1, 'current_price': 158.90, 'sector': 'Healthcare', 'market_cap': 416000000000},
            {'ticker': 'PFE', 'company_name': 'Pfizer Inc.', 'dividend_yield': 5.9, 'current_price': 28.50, 'sector': 'Healthcare', 'market_cap': 161000000000},
            {'ticker': 'XOM', 'company_name': 'Exxon Mobil Corporation', 'dividend_yield': 3.4, 'current_price': 117.80, 'sector': 'Energy', 'market_cap': 484000000000},
            {'ticker': 'CVX', 'company_name': 'Chevron Corporation', 'dividend_yield': 3.2, 'current_price': 162.90, 'sector': 'Energy', 'market_cap': 300000000000},
            {'ticker': 'JPM', 'company_name': 'JPMorgan Chase & Co.', 'dividend_yield': 2.1, 'current_price': 223.15, 'sector': 'Financials', 'market_cap': 640000000000},
            {'ticker': 'BAC', 'company_name': 'Bank of America Corp', 'dividend_yield': 2.9, 'current_price': 45.20, 'sector': 'Financials', 'market_cap': 360000000000},
            {'ticker': 'WFC', 'company_name': 'Wells Fargo & Company', 'dividend_yield': 2.8, 'current_price': 61.80, 'sector': 'Financials', 'market_cap': 220000000000},
            {'ticker': 'MSFT', 'company_name': 'Microsoft Corporation', 'dividend_yield': 0.7, 'current_price': 454.50, 'sector': 'Technology', 'market_cap': 3380000000000},
            {'ticker': 'AAPL', 'company_name': 'Apple Inc.', 'dividend_yield': 0.4, 'current_price': 229.00, 'sector': 'Technology', 'market_cap': 3480000000000},
            {'ticker': 'IBM', 'company_name': 'International Business Machines', 'dividend_yield': 3.5, 'current_price': 190.50, 'sector': 'Technology', 'market_cap': 176000000000},
            {'ticker': 'INTC', 'company_name': 'Intel Corporation', 'dividend_yield': 1.8, 'current_price': 20.85, 'sector': 'Technology', 'market_cap': 89000000000},
            {'ticker': 'CSCO', 'company_name': 'Cisco Systems Inc.', 'dividend_yield': 3.0, 'current_price': 58.30, 'sector': 'Technology', 'market_cap': 240000000000},
            {'ticker': 'NEE', 'company_name': 'NextEra Energy Inc.', 'dividend_yield': 2.8, 'current_price': 76.20, 'sector': 'Utilities', 'market_cap': 158000000000},
            {'ticker': 'D', 'company_name': 'Dominion Energy Inc.', 'dividend_yield': 5.1, 'current_price': 56.90, 'sector': 'Utilities', 'market_cap': 46000000000},
            {'ticker': 'SO', 'company_name': 'The Southern Company', 'dividend_yield': 3.7, 'current_price': 88.45, 'sector': 'Utilities', 'market_cap': 96000000000},
            {'ticker': 'DUK', 'company_name': 'Duke Energy Corporation', 'dividend_yield': 3.9, 'current_price': 114.80, 'sector': 'Utilities', 'market_cap': 89000000000},
            {'ticker': 'MMM', 'company_name': '3M Company', 'dividend_yield': 4.8, 'current_price': 132.50, 'sector': 'Industrials', 'market_cap': 74000000000},
            {'ticker': 'CAT', 'company_name': 'Caterpillar Inc.', 'dividend_yield': 1.8, 'current_price': 409.20, 'sector': 'Industrials', 'market_cap': 215000000000},
            {'ticker': 'WM', 'company_name': 'Waste Management Inc.', 'dividend_yield': 1.4, 'current_price': 219.80, 'sector': 'Industrials', 'market_cap': 90000000000},
            {'ticker': 'UNH', 'company_name': 'UnitedHealth Group Inc.', 'dividend_yield': 1.3, 'current_price': 628.90, 'sector': 'Healthcare', 'market_cap': 585000000000},
            {'ticker': 'ABBV', 'company_name': 'AbbVie Inc.', 'dividend_yield': 3.3, 'current_price': 188.50, 'sector': 'Healthcare', 'market_cap': 333000000000},
            {'ticker': 'MRK', 'company_name': 'Merck & Co. Inc.', 'dividend_yield': 2.7, 'current_price': 115.20, 'sector': 'Healthcare', 'market_cap': 292000000000},
            {'ticker': 'AMGN', 'company_name': 'Amgen Inc.', 'dividend_yield': 3.0, 'current_price': 298.50, 'sector': 'Healthcare', 'market_cap': 158000000000},
            {'ticker': 'GILD', 'company_name': 'Gilead Sciences Inc.', 'dividend_yield': 3.8, 'current_price': 80.90, 'sector': 'Healthcare', 'market_cap': 101000000000},
            {'ticker': 'LLY', 'company_name': 'Eli Lilly and Company', 'dividend_yield': 0.6, 'current_price': 898.50, 'sector': 'Healthcare', 'market_cap': 856000000000},
            {'ticker': 'BMY', 'company_name': 'Bristol-Myers Squibb', 'dividend_yield': 4.5, 'current_price': 53.20, 'sector': 'Healthcare', 'market_cap': 111000000000}
        ]
        
        # Apply filters
        filtered_stocks = []
        
        for stock in dividend_stocks:
            # Apply yield filter
            if stock['dividend_yield'] < yield_min:
                continue
                
            # Apply price filter
            if stock['current_price'] > price_max:
                continue
                
            # Apply sector filter
            if sector and sector.lower() not in stock['sector'].lower():
                continue
                
            filtered_stocks.append(stock)
        
        # Sort by dividend yield (highest first)
        filtered_stocks.sort(key=lambda x: x['dividend_yield'], reverse=True)
        
        logger.info(f"Fast screening complete: {len(filtered_stocks)} stocks found")
        return filtered_stocks
    
    async def _execute_optimization(self, intent: QueryIntent, original_query: str) -> QueryResponse:
        """Execute portfolio optimization."""
        try:
            # Extract or default tickers
            tickers = intent.parameters.get('tickers')
            if not tickers:
                # Use suggested dividend stocks if no specific tickers
                tickers = ['AAPL', 'MSFT', 'JNJ', 'PG', 'KO']
            
            # Ensure we have enough tickers
            if len(tickers) < 2:
                return QueryResponse(
                    success=False,
                    data=None,
                    explanation="I need at least 2 stocks to create an optimized portfolio. Please specify more tickers.",
                    suggestions=[
                        "Add more stock tickers to your request",
                        "Ask me to screen for stocks first",
                        "Try: 'optimize a portfolio with AAPL, MSFT, JNJ'"
                    ]
                )
            
            # Create optimization request
            objective = intent.parameters.get('objective', OptimizationObjective.SHARPE_RATIO)
            
            optimization_request = PortfolioOptimizationRequest(
                tickers=tickers,
                objective=objective,
                shrinkage_method=ShrinkageMethod.AUTO,
                max_weight=intent.parameters.get('max_weight', 0.3),
                min_dividend_yield=intent.parameters.get('min_dividend_yield')
            )
            
            # Initialize optimizer and run optimization using existing EPO service
            optimizer = EnhancedPortfolioOptimizer(self.data_provider)
            
            if optimization_request.max_weight:
                optimizer.max_weight = optimization_request.max_weight
            if optimization_request.min_dividend_yield:
                optimizer.min_dividend_yield = optimization_request.min_dividend_yield
            
            result = await optimizer.optimize_dividend_portfolio(
                tickers=optimization_request.tickers,
                objective=optimization_request.objective.value,
                shrinkage_method=optimization_request.shrinkage_method.value
            )
            
            # Format results for response
            optimization_data = {
                'weights': result.weights,
                'expected_return': result.expected_return,
                'volatility': result.volatility,
                'sharpe_ratio': result.sharpe_ratio,
                'expected_dividend_yield': result.expected_dividend_yield,
                'optimization_method': result.optimization_method,
                'tickers_analyzed': tickers
            }
            
            explanation = f"I've optimized a portfolio with {len(tickers)} stocks using the Enhanced Portfolio Optimization method. "
            explanation += f"The portfolio has an expected return of {result.expected_return:.1%} with a Sharpe ratio of {result.sharpe_ratio:.2f}."
            
            return QueryResponse(
                success=True,
                data=optimization_data,
                explanation=explanation,
                suggestions=[
                    "Review the allocation weights carefully",
                    "Consider the risk-return profile",
                    "Ask me to compare with other strategies"
                ],
                visualization_config={
                    'type': 'portfolio_allocation',
                    'chart_type': 'pie',
                    'show_metrics': True,
                    'include_risk_analysis': True
                }
            )
            
        except Exception as e:
            logger.error("Optimization execution failed", error=str(e))
            raise
    
    async def _execute_analysis(self, intent: QueryIntent, original_query: str) -> QueryResponse:
        """Execute analysis of stocks or portfolios."""
        try:
            tickers = intent.parameters.get('tickers', [])
            
            if not tickers:
                return QueryResponse(
                    success=False,
                    data=None,
                    explanation="Please specify which stocks or portfolio you'd like me to analyze.",
                    suggestions=[
                        "Include specific stock tickers in your request",
                        "Try: 'analyze AAPL dividend quality'",
                        "Ask about portfolio risk analysis"
                    ]
                )
            
            analysis_results = {}
            
            for ticker in tickers:
                try:
                    # Get comprehensive company data
                    company_info = await self.data_provider.get_company_info(ticker)
                    
                    # Get comprehensive dividend analysis using existing service
                    try:
                        dividend_analysis = await self.dividend_service.get_comprehensive_dividend_analysis(ticker)
                    except Exception as e:
                        logger.warning(f"Failed to get dividend analysis for {ticker}: {e}")
                        dividend_analysis = {'dividend_yield': company_info.get('dividend_yield', 0)}
                    
                    # Extract meaningful data from comprehensive analysis
                    if isinstance(dividend_analysis, dict) and 'dividend_quality_score' in dividend_analysis:
                        # Use comprehensive analysis
                        raw_quality_score = dividend_analysis.get('dividend_quality_score', {}).get('quality_score', 0)
                        # NORMALIZE: Convert from 0-100 scale to 0-10 scale
                        quality_score = min(10.0, max(0.0, raw_quality_score / 10.0))
                        current_yield = dividend_analysis.get('current_metrics', {}).get('current_yield', 0)
                        
                        # Extract strengths and risks from analysis
                        strengths = []
                        risks = []
                        
                        if current_yield > 3:
                            strengths.append("High dividend yield")
                        if quality_score > 7:
                            strengths.append("Strong dividend quality")
                        if dividend_analysis.get('growth_analytics', {}).get('five_year_cagr', 0) > 5:
                            strengths.append("Strong dividend growth history")
                        
                        if dividend_analysis.get('sustainability_analysis', {}).get('payout_ratio', 0) > 80:
                            risks.append("High payout ratio may limit growth")
                        if dividend_analysis.get('risk_assessment', {}).get('risk_score', 0) > 6:
                            risks.append("Above-average dividend risk")
                        
                    else:
                        # Fallback to simple analysis
                        current_yield = company_info.get('dividend_yield', 0)
                        if current_yield:
                            current_yield = current_yield * 100
                        
                        quality_factors = []
                        yield_score = min(current_yield * 2, 10) if current_yield else 0
                        quality_factors.append(yield_score)
                        
                        pe_ratio = company_info.get('pe_ratio', 25)
                        if pe_ratio and 10 <= pe_ratio <= 20:
                            pe_score = 8
                        elif pe_ratio and 20 < pe_ratio <= 30:
                            pe_score = 6
                        else:
                            pe_score = 4
                        quality_factors.append(pe_score)
                        
                        quality_score = sum(quality_factors) / len(quality_factors) if quality_factors else 5
                        
                        strengths = []
                        risks = []
                        if current_yield > 3:
                            strengths.append("Attractive dividend yield")
                        if current_yield < 1:
                            risks.append("Low dividend yield")
                        
                    # Combine analysis
                    analysis_results[ticker] = {
                        'company_info': company_info,
                        'dividend_analysis': dividend_analysis,
                        'strengths': strengths,
                        'risks': risks,
                        'quality_score': quality_score
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze {ticker}", error=str(e))
                    analysis_results[ticker] = {
                        'error': f"Analysis failed: {str(e)}",
                        'quality_score': 0.0
                    }
            
            explanation = f"I've analyzed {len(tickers)} stock(s) for you. "
            explanation += "The analysis includes dividend quality, valuation metrics, and key strengths/risks."
            
            return QueryResponse(
                success=True,
                data={'analysis_results': analysis_results},
                explanation=explanation,
                suggestions=[
                    "Review the quality scores and key metrics",
                    "Compare these stocks with alternatives",
                    "Ask for specific recommendations based on this analysis"
                ],
                visualization_config={
                    'type': 'analysis_dashboard',
                    'show_quality_scores': True,
                    'include_comparisons': True
                }
            )
            
        except Exception as e:
            logger.error("Analysis execution failed", error=str(e))
            raise
    
    async def _execute_comparison(self, intent: QueryIntent, original_query: str) -> QueryResponse:
        """Execute comparison between stocks or portfolios."""
        # Implementation similar to analysis but with comparative focus
        return QueryResponse(
            success=False,
            data=None,
            explanation="Comparison feature is under development. Please try stock analysis or portfolio optimization instead.",
            suggestions=[
                "Try analyzing individual stocks",
                "Use portfolio optimization to compare allocations",
                "Ask for investment recommendations"
            ]
        )

    async def _execute_etf_recommendation(self, intent: QueryIntent, original_query: str) -> QueryResponse:
        """Execute ETF and dividend fund recommendations."""
        try:
            logger.info("Executing ETF recommendations", query=original_query)
            
            risk_tolerance = intent.parameters.get('risk_tolerance', 'moderate')
            
            # High-quality dividend ETF alternatives
            etf_recommendations = {
                'dividend_etfs': [
                    {
                        'ticker': 'VYM',
                        'name': 'Vanguard High Dividend Yield ETF',
                        'expense_ratio': 0.06,
                        'yield': 2.85,
                        'aum': '50.2B',
                        'focus': 'High dividend yield stocks',
                        'rationale': 'Low-cost exposure to high-dividend stocks with broad diversification'
                    },
                    {
                        'ticker': 'SCHD',
                        'name': 'Schwab US Dividend Equity ETF',
                        'expense_ratio': 0.06,
                        'yield': 3.52,
                        'aum': '35.8B',
                        'focus': 'Dividend quality and growth',
                        'rationale': 'Focus on quality dividend-growing companies with consistent payouts'
                    },
                    {
                        'ticker': 'DVY',
                        'name': 'iShares Select Dividend ETF',
                        'expense_ratio': 0.38,
                        'yield': 3.89,
                        'aum': '20.1B',
                        'focus': 'Dividend track record',
                        'rationale': 'Companies with 5+ years of consecutive dividend payments'
                    }
                ],
                'reit_alternatives': [
                    {
                        'ticker': 'VNQ',
                        'name': 'Vanguard Real Estate ETF',
                        'expense_ratio': 0.12,
                        'yield': 3.75,
                        'aum': '38.5B',
                        'focus': 'Real estate investment trusts',
                        'rationale': 'Broad REIT exposure for real estate income'
                    },
                    {
                        'ticker': 'SPHD',
                        'name': 'Invesco S&P 500 High Dividend Low Volatility ETF',
                        'expense_ratio': 0.30,
                        'yield': 4.25,
                        'aum': '3.2B',
                        'focus': 'High yield with low volatility',
                        'rationale': 'Combines high dividends with reduced volatility'
                    }
                ],
                'income_alternatives': [
                    {
                        'ticker': 'JEPI',
                        'name': 'JPMorgan Equity Premium Income ETF',
                        'expense_ratio': 0.35,
                        'yield': 7.85,
                        'aum': '32.1B',
                        'focus': 'Income through options strategy',
                        'rationale': 'Higher income through covered call strategy'
                    },
                    {
                        'ticker': 'FDVV',
                        'name': 'Fidelity High Dividend ETF',
                        'expense_ratio': 0.29,
                        'yield': 4.15,
                        'aum': '8.5B',
                        'focus': 'Value-oriented dividend stocks',
                        'rationale': 'Focus on undervalued dividend-paying stocks'
                    }
                ]
            }
            
            # Customize recommendations based on risk tolerance
            if risk_tolerance == 'low':
                primary_recommendations = etf_recommendations['dividend_etfs'][:2]
                explanation = "Conservative dividend ETF alternatives focused on stability and consistent income."
            elif risk_tolerance == 'high':
                primary_recommendations = etf_recommendations['income_alternatives']
                explanation = "Higher-yield alternatives that may provide more income but with increased risk."
            else:
                primary_recommendations = etf_recommendations['dividend_etfs']
                explanation = "Balanced dividend ETF alternatives offering good diversification and reasonable yields."
            
            return QueryResponse(
                success=True,
                data={
                    'etf_recommendations': {
                        'primary_recommendations': primary_recommendations,
                        'all_categories': etf_recommendations,
                        'risk_profile': risk_tolerance
                    },
                    'comparison_factors': {
                        'expense_ratios': 'Lower is better (0.06% - 0.38% range)',
                        'yield': 'Current dividend yield (2.85% - 7.85% range)',
                        'aum': 'Assets under management (liquidity indicator)',
                        'focus': 'Investment strategy and holdings focus'
                    }
                },
                explanation=explanation,
                suggestions=[
                    "Compare expense ratios - lower fees mean more money for you",
                    "Consider yield vs. risk - higher yields often mean higher risk",
                    "Look at fund focus - growth vs. income vs. value strategies",
                    "Check fund size (AUM) for liquidity and stability",
                    "Diversify across multiple ETFs for better risk management"
                ],
                confidence=0.95
            )
            
        except Exception as e:
            logger.error("ETF recommendation failed", error=str(e))
            return QueryResponse(
                success=False,
                data=None,
                explanation="I encountered an error generating ETF recommendations. Please try rephrasing your question.",
                suggestions=[
                    "Ask about specific dividend ETFs like VYM or SCHD",
                    "Try asking about dividend investing strategies",
                    "Ask for individual dividend stock recommendations instead"
                ]
            )
    
    async def _execute_enhanced_recommendation(self, intent: QueryIntent, original_query: str) -> QueryResponse:
        """Enhanced recommendation engine with comprehensive backend integration."""
        try:
            # Determine recommendation type based on parameters
            target_income = intent.parameters.get('target_income')
            objective = intent.parameters.get('objective', 'balanced')
            risk_tolerance = intent.parameters.get('risk_tolerance', 'moderate')
            
            if target_income:
                return await self._generate_enhanced_income_recommendations(target_income, risk_tolerance, original_query)
            elif objective in ['growth', 'aggressive']:
                return await self._generate_enhanced_growth_recommendations(objective, risk_tolerance, original_query)
            else:
                return await self._generate_enhanced_general_recommendations(risk_tolerance, original_query)
            
        except Exception as e:
            logger.error("Enhanced recommendation execution failed", error=str(e))
            raise

    async def _generate_enhanced_income_recommendations(self, target_income: float, risk_tolerance: str, original_query: str) -> QueryResponse:
        """Generate enhanced income recommendations using comprehensive backend data."""
        try:
            # Calculate investment requirements with realistic yield expectations
            risk_yield_mapping = {
                'low': {'min_yield': 0.025, 'max_yield': 0.06, 'target_yield': 0.04},      # 2.5-6% yield
                'moderate': {'min_yield': 0.03, 'max_yield': 0.08, 'target_yield': 0.05},  # 3-8% yield  
                'high': {'min_yield': 0.04, 'max_yield': 0.12, 'target_yield': 0.07}      # 4-12% yield
            }
            
            yield_params = risk_yield_mapping.get(risk_tolerance, risk_yield_mapping['moderate'])
            target_yield = yield_params['target_yield']
            required_investment = target_income / target_yield
            
            # Define risk-appropriate stock universe
            risk_stock_mapping = {
                'low': ['JNJ', 'PG', 'KO', 'WMT', 'VZ', 'T', 'XOM', 'CVX', 'MMM', 'CAT'],
                'moderate': ['AAPL', 'MSFT', 'JPM', 'HD', 'PEP', 'ABBV', 'MRK', 'PFE', 'INTC', 'CSCO'],
                'high': ['O', 'MAIN', 'STAG', 'MPW', 'AGNC', 'NLY', 'ARCC', 'PSEC', 'GLAD', 'HTGC']
            }
            
            candidate_tickers = risk_stock_mapping.get(risk_tolerance, risk_stock_mapping['moderate'])
            
            # Analyze candidates using comprehensive backend services
            income_candidates = []
            
            for ticker in candidate_tickers:
                try:
                    # Get comprehensive dividend analysis
                    dividend_analysis = await self.dividend_service.get_comprehensive_dividend_analysis(
                        ticker, include_forecast=False, include_peer_comparison=False
                    )
                    
                    # Get company information
                    company_info = await self.data_provider.get_company_info(ticker)
                    
                    # Extract key metrics
                    current_yield = dividend_analysis.get('current_metrics', {}).get('current_yield', 0) / 100  # Convert to decimal
                    raw_quality_score = dividend_analysis.get('dividend_quality_score', {}).get('quality_score', 0)
                    # NORMALIZE: Convert from 0-100 scale to 0-10 scale
                    quality_score = min(10.0, max(0.0, raw_quality_score / 10.0))
                    sustainability_rating = dividend_analysis.get('sustainability_analysis', {}).get('sustainability_rating', 'Unknown')
                    payout_ratio = dividend_analysis.get('coverage_analysis', {}).get('payout_ratio', 0)
                    
                    # Filter by yield range for risk tolerance
                    if current_yield >= yield_params['min_yield'] and current_yield <= yield_params['max_yield']:
                        # Calculate position size for target income
                        position_size = target_income / current_yield if current_yield > 0 else 0
                        
                        income_candidates.append({
                            'ticker': ticker,
                            'company_name': company_info.get('name', ticker),
                            'dividend_yield': round(current_yield * 100, 2),  # Convert back to percentage
                            'quality_score': round(quality_score, 1),
                            'sustainability_rating': sustainability_rating,
                            'payout_ratio': round(payout_ratio, 1),
                            'estimated_annual_income': round(target_income, 0),
                            'required_investment': round(position_size, 0),
                            'risk_level': risk_tolerance,
                            'sector': company_info.get('sector', 'Unknown'),
                            'current_price': company_info.get('current_price', 0)
                        })
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze {ticker} for income: {e}")
                    continue
            
            # Sort by combination of yield and quality
            income_candidates.sort(key=lambda x: (x['dividend_yield'] * 0.6 + x['quality_score'] * 0.4), reverse=True)
            income_candidates = income_candidates[:10]
            
            if not income_candidates:
                return QueryResponse(
                    success=False,
                    data=None,
                    explanation=f"No suitable dividend stocks found for ${target_income:,.0f} annual income with {risk_tolerance} risk tolerance.",
                    suggestions=[
                        "Consider lowering your income target",
                        "Increase your risk tolerance for higher-yield options",
                        "Explore dividend-focused ETFs",
                        "Consider a longer investment timeline"
                    ]
                )
            
            # Calculate portfolio summary
            avg_yield = sum(stock['dividend_yield'] for stock in income_candidates) / len(income_candidates)
            total_investment_needed = target_income / (avg_yield / 100)
            
            explanation = f"Based on your ${target_income:,.0f} annual income target with {risk_tolerance} risk tolerance, "
            explanation += f"I found {len(income_candidates)} high-quality dividend stocks. "
            explanation += f"You would need approximately ${total_investment_needed:,.0f} invested at {avg_yield:.1f}% average yield."
            
            return QueryResponse(
                success=True,
                data={
                    'income_recommendations': income_candidates,
                    'target_income': target_income,
                    'average_yield': round(avg_yield, 2),
                    'total_investment_needed': round(total_investment_needed, 0),
                    'risk_tolerance': risk_tolerance,
                    'strategy': f'{risk_tolerance} risk dividend income strategy',
                    'data_sources': ['comprehensive_dividend_analysis', 'multi_source_financial_data']
                },
                explanation=explanation,
                suggestions=[
                    "Diversify across multiple stocks to reduce risk",
                    "Review dividend sustainability ratings carefully",
                    "Consider dollar-cost averaging for entry",
                    "Monitor payout ratios for dividend safety",
                    "Use portfolio optimization to determine exact allocations"
                ],
                visualization_config={
                    'type': 'enhanced_income_recommendations',
                    'show_yield_analysis': True,
                    'include_quality_metrics': True,
                    'sector_diversification': True
                }
            )
            
        except Exception as e:
            logger.error("Enhanced income recommendation generation failed", error=str(e))
            raise

    async def _generate_enhanced_growth_recommendations(self, objective: str, risk_tolerance: str, original_query: str) -> QueryResponse:
        """Generate enhanced growth recommendations using comprehensive analysis."""
        try:
            growth_universe = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'CRM', 'SHOP']
            
            growth_candidates = []
            
            for ticker in growth_universe:
                try:
                    # Get comprehensive analysis
                    company_info = await self.data_provider.get_company_info(ticker)
                    
                    # Get financial ratios
                    try:
                        income_statements = await self.data_provider.get_income_statements(ticker, limit=2)
                        balance_sheets = await self.data_provider.get_balance_sheets(ticker, limit=2)
                        
                        if income_statements and balance_sheets:
                            financial_ratios = await self.ratio_calculator.calculate_all_ratios(
                                income_statements, balance_sheets
                            )
                        else:
                            financial_ratios = {}
                    except Exception as e:
                        logger.warning(f"Failed to get financial ratios for {ticker}: {e}")
                        financial_ratios = {}
                    
                    # Try to get dividend info (some growth stocks do pay dividends)
                    try:
                        dividend_analysis = await self.dividend_service.get_comprehensive_dividend_analysis(ticker)
                        current_yield = dividend_analysis.get('current_metrics', {}).get('current_yield', 0)
                        dividend_growth = dividend_analysis.get('growth_analytics', {}).get('cagr_5_year', 0)
                    except:
                        current_yield = 0
                        dividend_growth = 0
                    
                    growth_candidates.append({
                        'ticker': ticker,
                        'company_name': company_info.get('name', ticker),
                        'sector': company_info.get('sector', 'Technology'),
                        'market_cap': company_info.get('market_cap', 0),
                        'current_price': company_info.get('current_price', 0),
                        'pe_ratio': financial_ratios.get('market_ratios', {}).get('pe_ratio'),
                        'roe': financial_ratios.get('profitability_ratios', {}).get('return_on_equity'),
                        'dividend_yield': current_yield,
                        'dividend_growth': dividend_growth,
                        'beta': company_info.get('beta', 1.0),
                        'growth_score': self._calculate_growth_score(company_info, financial_ratios)
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze {ticker} for growth: {e}")
                    continue
            
            # Sort by growth score
            growth_candidates.sort(key=lambda x: x['growth_score'], reverse=True)
            growth_candidates = growth_candidates[:8]
            
            explanation = f"For {objective} investing with {risk_tolerance} risk tolerance, I recommend these growth stocks with strong fundamentals and potential for capital appreciation."
            
            return QueryResponse(
                success=True,
                data={
                    'objective_recommendations': growth_candidates,
                    'investment_objective': objective,
                    'risk_tolerance': risk_tolerance,
                    'strategy': 'Growth-focused with dividend upside potential'
                },
                explanation=explanation,
                suggestions=[
                    "Consider the P/E ratios for valuation",
                    "Monitor beta for volatility assessment", 
                    "Look for dividend growth potential",
                    "Diversify across different growth sectors"
                ]
            )
            
        except Exception as e:
            logger.error("Enhanced growth recommendation generation failed", error=str(e))
            raise

    def _calculate_growth_score(self, company_info: Dict, financial_ratios: Dict) -> float:
        """Calculate a growth score based on multiple factors."""
        score = 0
        
        # Market cap factor (larger companies get slightly lower scores)
        market_cap = company_info.get('market_cap', 0)
        if market_cap > 1e12:  # > $1T
            score += 7
        elif market_cap > 1e11:  # > $100B
            score += 8
        elif market_cap > 1e10:  # > $10B
            score += 9
        else:
            score += 6
        
        # ROE factor
        roe = financial_ratios.get('profitability_ratios', {}).get('return_on_equity', 0)
        if roe and roe > 0.20:  # 20%
            score += 10
        elif roe and roe > 0.15:  # 15%
            score += 8
        elif roe and roe > 0.10:  # 10%
            score += 6
        else:
            score += 3
        
        # PE ratio factor (reasonable valuation)
        pe = financial_ratios.get('market_ratios', {}).get('pe_ratio', 30)
        if pe and 15 <= pe <= 25:
            score += 8
        elif pe and 10 <= pe <= 35:
            score += 6
        else:
            score += 3
        
        return score

    async def _generate_enhanced_general_recommendations(self, risk_tolerance: str, original_query: str) -> QueryResponse:
        """Generate enhanced general recommendations."""
        try:
            # Risk-based portfolio suggestions
            risk_portfolios = {
                'low': {
                    'stocks': ['JNJ', 'PG', 'KO', 'WMT', 'VZ', 'T'],
                    'strategy': 'Conservative dividend aristocrats with consistent payouts',
                    'allocation': 'Conservative: 70% dividend stocks, 20% bonds, 10% REITs',
                    'target_yield': '3-5%'
                },
                'moderate': {
                    'stocks': ['AAPL', 'MSFT', 'JNJ', 'HD', 'PG', 'JPM'],
                    'strategy': 'Balanced dividend growth with capital appreciation',
                    'allocation': 'Balanced: 60% dividend growth, 25% bonds, 15% growth stocks',
                    'target_yield': '2-4%'
                },
                'high': {
                    'stocks': ['GOOGL', 'TSLA', 'NVDA', 'AAPL', 'O', 'MAIN'],
                    'strategy': 'Growth-oriented with high-yield opportunities',
                    'allocation': 'Aggressive: 50% growth stocks, 30% high-yield, 20% alternatives',
                    'target_yield': '4-8%'
                }
            }
            
            risk_key = risk_tolerance if risk_tolerance in risk_portfolios else 'moderate'
            portfolio = risk_portfolios[risk_key]
            
            # Analyze the recommended stocks
            recommendations = []
            for ticker in portfolio['stocks']:
                try:
                    company_info = await self.data_provider.get_company_info(ticker)
                    
                    try:
                        dividend_analysis = await self.dividend_service.get_comprehensive_dividend_analysis(ticker)
                        current_yield = dividend_analysis.get('current_metrics', {}).get('current_yield', 0)
                        raw_quality_score = dividend_analysis.get('dividend_quality_score', {}).get('quality_score', 0)
                        # NORMALIZE: Convert from 0-100 scale to 0-10 scale
                        quality_score = min(10.0, max(0.0, raw_quality_score / 10.0))
                    except:
                        current_yield = 0
                        quality_score = 0
                    
                    recommendations.append({
                        'ticker': ticker,
                        'company_name': company_info.get('name', ticker),
                        'sector': company_info.get('sector', 'Unknown'),
                        'current_price': company_info.get('current_price', 0),
                        'dividend_yield': current_yield,
                        'quality_score': quality_score,
                        'market_cap': company_info.get('market_cap', 0),
                        'rationale': f"Strong {risk_tolerance} risk investment in {company_info.get('sector', 'this')} sector"
                    })
                except Exception as e:
                    logger.warning(f"Failed to analyze {ticker}: {e}")
                    continue
            
            return QueryResponse(
                success=True,
                data={
                    'general_recommendations': {
                        'recommended_stocks': recommendations,
                        'strategy': portfolio['strategy'],
                        'allocation_guidance': portfolio['allocation'],
                        'target_yield_range': portfolio['target_yield'],
                        'risk_level': risk_tolerance
                    }
                },
                explanation=f"Based on your {risk_tolerance} risk tolerance, {portfolio['strategy'].lower()}.",
                suggestions=[
                    "Start with 2-3 positions and build gradually",
                    "Use dollar-cost averaging for market entry",
                    "Rebalance quarterly to maintain target allocation",
                    "Consider tax implications in taxable accounts",
                    "Review and adjust based on market conditions"
                ]
            )
            
        except Exception as e:
            logger.error("Enhanced general recommendation generation failed", error=str(e))
            raise

    async def _enhance_response_with_backend_ai(self, response: QueryResponse, original_query: str, intent: QueryIntent) -> QueryResponse:
        """Enhanced AI insights using comprehensive backend data and Gemini integration."""
        try:
            if not response.success or not response.data:
                return response
            
            # Extract relevant data for AI enhancement
            context_data = {
                'query': original_query,
                'intent': intent.action,
                'data_summary': self._summarize_data_for_ai(response.data),
                'data_sources': ['yfinance', 'alpha_vantage', 'fmp', 'fred'],
                'analysis_type': 'comprehensive_multi_source'
            }
            
            # Generate AI insights using the available AI service
            ai_prompt = f"""
            The user asked: "{original_query}"
            
            We executed a {intent.action} operation with the following results:
            {context_data['data_summary']}
            
            Based on this comprehensive financial analysis from multiple data sources (YFinance, Alpha Vantage, FMP, FRED), 
            provide 2-3 additional insights or recommendations that would be valuable to the user.
            
            Keep it concise and actionable. Focus on what they should know or do next.
            Consider dividend sustainability, risk factors, and market conditions.
            """
            
            try:
                ai_insights = await self.ai_insights._query_llm(ai_prompt)
                if ai_insights and len(ai_insights.strip()) > 10:
                    enhanced_explanation = response.explanation + "\n\n💡 AI Insights: " + ai_insights.strip()
                    response.explanation = enhanced_explanation
            except Exception as e:
                logger.warning(f"AI enhancement failed: {e}")
                # Continue without AI enhancement
            
            return response
            
        except Exception as e:
            logger.warning("AI enhancement failed, returning original response", error=str(e))
            return response

    def _summarize_data_for_ai(self, data: Dict[str, Any]) -> str:
        """Summarize response data for AI context."""
        summary_parts = []
        
        if 'screening_results' in data:
            count = len(data['screening_results'])
            summary_parts.append(f"Found {count} stocks in screening")
            
        if 'income_recommendations' in data:
            count = len(data['income_recommendations'])
            target = data.get('target_income', 0)
            summary_parts.append(f"Generated {count} income stocks for ${target:,.0f} target")
            
        if 'analysis_results' in data:
            tickers = [result['ticker'] for result in data['analysis_results']]
            summary_parts.append(f"Analyzed stocks: {', '.join(tickers)}")
            
        if 'objective_recommendations' in data:
            count = len(data['objective_recommendations'])
            objective = data.get('investment_objective', 'general')
            summary_parts.append(f"Generated {count} {objective} recommendations")
        
        return "; ".join(summary_parts) if summary_parts else "Financial analysis completed"

    async def _handle_unclear_query(self, query: str) -> QueryResponse:
        """Handle queries where intent is unclear."""
        return QueryResponse(
            success=False,
            data=None,
            explanation="I'm not sure exactly what you're looking for. Could you be more specific?",
            suggestions=[
                "Try: 'Find dividend stocks with yield above 4%'",
                "Try: 'Optimize a portfolio with AAPL, MSFT, JNJ'",
                "Try: 'Analyze AAPL dividend quality'",
                "Include specific stock tickers or criteria"
            ],
            confidence=0.0
        ) 
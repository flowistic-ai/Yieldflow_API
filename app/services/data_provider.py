import asyncio
import aiohttp
import yfinance as yf
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date, timedelta
import pandas as pd
import structlog
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.timeseries import TimeSeries

from app.core.config import settings
from app.utils.exceptions import DataSourceError, TickerNotFoundError, ValidationError
from app.services.cache_service import CacheService

logger = structlog.get_logger()


class DataProvider:
    """Multi-source financial data provider with cross-validation and fallback"""
    
    def __init__(self):
        self.cache_service = CacheService()
        
        # API Configuration
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.fmp_key = settings.FMP_API_KEY if settings.FMP_API_KEY else "demo"
        self.polygon_key = getattr(settings, 'POLYGON_API_KEY', None)
        self.twelvedata_key = getattr(settings, 'TWELVEDATA_API_KEY', None)
        self.iex_key = getattr(settings, 'IEX_CLOUD_API_KEY', None)
        self.quandl_key = getattr(settings, 'QUANDL_API_KEY', None)
        self.eod_key = getattr(settings, 'EOD_HISTORICAL_API_KEY', None)
        
        # Initialize Alpha Vantage clients
        if self.alpha_vantage_key:
            self.av_fundamental = FundamentalData(key=self.alpha_vantage_key, output_format='pandas')
            self.av_timeseries = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
        
        # API Base URLs
        self.fmp_base_url = "https://financialmodelingprep.com/api/v3"
        self.polygon_base_url = "https://api.polygon.io"
        self.twelvedata_base_url = "https://api.twelvedata.com"
        self.iex_base_url = "https://cloud.iexapis.com/stable"
        self.eod_base_url = "https://eodhd.com/api"
        
        # Data source priority ranking (higher is better)
        self.source_reliability = {
            'alpha_vantage': 0.95,    # Official NASDAQ vendor
            'financial_modeling_prep': 0.90,  # SEC data source
            'polygon': 0.85,          # High-quality institutional data
            'twelvedata': 0.80,       # Good coverage and accuracy
            'iex_cloud': 0.85,        # Previously reliable until shutdown
            'eod_historical': 0.80,   # Good for historical data
            'yahoo_finance': 0.75,    # Free but sometimes inconsistent
            'quandl': 0.90           # High-quality for specific datasets
        }
    
    async def get_company_info(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive company information from multiple sources"""
        
        # Check cache first
        cached_data = await self.cache_service.get_static_data(f"company_info_{ticker}")
        if cached_data:
            return cached_data
        
        company_data = {}
        
        try:
            # Primary source: yfinance (free and comprehensive)
            yf_data = await self._get_yfinance_company_info(ticker)
            if yf_data:
                company_data.update(yf_data)
            
            # Secondary source: Alpha Vantage (for additional details)
            av_data = await self._get_alpha_vantage_company_info(ticker)
            if av_data:
                company_data.update(av_data)
            
            # Tertiary source: Financial Modeling Prep (if available)
            if self.fmp_key:
                fmp_data = await self._get_fmp_company_info(ticker)
                if fmp_data:
                    company_data.update(fmp_data)
            
            if not company_data:
                raise TickerNotFoundError(ticker)
            
            # Standardize and validate data
            standardized_data = self._standardize_company_data(company_data, ticker)
            
            # Cache the result
            await self.cache_service.cache_static_data(f"company_info_{ticker}", standardized_data)
            
            return standardized_data
            
        except Exception as e:
            logger.error("Error fetching company info", ticker=ticker, error=str(e))
            if isinstance(e, TickerNotFoundError):
                raise e
            raise DataSourceError(f"Failed to fetch company info: {str(e)}", "multi_source")
    
    async def get_income_statements(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 4,
        period_gte: Optional[date] = None,
        period_lte: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get income statements from multiple sources with cross-validation"""
        
        cache_key = f"income_statements_{ticker}_{period}_{limit}"
        cached_data = await self.cache_service.get_financial_data(ticker, f"income_{period}")
        if cached_data:
            return cached_data.get('income_statements', [])
        
        try:
            statements = []
            
            # Primary source: Alpha Vantage
            av_statements = await self._get_alpha_vantage_income_statements(ticker, period)
            
            # Secondary source: yfinance
            yf_statements = await self._get_yfinance_income_statements(ticker, period)
            
            # Tertiary source: Financial Modeling Prep
            fmp_statements = []
            if self.fmp_key:
                fmp_statements = await self._get_fmp_income_statements(ticker, period)
            
            # Use the enhanced merging logic (backward compatible for now)
            statements = self._merge_income_statements(av_statements, yf_statements, fmp_statements)
            
            # Apply filters
            statements = self._filter_statements_by_date(statements, period_gte, period_lte)
            statements = statements[:limit] if limit else statements
            
            return statements
            
        except Exception as e:
            logger.error("Error fetching income statements", ticker=ticker, error=str(e))
            raise DataSourceError(f"Failed to fetch income statements: {str(e)}", "multi_source")
    
    async def get_balance_sheets(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 4,
        period_gte: Optional[date] = None,
        period_lte: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get balance sheets from multiple sources"""
        
        try:
            statements = []
            
            # Primary source: Alpha Vantage
            av_statements = await self._get_alpha_vantage_balance_sheets(ticker, period)
            
            # Secondary source: yfinance
            yf_statements = await self._get_yfinance_balance_sheets(ticker, period)
            
            # Tertiary source: Financial Modeling Prep
            fmp_statements = []
            if self.fmp_key:
                fmp_statements = await self._get_fmp_balance_sheets(ticker, period)
            
            # Cross-validate and merge data
            statements = self._merge_balance_sheets(av_statements, yf_statements, fmp_statements)
            
            # Apply filters
            statements = self._filter_statements_by_date(statements, period_gte, period_lte)
            statements = statements[:limit] if limit else statements
            
            return statements
            
        except Exception as e:
            logger.error("Error fetching balance sheets", ticker=ticker, error=str(e))
            raise DataSourceError(f"Failed to fetch balance sheets: {str(e)}", "multi_source")
    
    async def get_cash_flows(
        self,
        ticker: str,
        period: str = "annual",
        limit: int = 4,
        period_gte: Optional[date] = None,
        period_lte: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """Get cash flow statements from multiple sources"""
        
        try:
            statements = []
            
            # Primary source: Alpha Vantage
            av_statements = await self._get_alpha_vantage_cash_flows(ticker, period)
            
            # Secondary source: yfinance
            yf_statements = await self._get_yfinance_cash_flows(ticker, period)
            
            # Tertiary source: Financial Modeling Prep
            fmp_statements = []
            if self.fmp_key:
                fmp_statements = await self._get_fmp_cash_flows(ticker, period)
            
            # Cross-validate and merge data
            statements = self._merge_cash_flows(av_statements, yf_statements, fmp_statements)
            
            # Apply filters
            statements = self._filter_statements_by_date(statements, period_gte, period_lte)
            statements = statements[:limit] if limit else statements
            
            return statements
            
        except Exception as e:
            logger.error("Error fetching cash flows", ticker=ticker, error=str(e))
            raise DataSourceError(f"Failed to fetch cash flows: {str(e)}", "multi_source")
    
    # Alpha Vantage implementations
    async def _get_alpha_vantage_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetch company overview from Alpha Vantage"""
        try:
            data, _ = self.av_fundamental.get_company_overview(symbol=ticker)
            if data.empty:
                return {}
            
            company_data = data.iloc[0].to_dict()
            return {
                'name': company_data.get('Name', ''),
                'exchange': company_data.get('Exchange', ''),
                'sector': company_data.get('Sector', ''),
                'industry': company_data.get('Industry', ''),
                'country': company_data.get('Country', ''),
                'currency': company_data.get('Currency', ''),
                'market_cap': self._safe_float(company_data.get('MarketCapitalization')),
                'description': company_data.get('Description', ''),
                'employees': self._safe_int(company_data.get('FullTimeEmployees')),
                'data_source': 'alpha_vantage'
            }
        except Exception as e:
            logger.warning("Alpha Vantage company info failed", ticker=ticker, error=str(e))
            return {}
    
    async def _get_alpha_vantage_income_statements(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch income statements from Alpha Vantage"""
        try:
            if period == "quarterly":
                data, _ = self.av_fundamental.get_income_statement_quarterly(symbol=ticker)
            else:
                data, _ = self.av_fundamental.get_income_statement_annual(symbol=ticker)
            
            if data.empty:
                return []
            
            statements = []
            for _, row in data.iterrows():
                statement = {
                    'period_ending': self._parse_date(row.get('fiscalDateEnding')),
                    'period_type': period,
                    'fiscal_year': self._extract_year(row.get('fiscalDateEnding')),
                    'revenue': self._safe_float(row.get('totalRevenue')),
                    'cost_of_revenue': self._safe_float(row.get('costOfRevenue')),
                    'gross_profit': self._safe_float(row.get('grossProfit')),
                    'operating_expenses': self._safe_float(row.get('totalOperatingExpenses')),
                    'operating_income': self._safe_float(row.get('operatingIncome')),
                    'interest_expense': self._safe_float(row.get('interestExpense')),
                    'pretax_income': self._safe_float(row.get('incomeBeforeTax')),
                    'income_tax_expense': self._safe_float(row.get('incomeTaxExpense')),
                    'net_income': self._safe_float(row.get('netIncome')),
                    'data_source': 'alpha_vantage',
                    'confidence_score': 0.9
                }
                statements.append(statement)
            
            return statements
            
        except Exception as e:
            logger.warning("Alpha Vantage income statements failed", ticker=ticker, error=str(e))
            return []
    
    async def _get_alpha_vantage_balance_sheets(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch balance sheets from Alpha Vantage"""
        try:
            if period == "quarterly":
                data, _ = self.av_fundamental.get_balance_sheet_quarterly(symbol=ticker)
            else:
                data, _ = self.av_fundamental.get_balance_sheet_annual(symbol=ticker)
            
            if data.empty:
                return []
            
            statements = []
            for _, row in data.iterrows():
                statement = {
                    'period_ending': self._parse_date(row.get('fiscalDateEnding')),
                    'period_type': period,
                    'fiscal_year': self._extract_year(row.get('fiscalDateEnding')),
                    'cash_and_equivalents': self._safe_float(row.get('cashAndCashEquivalentsAtCarryingValue')),
                    'accounts_receivable': self._safe_float(row.get('currentNetReceivables')),
                    'inventory': self._safe_float(row.get('inventory')),
                    'current_assets': self._safe_float(row.get('totalCurrentAssets')),
                    'property_plant_equipment': self._safe_float(row.get('propertyPlantEquipment')),
                    'goodwill': self._safe_float(row.get('goodwill')),
                    'intangible_assets': self._safe_float(row.get('intangibleAssets')),
                    'total_assets': self._safe_float(row.get('totalAssets')),
                    'accounts_payable': self._safe_float(row.get('accountsPayable')),
                    'short_term_debt': self._safe_float(row.get('shortTermDebt')),
                    'current_liabilities': self._safe_float(row.get('totalCurrentLiabilities')),
                    'long_term_debt': self._safe_float(row.get('longTermDebt')),
                    'total_liabilities': self._safe_float(row.get('totalLiabilities')),
                    'shareholders_equity': self._safe_float(row.get('totalShareholderEquity')),
                    'retained_earnings': self._safe_float(row.get('retainedEarnings')),
                    'data_source': 'alpha_vantage',
                    'confidence_score': 0.9
                }
                statements.append(statement)
            
            return statements
            
        except Exception as e:
            logger.warning("Alpha Vantage balance sheets failed", ticker=ticker, error=str(e))
            return []
    
    async def _get_alpha_vantage_cash_flows(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch cash flows from Alpha Vantage"""
        try:
            if period == "quarterly":
                data, _ = self.av_fundamental.get_cash_flow_quarterly(symbol=ticker)
            else:
                data, _ = self.av_fundamental.get_cash_flow_annual(symbol=ticker)
            
            if data.empty:
                return []
            
            statements = []
            for _, row in data.iterrows():
                statement = {
                    'period_ending': self._parse_date(row.get('fiscalDateEnding')),
                    'period_type': period,
                    'fiscal_year': self._extract_year(row.get('fiscalDateEnding')),
                    'net_income': self._safe_float(row.get('netIncome')),
                    'depreciation_amortization': self._safe_float(row.get('depreciationDepletionAndAmortization')),
                    'operating_cash_flow': self._safe_float(row.get('operatingCashflow')),
                    'capital_expenditures': self._safe_float(row.get('capitalExpenditures')),
                    'investing_cash_flow': self._safe_float(row.get('cashflowFromInvestment')),
                    'financing_cash_flow': self._safe_float(row.get('cashflowFromFinancing')),
                    'net_change_in_cash': self._safe_float(row.get('changeInCashAndCashEquivalents')),
                    'data_source': 'alpha_vantage',
                    'confidence_score': 0.9
                }
                statements.append(statement)
            
            return statements
            
        except Exception as e:
            logger.warning("Alpha Vantage cash flows failed", ticker=ticker, error=str(e))
            return []
    
    # Yahoo Finance implementations
    async def _get_yfinance_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetch company info from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'name': info.get('longName', info.get('shortName', '')),
                'exchange': info.get('exchange', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'country': info.get('country', ''),
                'currency': info.get('currency', ''),
                'market_cap': info.get('marketCap'),
                'employees': info.get('fullTimeEmployees'),
                'description': info.get('longBusinessSummary', ''),
                'website': info.get('website', ''),
                'data_source': 'yahoo_finance'
            }
        except Exception as e:
            logger.warning("Yahoo Finance company info failed", ticker=ticker, error=str(e))
            return {}
    
    async def _get_yfinance_income_statements(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch income statements from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            
            if period == "quarterly":
                data = stock.quarterly_financials
            else:
                data = stock.financials
            
            if data.empty:
                return []
            
            statements = []
            for date_col in data.columns:
                statement = {
                    'period_ending': date_col.date() if hasattr(date_col, 'date') else date_col,
                    'period_type': period,
                    'fiscal_year': date_col.year if hasattr(date_col, 'year') else None,
                    'revenue': self._safe_float(data.loc['Total Revenue', date_col]) if 'Total Revenue' in data.index else None,
                    'cost_of_revenue': self._safe_float(data.loc['Cost Of Revenue', date_col]) if 'Cost Of Revenue' in data.index else None,
                    'gross_profit': self._safe_float(data.loc['Gross Profit', date_col]) if 'Gross Profit' in data.index else None,
                    'operating_income': self._safe_float(data.loc['Operating Income', date_col]) if 'Operating Income' in data.index else None,
                    'net_income': self._safe_float(data.loc['Net Income', date_col]) if 'Net Income' in data.index else None,
                    'data_source': 'yahoo_finance',
                    'confidence_score': 0.8
                }
                statements.append(statement)
            
            return statements
            
        except Exception as e:
            logger.warning("Yahoo Finance income statements failed", ticker=ticker, error=str(e))
            return []
    
    async def _get_yfinance_balance_sheets(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch balance sheets from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            
            if period == "quarterly":
                data = stock.quarterly_balance_sheet
            else:
                data = stock.balance_sheet
            
            if data.empty:
                return []
            
            statements = []
            for date_col in data.columns:
                statement = {
                    'period_ending': date_col.date() if hasattr(date_col, 'date') else date_col,
                    'period_type': period,
                    'fiscal_year': date_col.year if hasattr(date_col, 'year') else None,
                    'cash_and_equivalents': self._safe_float(data.loc['Cash And Cash Equivalents', date_col]) if 'Cash And Cash Equivalents' in data.index else None,
                    'total_assets': self._safe_float(data.loc['Total Assets', date_col]) if 'Total Assets' in data.index else None,
                    'current_assets': self._safe_float(data.loc['Current Assets', date_col]) if 'Current Assets' in data.index else None,
                    'current_liabilities': self._safe_float(data.loc['Current Liabilities', date_col]) if 'Current Liabilities' in data.index else None,
                    'total_liabilities': self._safe_float(data.loc['Total Liabilities Net Minority Interest', date_col]) if 'Total Liabilities Net Minority Interest' in data.index else None,
                    'shareholders_equity': self._safe_float(data.loc['Stockholders Equity', date_col]) if 'Stockholders Equity' in data.index else None,
                    'data_source': 'yahoo_finance',
                    'confidence_score': 0.8
                }
                statements.append(statement)
            
            return statements
            
        except Exception as e:
            logger.warning("Yahoo Finance balance sheets failed", ticker=ticker, error=str(e))
            return []
    
    async def _get_yfinance_cash_flows(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch cash flows from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            
            if period == "quarterly":
                data = stock.quarterly_cashflow
            else:
                data = stock.cashflow
            
            if data.empty:
                return []
            
            statements = []
            for date_col in data.columns:
                statement = {
                    'period_ending': date_col.date() if hasattr(date_col, 'date') else date_col,
                    'period_type': period,
                    'fiscal_year': date_col.year if hasattr(date_col, 'year') else None,
                    'operating_cash_flow': self._safe_float(data.loc['Operating Cash Flow', date_col]) if 'Operating Cash Flow' in data.index else None,
                    'investing_cash_flow': self._safe_float(data.loc['Investing Cash Flow', date_col]) if 'Investing Cash Flow' in data.index else None,
                    'financing_cash_flow': self._safe_float(data.loc['Financing Cash Flow', date_col]) if 'Financing Cash Flow' in data.index else None,
                    'net_change_in_cash': self._safe_float(data.loc['Changes In Cash', date_col]) if 'Changes In Cash' in data.index else None,
                    'capital_expenditures': self._safe_float(data.loc['Capital Expenditure', date_col]) if 'Capital Expenditure' in data.index else None,
                    'data_source': 'yahoo_finance',
                    'confidence_score': 0.8
                }
                statements.append(statement)
            
            return statements
            
        except Exception as e:
            logger.warning("Yahoo Finance cash flows failed", ticker=ticker, error=str(e))
            return []
    
    # Financial Modeling Prep implementations
    async def _get_fmp_company_info(self, ticker: str) -> Dict[str, Any]:
        """Fetch company info from Financial Modeling Prep"""
        if not self.fmp_key:
            return {}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.fmp_base_url}/profile/{ticker}"
                params = {"apikey": self.fmp_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data and len(data) > 0:
                            company = data[0]
                            return {
                                'name': company.get('companyName', ''),
                                'exchange': company.get('exchangeShortName', ''),
                                'sector': company.get('sector', ''),
                                'industry': company.get('industry', ''),
                                'country': company.get('country', ''),
                                'currency': company.get('currency', ''),
                                'market_cap': company.get('mktCap'),
                                'employees': company.get('fullTimeEmployees'),
                                'description': company.get('description', ''),
                                'website': company.get('website', ''),
                                'data_source': 'financial_modeling_prep'
                            }
        except Exception as e:
            logger.warning("FMP company info failed", ticker=ticker, error=str(e))
        
        return {}
    
    async def _get_fmp_income_statements(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch income statements from Financial Modeling Prep"""
        if not self.fmp_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.fmp_base_url}/income-statement/{ticker}"
                params = {
                    "apikey": self.fmp_key,
                    "period": "quarter" if period == "quarterly" else "annual",
                    "limit": 10
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        statements = []
                        
                        for stmt in data:
                            statement = {
                                'period_ending': self._parse_date(stmt.get('date')),
                                'period_type': period,
                                'fiscal_year': self._extract_year(stmt.get('date')),
                                'revenue': self._safe_float(stmt.get('revenue')),
                                'cost_of_revenue': self._safe_float(stmt.get('costOfRevenue')),
                                'gross_profit': self._safe_float(stmt.get('grossProfit')),
                                'operating_expenses': self._safe_float(stmt.get('operatingExpenses')),
                                'operating_income': self._safe_float(stmt.get('operatingIncome')),
                                'interest_expense': self._safe_float(stmt.get('interestExpense')),
                                'pretax_income': self._safe_float(stmt.get('incomeBeforeTax')),
                                'income_tax_expense': self._safe_float(stmt.get('incomeTaxExpense')),
                                'net_income': self._safe_float(stmt.get('netIncome')),
                                'data_source': 'financial_modeling_prep',
                                'confidence_score': 0.9
                            }
                            statements.append(statement)
                        
                        return statements
        except Exception as e:
            logger.warning("FMP income statements failed", ticker=ticker, error=str(e))
        
        return []
    
    async def _get_fmp_balance_sheets(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch balance sheets from Financial Modeling Prep"""
        if not self.fmp_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.fmp_base_url}/balance-sheet-statement/{ticker}"
                params = {
                    "apikey": self.fmp_key,
                    "period": "quarter" if period == "quarterly" else "annual",
                    "limit": 10
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        statements = []
                        
                        for stmt in data:
                            statement = {
                                'period_ending': self._parse_date(stmt.get('date')),
                                'period_type': period,
                                'fiscal_year': self._extract_year(stmt.get('date')),
                                'cash_and_equivalents': self._safe_float(stmt.get('cashAndCashEquivalents')),
                                'accounts_receivable': self._safe_float(stmt.get('netReceivables')),
                                'inventory': self._safe_float(stmt.get('inventory')),
                                'current_assets': self._safe_float(stmt.get('totalCurrentAssets')),
                                'property_plant_equipment': self._safe_float(stmt.get('propertyPlantEquipmentNet')),
                                'goodwill': self._safe_float(stmt.get('goodwill')),
                                'intangible_assets': self._safe_float(stmt.get('intangibleAssets')),
                                'total_assets': self._safe_float(stmt.get('totalAssets')),
                                'accounts_payable': self._safe_float(stmt.get('accountPayables')),
                                'short_term_debt': self._safe_float(stmt.get('shortTermDebt')),
                                'current_liabilities': self._safe_float(stmt.get('totalCurrentLiabilities')),
                                'long_term_debt': self._safe_float(stmt.get('longTermDebt')),
                                'total_liabilities': self._safe_float(stmt.get('totalLiabilities')),
                                'shareholders_equity': self._safe_float(stmt.get('totalShareholdersEquity')),
                                'retained_earnings': self._safe_float(stmt.get('retainedEarnings')),
                                'data_source': 'financial_modeling_prep',
                                'confidence_score': 0.9
                            }
                            statements.append(statement)
                        
                        return statements
        except Exception as e:
            logger.warning("FMP balance sheets failed", ticker=ticker, error=str(e))
        
        return []
    
    async def _get_fmp_cash_flows(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch cash flows from Financial Modeling Prep"""
        if not self.fmp_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.fmp_base_url}/cash-flow-statement/{ticker}"
                params = {
                    "apikey": self.fmp_key,
                    "period": "quarter" if period == "quarterly" else "annual",
                    "limit": 10
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        statements = []
                        
                        for stmt in data:
                            statement = {
                                'period_ending': self._parse_date(stmt.get('date')),
                                'period_type': period,
                                'fiscal_year': self._extract_year(stmt.get('date')),
                                'net_income': self._safe_float(stmt.get('netIncome')),
                                'depreciation_amortization': self._safe_float(stmt.get('depreciationAndAmortization')),
                                'operating_cash_flow': self._safe_float(stmt.get('operatingCashFlow')),
                                'capital_expenditures': self._safe_float(stmt.get('capitalExpenditure')),
                                'investing_cash_flow': self._safe_float(stmt.get('netCashUsedForInvestingActivities')),
                                'financing_cash_flow': self._safe_float(stmt.get('netCashUsedProvidedByFinancingActivities')),
                                'net_change_in_cash': self._safe_float(stmt.get('netChangeInCash')),
                                'data_source': 'financial_modeling_prep',
                                'confidence_score': 0.9
                            }
                            statements.append(statement)
                        
                        return statements
        except Exception as e:
            logger.warning("FMP cash flows failed", ticker=ticker, error=str(e))
        
        return []
    
    # Additional Premium Data Sources for Enhanced Accuracy
    async def _get_polygon_income_statements(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch income statements from Polygon.io (premium institutional data)"""
        if not self.polygon_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Polygon uses different endpoint structure
                url = f"{self.polygon_base_url}/vX/reference/financials"
                params = {
                    "ticker": ticker,
                    "timeframe": "annual" if period == "annual" else "quarterly",
                    "limit": 10,
                    "apikey": self.polygon_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        statements = []
                        
                        for result in data.get('results', []):
                            financials = result.get('financials', {})
                            income_statement = financials.get('income_statement', {})
                            
                            statement = {
                                'period_ending': self._parse_date(result.get('end_date')),
                                'period_type': period,
                                'fiscal_year': self._extract_year(result.get('end_date')),
                                'total_revenue': self._safe_float(income_statement.get('revenues', {}).get('value')),
                                'cost_of_revenue': self._safe_float(income_statement.get('cost_of_revenue', {}).get('value')),
                                'gross_profit': self._safe_float(income_statement.get('gross_profit', {}).get('value')),
                                'operating_expense': self._safe_float(income_statement.get('operating_expenses', {}).get('value')),
                                'operating_income': self._safe_float(income_statement.get('operating_income_loss', {}).get('value')),
                                'net_income': self._safe_float(income_statement.get('net_income_loss', {}).get('value')),
                                'eps_basic': self._safe_float(income_statement.get('basic_earnings_per_share', {}).get('value')),
                                'eps_diluted': self._safe_float(income_statement.get('diluted_earnings_per_share', {}).get('value')),
                                'data_source': 'polygon',
                                'confidence_score': self.source_reliability['polygon']
                            }
                            statements.append(statement)
                        
                        logger.info("Polygon income statements fetched", ticker=ticker, count=len(statements))
                        return statements
        except Exception as e:
            logger.warning("Polygon income statements failed", ticker=ticker, error=str(e))
        
        return []
    
    async def _get_twelvedata_income_statements(self, ticker: str, period: str) -> List[Dict[str, Any]]:
        """Fetch income statements from TwelveData (good coverage and accuracy)"""
        if not self.twelvedata_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.twelvedata_base_url}/income_statement"
                params = {
                    "symbol": ticker,
                    "period": period,
                    "apikey": self.twelvedata_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        statements = []
                        
                        for stmt in data.get('income_statements', []):
                            statement = {
                                'period_ending': self._parse_date(stmt.get('fiscal_date_ending')),
                                'period_type': period,
                                'fiscal_year': self._extract_year(stmt.get('fiscal_date_ending')),
                                'total_revenue': self._safe_float(stmt.get('total_revenue')),
                                'cost_of_revenue': self._safe_float(stmt.get('cost_of_revenue')),
                                'gross_profit': self._safe_float(stmt.get('gross_profit')),
                                'operating_expense': self._safe_float(stmt.get('total_operating_expense')),
                                'operating_income': self._safe_float(stmt.get('operating_income')),
                                'net_income': self._safe_float(stmt.get('net_income')),
                                'eps_basic': self._safe_float(stmt.get('earnings_per_share')),
                                'data_source': 'twelvedata',
                                'confidence_score': self.source_reliability['twelvedata']
                            }
                            statements.append(statement)
                        
                        logger.info("TwelveData income statements fetched", ticker=ticker, count=len(statements))
                        return statements
        except Exception as e:
            logger.warning("TwelveData income statements failed", ticker=ticker, error=str(e))
        
        return []
    
    # Enhanced data merging with weighted confidence scoring
    def _merge_income_statements_enhanced(self, av_data: List, yf_data: List, fmp_data: List, 
                                        polygon_data: List, twelvedata_data: List) -> List[Dict[str, Any]]:
        """Enhanced merge with weighted confidence scoring and cross-validation"""
        all_sources = [
            (av_data, 'alpha_vantage'),
            (fmp_data, 'financial_modeling_prep'),
            (polygon_data, 'polygon'),
            (twelvedata_data, 'twelvedata'),
            (yf_data, 'yahoo_finance')  # Yahoo Finance as fallback
        ]
        
        merged_statements = []
        
        # Group all statements by fiscal period
        period_groups = {}
        
        for source_data, source_name in all_sources:
            for stmt in source_data:
                period_key = stmt.get('period_ending')
                if period_key:
                    if period_key not in period_groups:
                        period_groups[period_key] = []
                    stmt['source_name'] = source_name
                    period_groups[period_key].append(stmt)
        
        # Merge statements for each period with weighted averaging
        for period_date, statements in period_groups.items():
            if not statements:
                continue
            
            # Start with the highest-reliability source as base
            statements.sort(key=lambda x: self.source_reliability.get(x['source_name'], 0), reverse=True)
            merged_stmt = statements[0].copy()
            
            # Cross-validate numerical fields across sources
            numerical_fields = ['total_revenue', 'cost_of_revenue', 'gross_profit', 
                              'operating_income', 'net_income', 'eps_basic', 'eps_diluted']
            
            for field in numerical_fields:
                values = []
                weights = []
                
                for stmt in statements:
                    value = stmt.get(field)
                    if value is not None and value != 0:
                        values.append(value)
                        weights.append(self.source_reliability.get(stmt['source_name'], 0.5))
                
                if len(values) > 1:
                    # Calculate weighted average if multiple sources agree
                    variance = self._calculate_variance(values)
                    if variance < 0.1:  # Less than 10% variance between sources
                        weighted_avg = sum(v * w for v, w in zip(values, weights)) / sum(weights)
                        merged_stmt[field] = weighted_avg
                        merged_stmt['confidence_score'] = min(0.98, merged_stmt.get('confidence_score', 0.8) + 0.1)
                elif len(values) == 1:
                    merged_stmt[field] = values[0]
            
            # Track data sources used
            merged_stmt['data_sources'] = [stmt['source_name'] for stmt in statements]
            merged_stmt['source_count'] = len(statements)
            
            merged_statements.append(merged_stmt)
        
        # Sort by period_ending descending
        merged_statements.sort(key=lambda x: x.get('period_ending', date.min), reverse=True)
        
        logger.info("Enhanced income statements merged", 
                   total_periods=len(merged_statements),
                   avg_sources_per_period=sum(stmt.get('source_count', 0) for stmt in merged_statements) / len(merged_statements) if merged_statements else 0)
        
        return merged_statements
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate coefficient of variation for cross-validation"""
        if len(values) < 2:
            return 0
        
        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return 0
        
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        return std_dev / abs(mean_val)  # Coefficient of variation
    
    # Data merging and validation methods
    def _merge_income_statements(self, av_data: List, yf_data: List, fmp_data: List) -> List[Dict[str, Any]]:
        """Merge and cross-validate income statements from multiple sources"""
        # Create a comprehensive merge strategy
        merged_statements = []
        
        # Use Alpha Vantage as primary, fill gaps with Yahoo Finance
        for av_stmt in av_data:
            merged_stmt = av_stmt.copy()
            
            # Find corresponding Yahoo Finance statement
            yf_match = self._find_matching_statement(av_stmt, yf_data)
            if yf_match:
                # Fill missing values from Yahoo Finance
                for key, value in yf_match.items():
                    if merged_stmt.get(key) is None and value is not None:
                        merged_stmt[key] = value
                
                # Update confidence score based on cross-validation
                merged_stmt['confidence_score'] = 0.95
            
            merged_statements.append(merged_stmt)
        
        # Add any Yahoo Finance statements not in Alpha Vantage
        for yf_stmt in yf_data:
            if not self._find_matching_statement(yf_stmt, av_data):
                merged_statements.append(yf_stmt)
        
        # Sort by period_ending descending
        merged_statements.sort(key=lambda x: x.get('period_ending', date.min), reverse=True)
        
        return merged_statements
    
    def _merge_balance_sheets(self, av_data: List, yf_data: List, fmp_data: List) -> List[Dict[str, Any]]:
        """Merge and cross-validate balance sheets from multiple sources"""
        return self._merge_statements_generic(av_data, yf_data, fmp_data)
    
    def _merge_cash_flows(self, av_data: List, yf_data: List, fmp_data: List) -> List[Dict[str, Any]]:
        """Merge and cross-validate cash flows from multiple sources"""
        return self._merge_statements_generic(av_data, yf_data, fmp_data)
    
    def _merge_statements_generic(self, av_data: List, yf_data: List, fmp_data: List) -> List[Dict[str, Any]]:
        """Generic method to merge statements from multiple sources"""
        merged_statements = []
        
        for av_stmt in av_data:
            merged_stmt = av_stmt.copy()
            
            yf_match = self._find_matching_statement(av_stmt, yf_data)
            if yf_match:
                for key, value in yf_match.items():
                    if merged_stmt.get(key) is None and value is not None:
                        merged_stmt[key] = value
                merged_stmt['confidence_score'] = 0.95
            
            merged_statements.append(merged_stmt)
        
        for yf_stmt in yf_data:
            if not self._find_matching_statement(yf_stmt, av_data):
                merged_statements.append(yf_stmt)
        
        merged_statements.sort(key=lambda x: x.get('period_ending', date.min), reverse=True)
        return merged_statements
    
    def _find_matching_statement(self, target_stmt: Dict, statements: List[Dict]) -> Optional[Dict]:
        """Find matching statement by period_ending date"""
        target_date = target_stmt.get('period_ending')
        if not target_date:
            return None
        
        for stmt in statements:
            stmt_date = stmt.get('period_ending')
            if stmt_date and abs((target_date - stmt_date).days) <= 90:  # Within 3 months
                return stmt
        
        return None
    
    def _standardize_company_data(self, data: Dict[str, Any], ticker: str) -> Dict[str, Any]:
        """Standardize company data from multiple sources"""
        return {
            'ticker': ticker.upper(),
            'name': data.get('name', ''),
            'exchange': data.get('exchange', ''),
            'sector': data.get('sector', ''),
            'industry': data.get('industry', ''),
            'country': data.get('country', ''),
            'currency': data.get('currency', 'USD'),
            'market_cap': data.get('market_cap'),
            'employees': data.get('employees'),
            'description': data.get('description', ''),
            'website': data.get('website', ''),
            'data_quality_score': self._calculate_data_quality_score(data),
            'last_updated': datetime.utcnow()
        }
    
    def _calculate_data_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score based on completeness"""
        total_fields = 10
        filled_fields = sum(1 for value in data.values() if value is not None and value != '')
        return min(filled_fields / total_fields, 1.0)
    
    def _filter_statements_by_date(
        self,
        statements: List[Dict[str, Any]],
        period_gte: Optional[date],
        period_lte: Optional[date]
    ) -> List[Dict[str, Any]]:
        """Filter statements by date range"""
        if not period_gte and not period_lte:
            return statements
        
        filtered = []
        for stmt in statements:
            stmt_date = stmt.get('period_ending')
            if not stmt_date:
                continue
            
            if period_gte and stmt_date < period_gte:
                continue
            if period_lte and stmt_date > period_lte:
                continue
            
            filtered.append(stmt)
        
        return filtered
    
    # Utility methods
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == '' or str(value).lower() in ['none', 'nan', 'n/a']:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int"""
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _parse_date(self, date_str) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        try:
            if isinstance(date_str, date):
                return date_str
            return datetime.strptime(str(date_str), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None
    
    def _extract_year(self, date_str) -> Optional[int]:
        """Extract year from date string"""
        parsed_date = self._parse_date(date_str)
        return parsed_date.year if parsed_date else None

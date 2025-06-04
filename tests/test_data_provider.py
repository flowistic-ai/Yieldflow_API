import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import date, datetime

from app.services.data_provider import DataProvider
from app.utils.exceptions import TickerNotFoundError, DataSourceError


class TestDataProvider:
    """Test suite for DataProvider service"""
    
    @pytest.fixture
    def data_provider(self):
        """Create DataProvider instance for testing"""
        return DataProvider()
    
    @pytest.mark.asyncio
    async def test_get_company_info_success(self, data_provider):
        """Test successful company info retrieval"""
        # Mock the yfinance response
        with patch('yfinance.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {
                'longName': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'country': 'United States',
                'currency': 'USD',
                'marketCap': 3000000000000,
                'fullTimeEmployees': 164000,
                'longBusinessSummary': 'Apple Inc. designs and manufactures consumer electronics...'
            }
            mock_ticker.return_value = mock_stock
            
            # Mock cache service
            with patch.object(data_provider.cache_service, 'get_static_data', return_value=None):
                with patch.object(data_provider.cache_service, 'cache_static_data'):
                    result = await data_provider.get_company_info('AAPL')
                    
                    assert result['ticker'] == 'AAPL'
                    assert result['name'] == 'Apple Inc.'
                    assert result['sector'] == 'Technology'
                    assert result['market_cap'] == 3000000000000
    
    @pytest.mark.asyncio
    async def test_get_company_info_ticker_not_found(self, data_provider):
        """Test ticker not found scenario"""
        with patch('yfinance.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.info = {}
            mock_ticker.return_value = mock_stock
            
            # Mock Alpha Vantage to also return empty
            with patch.object(data_provider.av_fundamental, 'get_company_overview', return_value=(None, None)):
                with patch.object(data_provider.cache_service, 'get_static_data', return_value=None):
                    with pytest.raises(TickerNotFoundError):
                        await data_provider.get_company_info('INVALID')
    
    @pytest.mark.asyncio
    async def test_get_income_statements_success(self, data_provider):
        """Test successful income statements retrieval"""
        # Mock Alpha Vantage response
        mock_data = Mock()
        mock_data.empty = False
        mock_data.iterrows.return_value = [
            (0, {
                'fiscalDateEnding': '2023-12-31',
                'totalRevenue': '383000000000',
                'grossProfit': '170000000000',
                'operatingIncome': '115000000000',
                'netIncome': '97000000000'
            })
        ]
        
        with patch.object(data_provider.av_fundamental, 'get_income_statement_annual', return_value=(mock_data, None)):
            with patch.object(data_provider, '_get_yfinance_income_statements', return_value=[]):
                with patch.object(data_provider, '_get_fmp_income_statements', return_value=[]):
                    result = await data_provider.get_income_statements('AAPL')
                    
                    assert len(result) > 0
                    assert result[0]['revenue'] == 383000000000.0
                    assert result[0]['net_income'] == 97000000000.0
    
    @pytest.mark.asyncio
    async def test_safe_float_conversion(self, data_provider):
        """Test safe float conversion utility"""
        assert data_provider._safe_float('123.45') == 123.45
        assert data_provider._safe_float('123') == 123.0
        assert data_provider._safe_float(None) is None
        assert data_provider._safe_float('') is None
        assert data_provider._safe_float('N/A') is None
        assert data_provider._safe_float('invalid') is None
    
    @pytest.mark.asyncio
    async def test_parse_date(self, data_provider):
        """Test date parsing utility"""
        assert data_provider._parse_date('2023-12-31') == date(2023, 12, 31)
        assert data_provider._parse_date(date(2023, 12, 31)) == date(2023, 12, 31)
        assert data_provider._parse_date(None) is None
        assert data_provider._parse_date('invalid') is None
    
    @pytest.mark.asyncio
    async def test_data_merging(self, data_provider):
        """Test data merging from multiple sources"""
        av_data = [{
            'period_ending': date(2023, 12, 31),
            'revenue': 100000000,
            'net_income': None,
            'confidence_score': 0.9
        }]
        
        yf_data = [{
            'period_ending': date(2023, 12, 31),
            'revenue': None,
            'net_income': 20000000,
            'confidence_score': 0.8
        }]
        
        result = data_provider._merge_income_statements(av_data, yf_data, [])
        
        assert len(result) == 1
        assert result[0]['revenue'] == 100000000  # From Alpha Vantage
        assert result[0]['net_income'] == 20000000  # Filled from Yahoo Finance
        assert result[0]['confidence_score'] == 0.95  # Cross-validated 
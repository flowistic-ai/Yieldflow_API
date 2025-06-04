import pytest
from datetime import date, datetime
from unittest.mock import Mock

from app.services.financial_analyzer import FinancialAnalyzer
from app.utils.exceptions import CalculationError, InsufficientDataError


class TestFinancialAnalyzer:
    """Test suite for FinancialAnalyzer service"""
    
    @pytest.fixture
    def analyzer(self):
        """Create FinancialAnalyzer instance for testing"""
        return FinancialAnalyzer()
    
    @pytest.fixture
    def sample_income_statements(self):
        """Sample income statements for testing"""
        return [
            {
                'period_ending': date(2023, 12, 31),
                'revenue': 400000000000,
                'gross_profit': 180000000000,
                'operating_income': 120000000000,
                'net_income': 100000000000
            },
            {
                'period_ending': date(2022, 12, 31),
                'revenue': 380000000000,
                'gross_profit': 170000000000,
                'operating_income': 115000000000,
                'net_income': 95000000000
            },
            {
                'period_ending': date(2021, 12, 31),
                'revenue': 360000000000,
                'gross_profit': 160000000000,
                'operating_income': 110000000000,
                'net_income': 90000000000
            }
        ]
    
    @pytest.fixture
    def sample_balance_sheets(self):
        """Sample balance sheets for testing"""
        return [
            {
                'period_ending': date(2023, 12, 31),
                'current_assets': 150000000000,
                'current_liabilities': 100000000000,
                'total_assets': 350000000000,
                'total_liabilities': 200000000000,
                'shareholders_equity': 150000000000,
                'cash_and_equivalents': 50000000000,
                'inventory': 10000000000
            },
            {
                'period_ending': date(2022, 12, 31),
                'current_assets': 140000000000,
                'current_liabilities': 95000000000,
                'total_assets': 330000000000,
                'total_liabilities': 190000000000,
                'shareholders_equity': 140000000000,
                'cash_and_equivalents': 45000000000,
                'inventory': 9000000000
            }
        ]
    
    @pytest.fixture
    def sample_cash_flows(self):
        """Sample cash flows for testing"""
        return [
            {
                'period_ending': date(2023, 12, 31),
                'operating_cash_flow': 110000000000,
                'capital_expenditures': 15000000000,
                'investing_cash_flow': -20000000000,
                'financing_cash_flow': -30000000000,
                'net_change_in_cash': 5000000000
            },
            {
                'period_ending': date(2022, 12, 31),
                'operating_cash_flow': 105000000000,
                'capital_expenditures': 14000000000,
                'investing_cash_flow': -18000000000,
                'financing_cash_flow': -25000000000,
                'net_change_in_cash': 3000000000
            }
        ]
    
    @pytest.mark.asyncio
    async def test_analyze_income_trends_success(self, analyzer, sample_income_statements):
        """Test successful income trend analysis"""
        result = await analyzer.analyze_income_trends(sample_income_statements)
        
        assert result['revenue_trend'] == 'increasing'
        assert result['data_completeness'] > 0.5
        assert 'revenue_cagr_3y' in result
        assert result['confidence'] > 0.0
    
    @pytest.mark.asyncio
    async def test_analyze_income_trends_insufficient_data(self, analyzer):
        """Test income trend analysis with insufficient data"""
        result = await analyzer.analyze_income_trends([])
        
        assert result['revenue_trend'] == 'insufficient_data'
        assert result['data_completeness'] == 0.0
    
    @pytest.mark.asyncio
    async def test_analyze_liquidity(self, analyzer, sample_balance_sheets):
        """Test liquidity analysis"""
        result = await analyzer.analyze_liquidity(sample_balance_sheets)
        
        assert 'current_ratio' in result
        assert 'quick_ratio' in result
        assert 'cash_ratio' in result
        assert 'score' in result
        assert 'assessment' in result
        
        # Check that current ratio is calculated correctly
        expected_current_ratio = 150000000000 / 100000000000  # 1.5
        assert result['current_ratio'] == expected_current_ratio
    
    @pytest.mark.asyncio
    async def test_analyze_liquidity_no_data(self, analyzer):
        """Test liquidity analysis with no data"""
        with pytest.raises(InsufficientDataError):
            await analyzer.analyze_liquidity([])
    
    @pytest.mark.asyncio
    async def test_analyze_solvency(self, analyzer, sample_balance_sheets):
        """Test solvency analysis"""
        result = await analyzer.analyze_solvency(sample_balance_sheets)
        
        assert 'debt_to_equity' in result
        assert 'debt_to_assets' in result
        assert 'equity_ratio' in result
        assert 'score' in result
        assert 'assessment' in result
        
        # Check debt-to-equity calculation
        expected_debt_to_equity = 200000000000 / 150000000000  # ~1.33
        assert abs(result['debt_to_equity'] - expected_debt_to_equity) < 0.01
    
    @pytest.mark.asyncio
    async def test_analyze_cash_flow_quality(self, analyzer, sample_cash_flows):
        """Test cash flow quality analysis"""
        result = await analyzer.analyze_cash_flow_quality(sample_cash_flows)
        
        assert 'latest_fcf' in result
        assert 'operating_quality' in result
        assert 'fcf_stability' in result
        
        # Check free cash flow calculation
        expected_fcf = 110000000000 - 15000000000  # 95B
        assert result['latest_fcf'] == expected_fcf
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self, analyzer, sample_income_statements, 
                                        sample_balance_sheets, sample_cash_flows):
        """Test comprehensive analysis"""
        result = await analyzer.comprehensive_analysis(
            sample_income_statements, sample_balance_sheets, sample_cash_flows
        )
        
        assert 'overall_score' in result
        assert 'profitability_score' in result
        assert 'liquidity_score' in result
        assert 'solvency_score' in result
        assert 'efficiency_score' in result
        assert 'growth_score' in result
        assert 'insights' in result
        assert 'risk_factors' in result
        assert 'opportunities' in result
        assert 'summary' in result
        
        # Scores should be between 1 and 10
        assert 1 <= result['overall_score'] <= 10
        assert 1 <= result['profitability_score'] <= 10
    
    def test_safe_divide(self, analyzer):
        """Test safe division utility"""
        assert analyzer._safe_divide(10, 2) == 5.0
        assert analyzer._safe_divide(10, 0) is None
        assert analyzer._safe_divide(None, 2) is None
        assert analyzer._safe_divide(10, None) is None
    
    def test_determine_trend(self, analyzer):
        """Test trend determination utility"""
        assert analyzer._determine_trend([1, 2, 3, 4, 5]) == 'improving'
        assert analyzer._determine_trend([5, 4, 3, 2, 1]) == 'declining'
        assert analyzer._determine_trend([3, 3.1, 2.9, 3.05, 3.02]) == 'stable'
        assert analyzer._determine_trend([1]) == 'insufficient_data'
    
    def test_calculate_data_completeness(self, analyzer):
        """Test data completeness calculation"""
        complete_statements = [
            {
                'revenue': 100,
                'net_income': 10,
                'operating_income': 15,
                'gross_profit': 30
            }
        ]
        
        incomplete_statements = [
            {
                'revenue': 100,
                'net_income': None,
                'operating_income': None,
                'gross_profit': None
            }
        ]
        
        assert analyzer._calculate_data_completeness(complete_statements) == 1.0
        assert analyzer._calculate_data_completeness(incomplete_statements) == 0.25
        assert analyzer._calculate_data_completeness([]) == 0.0 
import pytest
from datetime import date, datetime
from unittest.mock import Mock

from app.services.ratio_calculator import RatioCalculator
from app.utils.exceptions import CalculationError, InsufficientDataError


class TestRatioCalculator:
    """Test suite for RatioCalculator service"""
    
    @pytest.fixture
    def calculator(self):
        """Create RatioCalculator instance for testing"""
        return RatioCalculator()
    
    @pytest.fixture
    def sample_income_statements(self):
        """Sample income statements for testing"""
        return [
            {
                'period_ending': date(2023, 12, 31),
                'revenue': 400000000000,
                'gross_profit': 180000000000,
                'operating_income': 120000000000,
                'net_income': 100000000000,
                'interest_expense': 5000000000
            },
            {
                'period_ending': date(2022, 12, 31),
                'revenue': 380000000000,
                'gross_profit': 170000000000,
                'operating_income': 115000000000,
                'net_income': 95000000000,
                'interest_expense': 4500000000
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
                'inventory': 10000000000,
                'accounts_receivable': 20000000000,
                'accounts_payable': 15000000000,
                'long_term_debt': 80000000000,
                'short_term_debt': 20000000000
            },
            {
                'period_ending': date(2022, 12, 31),
                'current_assets': 140000000000,
                'current_liabilities': 95000000000,
                'total_assets': 330000000000,
                'total_liabilities': 190000000000,
                'shareholders_equity': 140000000000,
                'cash_and_equivalents': 45000000000,
                'inventory': 9000000000,
                'accounts_receivable': 18000000000,
                'accounts_payable': 14000000000,
                'long_term_debt': 75000000000,
                'short_term_debt': 18000000000
            }
        ]
    
    @pytest.mark.asyncio
    async def test_calculate_profitability_ratios(self, calculator, sample_income_statements, sample_balance_sheets):
        """Test profitability ratio calculations"""
        result = await calculator.calculate_profitability_ratios(
            sample_income_statements, sample_balance_sheets
        )
        
        ratios = result['ratios']
        
        # Test margin calculations
        assert 'gross_margin' in ratios
        assert 'operating_margin' in ratios
        assert 'net_margin' in ratios
        
        # Test return ratios
        assert 'return_on_assets' in ratios
        assert 'return_on_equity' in ratios
        
        # Verify gross margin calculation
        expected_gross_margin = 180000000000 / 400000000000  # 0.45
        assert abs(ratios['gross_margin'] - expected_gross_margin) < 0.01
        
        # Verify net margin calculation
        expected_net_margin = 100000000000 / 400000000000  # 0.25
        assert abs(ratios['net_margin'] - expected_net_margin) < 0.01
    
    @pytest.mark.asyncio
    async def test_calculate_liquidity_ratios(self, calculator, sample_balance_sheets):
        """Test liquidity ratio calculations"""
        result = await calculator.calculate_liquidity_ratios(sample_balance_sheets)
        
        ratios = result['ratios']
        
        assert 'current_ratio' in ratios
        assert 'quick_ratio' in ratios
        assert 'cash_ratio' in ratios
        assert 'working_capital' in ratios
        
        # Verify current ratio calculation
        expected_current_ratio = 150000000000 / 100000000000  # 1.5
        assert ratios['current_ratio'] == expected_current_ratio
        
        # Verify quick ratio calculation (current assets - inventory) / current liabilities
        expected_quick_ratio = (150000000000 - 10000000000) / 100000000000  # 1.4
        assert ratios['quick_ratio'] == expected_quick_ratio
        
        # Verify working capital
        expected_working_capital = 150000000000 - 100000000000  # 50B
        assert ratios['working_capital'] == expected_working_capital
    
    @pytest.mark.asyncio
    async def test_calculate_leverage_ratios(self, calculator, sample_balance_sheets, sample_income_statements):
        """Test leverage ratio calculations"""
        result = await calculator.calculate_leverage_ratios(
            sample_balance_sheets, sample_income_statements
        )
        
        ratios = result['ratios']
        
        assert 'debt_to_equity' in ratios
        assert 'debt_to_assets' in ratios
        assert 'equity_ratio' in ratios
        assert 'interest_coverage' in ratios
        
        # Verify debt-to-equity calculation
        expected_debt_to_equity = 200000000000 / 150000000000  # ~1.33
        assert abs(ratios['debt_to_equity'] - expected_debt_to_equity) < 0.01
        
        # Verify debt-to-assets calculation
        expected_debt_to_assets = 200000000000 / 350000000000  # ~0.57
        assert abs(ratios['debt_to_assets'] - expected_debt_to_assets) < 0.01
        
        # Verify interest coverage
        expected_interest_coverage = 120000000000 / 5000000000  # 24
        assert ratios['interest_coverage'] == expected_interest_coverage
    
    @pytest.mark.asyncio
    async def test_calculate_efficiency_ratios(self, calculator, sample_income_statements, sample_balance_sheets):
        """Test efficiency ratio calculations"""
        result = await calculator.calculate_efficiency_ratios(
            sample_income_statements, sample_balance_sheets
        )
        
        ratios = result['ratios']
        
        assert 'asset_turnover' in ratios
        assert 'receivables_turnover' in ratios
        assert 'inventory_turnover' in ratios
        assert 'cash_conversion_cycle' in ratios
        
        # Verify asset turnover (revenue / avg total assets)
        avg_assets = (350000000000 + 330000000000) / 2
        expected_asset_turnover = 400000000000 / avg_assets
        assert abs(ratios['asset_turnover'] - expected_asset_turnover) < 0.01
    
    @pytest.mark.asyncio
    async def test_calculate_growth_ratios(self, calculator, sample_income_statements, sample_balance_sheets):
        """Test growth ratio calculations"""
        result = await calculator.calculate_growth_ratios(
            sample_income_statements, sample_balance_sheets
        )
        
        ratios = result['ratios']
        
        assert 'revenue_growth' in ratios
        assert 'net_income_growth' in ratios
        assert 'total_assets_growth' in ratios
        
        # Verify revenue growth calculation
        current_revenue = 400000000000
        previous_revenue = 380000000000
        expected_revenue_growth = (current_revenue - previous_revenue) / previous_revenue
        assert abs(ratios['revenue_growth'] - expected_revenue_growth) < 0.01
    
    @pytest.mark.asyncio
    async def test_calculate_all_ratios(self, calculator, sample_income_statements, sample_balance_sheets):
        """Test comprehensive ratio calculation"""
        result = await calculator.calculate_all_ratios(
            sample_income_statements, sample_balance_sheets
        )
        
        assert 'ratios' in result
        assert 'scores' in result
        assert 'summary' in result
        
        # Check that all categories are present
        assert 'profitability' in result['ratios']
        assert 'liquidity' in result['ratios']
        assert 'leverage' in result['ratios']
        assert 'efficiency' in result['ratios']
        assert 'growth' in result['ratios']
        
        # Check scores
        scores = result['scores']
        assert 'overall_score' in scores
        assert 1 <= scores['overall_score'] <= 10
    
    def test_safe_divide(self, calculator):
        """Test safe division utility"""
        assert calculator._safe_divide(10, 2) == 5.0
        assert calculator._safe_divide(10, 0) is None
        assert calculator._safe_divide(None, 2) is None
        assert calculator._safe_divide(10, None) is None
    
    def test_calculate_growth_rate(self, calculator):
        """Test growth rate calculation"""
        assert calculator._calculate_growth_rate(110, 100) == 0.1  # 10% growth
        assert calculator._calculate_growth_rate(90, 100) == -0.1  # 10% decline
        assert calculator._calculate_growth_rate(100, 0) is None  # Division by zero
        assert calculator._calculate_growth_rate(None, 100) is None  # None value
    
    def test_calculate_cagr(self, calculator):
        """Test CAGR calculation"""
        # 3-year CAGR from 100 to 133.1 should be ~10%
        values = [100, 110, 121, 133.1]
        cagr = calculator._calculate_cagr(values)
        assert abs(cagr - 0.1) < 0.01  # Within 1% tolerance
        
        # Test edge cases
        assert calculator._calculate_cagr([]) is None
        assert calculator._calculate_cagr([100]) is None
        assert calculator._calculate_cagr([0, 100]) is None  # Starting with zero
    
    @pytest.mark.asyncio
    async def test_insufficient_data_error(self, calculator):
        """Test error handling for insufficient data"""
        with pytest.raises(InsufficientDataError):
            await calculator.calculate_profitability_ratios([], [])
        
        with pytest.raises(InsufficientDataError):
            await calculator.calculate_liquidity_ratios([])
    
    def test_ratio_scoring(self, calculator):
        """Test ratio scoring functions"""
        # Test profitability scoring
        good_ratios = {'net_margin': 0.15, 'return_on_equity': 0.18, 'return_on_assets': 0.12}
        score = calculator._score_profitability_ratios(good_ratios)
        assert score > 7.0  # Should be high score
        
        poor_ratios = {'net_margin': -0.05, 'return_on_equity': -0.10, 'return_on_assets': -0.03}
        score = calculator._score_profitability_ratios(poor_ratios)
        assert score < 4.0  # Should be low score
        
        # Test liquidity scoring
        good_liquidity = {'current_ratio': 2.5, 'quick_ratio': 1.2}
        score = calculator._score_liquidity_ratios(good_liquidity)
        assert score > 7.0
        
        poor_liquidity = {'current_ratio': 0.8, 'quick_ratio': 0.3}
        score = calculator._score_liquidity_ratios(poor_liquidity)
        assert score < 4.0 
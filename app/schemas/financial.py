from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class CompanyBase(BaseModel):
    """Base company schema"""
    ticker: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    sector: Optional[str] = Field(None, description="Business sector")
    industry: Optional[str] = Field(None, description="Business industry")
    country: Optional[str] = Field(None, description="Country of incorporation")
    currency: Optional[str] = Field(None, description="Reporting currency")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    employees: Optional[int] = Field(None, description="Number of employees")
    description: Optional[str] = Field(None, description="Company description")
    website: Optional[str] = Field(None, description="Company website")


class CompanyCreate(CompanyBase):
    """Schema for creating company"""
    pass


class CompanyResponse(CompanyBase):
    """Schema for company response"""
    id: int
    data_quality_score: Optional[float]
    last_updated: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IncomeStatementBase(BaseModel):
    """Base income statement schema"""
    period_ending: date = Field(..., description="Period ending date")
    period_type: str = Field(..., description="Period type (annual/quarterly)")
    fiscal_year: int = Field(..., description="Fiscal year")
    fiscal_quarter: Optional[int] = Field(None, description="Fiscal quarter (1-4)")
    
    # Core financial metrics
    revenue: Optional[float] = Field(None, description="Total revenue")
    cost_of_revenue: Optional[float] = Field(None, description="Cost of revenue")
    gross_profit: Optional[float] = Field(None, description="Gross profit")
    operating_expenses: Optional[float] = Field(None, description="Operating expenses")
    operating_income: Optional[float] = Field(None, description="Operating income")
    interest_expense: Optional[float] = Field(None, description="Interest expense")
    pretax_income: Optional[float] = Field(None, description="Pretax income")
    income_tax_expense: Optional[float] = Field(None, description="Income tax expense")
    net_income: Optional[float] = Field(None, description="Net income")
    
    # Per share data
    basic_shares_outstanding: Optional[float] = Field(None, description="Basic shares outstanding")
    diluted_shares_outstanding: Optional[float] = Field(None, description="Diluted shares outstanding")
    basic_eps: Optional[float] = Field(None, description="Basic earnings per share")
    diluted_eps: Optional[float] = Field(None, description="Diluted earnings per share")
    
    # Metadata
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional financial data")
    data_source: Optional[str] = Field(None, description="Data source")
    confidence_score: Optional[float] = Field(None, description="Data confidence score (0-1)")


class IncomeStatementResponse(IncomeStatementBase):
    """Schema for income statement response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BalanceSheetBase(BaseModel):
    """Base balance sheet schema"""
    period_ending: date = Field(..., description="Period ending date")
    period_type: str = Field(..., description="Period type (annual/quarterly)")
    fiscal_year: int = Field(..., description="Fiscal year")
    fiscal_quarter: Optional[int] = Field(None, description="Fiscal quarter (1-4)")
    
    # Assets
    cash_and_equivalents: Optional[float] = Field(None, description="Cash and cash equivalents")
    short_term_investments: Optional[float] = Field(None, description="Short-term investments")
    accounts_receivable: Optional[float] = Field(None, description="Accounts receivable")
    inventory: Optional[float] = Field(None, description="Inventory")
    current_assets: Optional[float] = Field(None, description="Total current assets")
    property_plant_equipment: Optional[float] = Field(None, description="Property, plant & equipment")
    goodwill: Optional[float] = Field(None, description="Goodwill")
    intangible_assets: Optional[float] = Field(None, description="Intangible assets")
    total_assets: Optional[float] = Field(None, description="Total assets")
    
    # Liabilities
    accounts_payable: Optional[float] = Field(None, description="Accounts payable")
    short_term_debt: Optional[float] = Field(None, description="Short-term debt")
    current_liabilities: Optional[float] = Field(None, description="Total current liabilities")
    long_term_debt: Optional[float] = Field(None, description="Long-term debt")
    total_liabilities: Optional[float] = Field(None, description="Total liabilities")
    
    # Equity
    shareholders_equity: Optional[float] = Field(None, description="Shareholders' equity")
    retained_earnings: Optional[float] = Field(None, description="Retained earnings")
    
    # Metadata
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional financial data")
    data_source: Optional[str] = Field(None, description="Data source")
    confidence_score: Optional[float] = Field(None, description="Data confidence score (0-1)")


class BalanceSheetResponse(BalanceSheetBase):
    """Schema for balance sheet response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CashFlowStatementBase(BaseModel):
    """Base cash flow statement schema"""
    period_ending: date = Field(..., description="Period ending date")
    period_type: str = Field(..., description="Period type (annual/quarterly)")
    fiscal_year: int = Field(..., description="Fiscal year")
    fiscal_quarter: Optional[int] = Field(None, description="Fiscal quarter (1-4)")
    
    # Operating activities
    net_income: Optional[float] = Field(None, description="Net income")
    depreciation_amortization: Optional[float] = Field(None, description="Depreciation & amortization")
    working_capital_changes: Optional[float] = Field(None, description="Working capital changes")
    operating_cash_flow: Optional[float] = Field(None, description="Operating cash flow")
    
    # Investing activities
    capital_expenditures: Optional[float] = Field(None, description="Capital expenditures")
    investments: Optional[float] = Field(None, description="Investments")
    investing_cash_flow: Optional[float] = Field(None, description="Investing cash flow")
    
    # Financing activities
    debt_issuance: Optional[float] = Field(None, description="Debt issuance")
    debt_repayment: Optional[float] = Field(None, description="Debt repayment")
    equity_issuance: Optional[float] = Field(None, description="Equity issuance")
    dividends_paid: Optional[float] = Field(None, description="Dividends paid")
    financing_cash_flow: Optional[float] = Field(None, description="Financing cash flow")
    
    # Net change
    net_change_in_cash: Optional[float] = Field(None, description="Net change in cash")
    free_cash_flow: Optional[float] = Field(None, description="Free cash flow")
    
    # Metadata
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional financial data")
    data_source: Optional[str] = Field(None, description="Data source")
    confidence_score: Optional[float] = Field(None, description="Data confidence score (0-1)")


class CashFlowStatementResponse(CashFlowStatementBase):
    """Schema for cash flow statement response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FinancialDataRequest(BaseModel):
    """Schema for financial data requests"""
    ticker: str = Field(..., description="Stock ticker symbol")
    period: str = Field("annual", description="Period type: annual or quarterly")
    limit: Optional[int] = Field(4, description="Number of periods to return", ge=1, le=20)
    report_period_gte: Optional[date] = Field(None, description="Report period greater than or equal to")
    report_period_lte: Optional[date] = Field(None, description="Report period less than or equal to")
    
    @validator('period')
    def validate_period(cls, v):
        if v not in ['annual', 'quarterly']:
            raise ValueError('Period must be either "annual" or "quarterly"')
        return v


class FinancialStatementsResponse(BaseModel):
    """Comprehensive financial statements response"""
    company: CompanyResponse
    income_statements: List[IncomeStatementResponse]
    balance_sheets: List[BalanceSheetResponse]
    cash_flows: List[CashFlowStatementResponse]
    
    # Enhanced analytics summary
    analysis_summary: Optional[Dict[str, Any]] = Field(None, description="Summary analytics")
    key_ratios: Optional[Dict[str, Any]] = Field(None, description="Key financial ratios")
    data_quality: Optional[Dict[str, Any]] = Field(None, description="Data quality information")
    
    class Config:
        from_attributes = True


# Dividend-related enums and schemas
class DividendType(str, Enum):
    """Dividend type enumeration"""
    REGULAR = "regular"
    SPECIAL = "special"
    STOCK = "stock"
    SPIN_OFF = "spin_off"
    RIGHTS = "rights"


class DividendFrequency(str, Enum):
    """Dividend frequency enumeration"""
    ANNUAL = "annual"
    SEMI_ANNUAL = "semi_annual"
    QUARTERLY = "quarterly"
    MONTHLY = "monthly"
    IRREGULAR = "irregular"


class DividendBase(BaseModel):
    """Base dividend schema"""
    ex_date: date = Field(..., description="Ex-dividend date")
    record_date: Optional[date] = Field(None, description="Record date")
    payment_date: Optional[date] = Field(None, description="Payment date")
    declaration_date: Optional[date] = Field(None, description="Declaration date")
    amount: float = Field(..., description="Dividend amount per share", ge=0)
    dividend_type: DividendType = Field(DividendType.REGULAR, description="Type of dividend")
    frequency: Optional[DividendFrequency] = Field(None, description="Dividend frequency")
    currency: Optional[str] = Field("USD", description="Dividend currency")
    
    # Additional metadata
    adjusted_amount: Optional[float] = Field(None, description="Split-adjusted dividend amount")
    tax_rate: Optional[float] = Field(None, description="Applicable tax rate")
    data_source: Optional[str] = Field(None, description="Data source")
    confidence_score: Optional[float] = Field(None, description="Data confidence score (0-1)")


class DividendResponse(DividendBase):
    """Schema for dividend response"""
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DividendAnalysisBase(BaseModel):
    """Base dividend analysis schema"""
    # Yield metrics
    current_dividend_yield: Optional[float] = Field(None, description="Current dividend yield (%)")
    trailing_12m_yield: Optional[float] = Field(None, description="Trailing 12-month dividend yield (%)")
    forward_dividend_yield: Optional[float] = Field(None, description="Forward dividend yield (%)")
    
    # Growth metrics
    dividend_growth_rate_1y: Optional[float] = Field(None, description="1-year dividend growth rate (%)")
    dividend_growth_rate_3y: Optional[float] = Field(None, description="3-year annualized dividend growth rate (%)")
    dividend_growth_rate_5y: Optional[float] = Field(None, description="5-year annualized dividend growth rate (%)")
    dividend_growth_rate_10y: Optional[float] = Field(None, description="10-year annualized dividend growth rate (%)")
    
    # Consistency metrics
    dividend_consistency_score: Optional[float] = Field(None, description="Dividend consistency score (0-10)")
    years_of_consecutive_increases: Optional[int] = Field(None, description="Years of consecutive dividend increases")
    years_of_consecutive_payments: Optional[int] = Field(None, description="Years of consecutive dividend payments")
    
    # Coverage and sustainability
    payout_ratio: Optional[float] = Field(None, description="Dividend payout ratio (%)")
    free_cash_flow_payout_ratio: Optional[float] = Field(None, description="Free cash flow payout ratio (%)")
    debt_to_equity_ratio: Optional[float] = Field(None, description="Debt-to-equity ratio")
    interest_coverage_ratio: Optional[float] = Field(None, description="Interest coverage ratio")
    
    # Financial strength indicators
    roe: Optional[float] = Field(None, description="Return on equity (%)")
    roa: Optional[float] = Field(None, description="Return on assets (%)")
    current_ratio: Optional[float] = Field(None, description="Current ratio")
    debt_service_coverage: Optional[float] = Field(None, description="Debt service coverage ratio")
    
    # Dividend aristocrat status
    is_dividend_aristocrat: Optional[bool] = Field(None, description="S&P 500 Dividend Aristocrat status")
    is_dividend_king: Optional[bool] = Field(None, description="Dividend King status (25+ years)")
    is_dividend_champion: Optional[bool] = Field(None, description="Dividend Champion status")
    
    # Risk assessment
    dividend_risk_score: Optional[float] = Field(None, description="Dividend risk score (0-10, lower is better)")
    sustainability_rating: Optional[str] = Field(None, description="Dividend sustainability rating")
    
    # Market comparison
    sector_average_yield: Optional[float] = Field(None, description="Sector average dividend yield (%)")
    yield_vs_sector: Optional[float] = Field(None, description="Yield premium/discount vs sector (%)")
    yield_vs_market: Optional[float] = Field(None, description="Yield premium/discount vs market (%)")


class DividendAnalysisResponse(DividendAnalysisBase):
    """Schema for dividend analysis response"""
    id: int
    company_id: int
    analysis_date: date
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DividendForecast(BaseModel):
    """Dividend forecast schema"""
    forecast_date: date = Field(..., description="Forecast date")
    estimated_amount: float = Field(..., description="Estimated dividend amount")
    confidence_level: float = Field(..., description="Confidence level (0-1)", ge=0, le=1)
    methodology: str = Field(..., description="Forecasting methodology used")
    factors_considered: List[str] = Field(default_factory=list, description="Factors considered in forecast")


class DividendRequest(BaseModel):
    """Schema for dividend data requests"""
    ticker: str = Field(..., description="Stock ticker symbol")
    start_date: Optional[date] = Field(None, description="Start date for dividend history")
    end_date: Optional[date] = Field(None, description="End date for dividend history")
    include_analysis: bool = Field(True, description="Include dividend analysis")
    include_forecast: bool = Field(False, description="Include dividend forecast")
    include_peer_comparison: bool = Field(False, description="Include peer comparison")


class ComprehensiveDividendResponse(BaseModel):
    """Comprehensive dividend response with all dividend information"""
    company: CompanyResponse
    current_info: Dict[str, Any] = Field(..., description="Current dividend information")
    dividend_history: List[DividendResponse] = Field(default_factory=list, description="Historical dividends")
    analysis: Optional[DividendAnalysisResponse] = Field(None, description="Dividend analysis")
    forecast: Optional[List[DividendForecast]] = Field(None, description="Dividend forecasts")
    peer_comparison: Optional[Dict[str, Any]] = Field(None, description="Peer comparison data")
    market_context: Optional[Dict[str, Any]] = Field(None, description="Market context and benchmarks")
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Dividend risk assessment")
    
    # Economic context from FRED
    economic_indicators: Optional[Dict[str, Any]] = Field(None, description="Relevant economic indicators")
    
    class Config:
        from_attributes = True

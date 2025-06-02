from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from decimal import Decimal


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

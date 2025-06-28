from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, ForeignKey, Text, Date, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from app.models.database import BaseModel


class Company(BaseModel):
    """Company information model"""
    
    __tablename__ = "companies"
    
    ticker = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    exchange = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(50), nullable=True)
    currency = Column(String(10), nullable=True)
    market_cap = Column(Float, nullable=True)
    employees = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Metadata
    data_quality_score = Column(Float, nullable=True)  # 0-1 score
    last_updated = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    income_statements = relationship("IncomeStatement", back_populates="company", cascade="all, delete-orphan")
    balance_sheets = relationship("BalanceSheet", back_populates="company", cascade="all, delete-orphan")
    cash_flows = relationship("CashFlowStatement", back_populates="company", cascade="all, delete-orphan")
    analytics_cache = relationship("AnalyticsCache", back_populates="company", cascade="all, delete-orphan")


class IncomeStatement(BaseModel):
    """Income statement data model"""
    
    __tablename__ = "income_statements"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period_ending = Column(Date, nullable=False)
    period_type = Column(String(20), nullable=False)  # 'annual', 'quarterly'
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=True)
    
    # Core income statement items
    revenue = Column(Float, nullable=True)
    cost_of_revenue = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)
    operating_expenses = Column(Float, nullable=True)
    operating_income = Column(Float, nullable=True)
    interest_expense = Column(Float, nullable=True)
    pretax_income = Column(Float, nullable=True)
    income_tax_expense = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    
    # Per share data
    basic_shares_outstanding = Column(Float, nullable=True)
    diluted_shares_outstanding = Column(Float, nullable=True)
    basic_eps = Column(Float, nullable=True)
    diluted_eps = Column(Float, nullable=True)
    
    # Additional details (stored as JSONB for flexibility)
    additional_data = Column(JSONB, nullable=True)
    
    # Data source and quality
    data_source = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="income_statements")
    
    __table_args__ = (
        Index('ix_income_stmt_company_period', 'company_id', 'period_ending'),
        Index('ix_income_stmt_ticker_year', 'company_id', 'fiscal_year'),
    )


class BalanceSheet(BaseModel):
    """Balance sheet data model"""
    
    __tablename__ = "balance_sheets"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period_ending = Column(Date, nullable=False)
    period_type = Column(String(20), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=True)
    
    # Assets
    cash_and_equivalents = Column(Float, nullable=True)
    short_term_investments = Column(Float, nullable=True)
    accounts_receivable = Column(Float, nullable=True)
    inventory = Column(Float, nullable=True)
    current_assets = Column(Float, nullable=True)
    property_plant_equipment = Column(Float, nullable=True)
    goodwill = Column(Float, nullable=True)
    intangible_assets = Column(Float, nullable=True)
    total_assets = Column(Float, nullable=True)
    
    # Liabilities
    accounts_payable = Column(Float, nullable=True)
    short_term_debt = Column(Float, nullable=True)
    current_liabilities = Column(Float, nullable=True)
    long_term_debt = Column(Float, nullable=True)
    total_liabilities = Column(Float, nullable=True)
    
    # Equity
    shareholders_equity = Column(Float, nullable=True)
    retained_earnings = Column(Float, nullable=True)
    
    # Additional details
    additional_data = Column(JSONB, nullable=True)
    
    # Data source and quality
    data_source = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="balance_sheets")
    
    __table_args__ = (
        Index('ix_balance_sheet_company_period', 'company_id', 'period_ending'),
    )


class CashFlowStatement(BaseModel):
    """Cash flow statement data model"""
    
    __tablename__ = "cash_flow_statements"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    period_ending = Column(Date, nullable=False)
    period_type = Column(String(20), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer, nullable=True)
    
    # Operating activities
    net_income = Column(Float, nullable=True)
    depreciation_amortization = Column(Float, nullable=True)
    working_capital_changes = Column(Float, nullable=True)
    operating_cash_flow = Column(Float, nullable=True)
    
    # Investing activities
    capital_expenditures = Column(Float, nullable=True)
    investments = Column(Float, nullable=True)
    investing_cash_flow = Column(Float, nullable=True)
    
    # Financing activities
    debt_issuance = Column(Float, nullable=True)
    debt_repayment = Column(Float, nullable=True)
    equity_issuance = Column(Float, nullable=True)
    dividends_paid = Column(Float, nullable=True)
    financing_cash_flow = Column(Float, nullable=True)
    
    # Net change
    net_change_in_cash = Column(Float, nullable=True)
    free_cash_flow = Column(Float, nullable=True)
    
    # Additional details
    additional_data = Column(JSONB, nullable=True)
    
    # Data source and quality
    data_source = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="cash_flows")
    
    __table_args__ = (
        Index('ix_cash_flow_company_period', 'company_id', 'period_ending'),
    )


class AnalyticsCache(BaseModel):
    """Cache for computed analytics and ratios"""
    
    __tablename__ = "analytics_cache"
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    analysis_type = Column(String(50), nullable=False)  # 'profitability', 'liquidity', etc.
    period_ending = Column(Date, nullable=False)
    period_type = Column(String(20), nullable=False)
    
    # Computed results (stored as JSONB for flexibility)
    results = Column(JSONB, nullable=False)
    
    # Metadata
    computation_version = Column(String(20), nullable=False)  # Version of calculation logic
    expires_at = Column(DateTime(timezone=True), nullable=False)
    data_freshness = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="analytics_cache")
    
    __table_args__ = (
        Index('ix_analytics_cache_lookup', 'company_id', 'analysis_type', 'period_ending'),
        Index('ix_analytics_cache_expiry', 'expires_at'),
    )

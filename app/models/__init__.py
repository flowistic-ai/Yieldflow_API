# Import all models to make them available
from .user import User, APIKey, UsageRecord
from .financial import Company, IncomeStatement, BalanceSheet, CashFlowStatement, AnalyticsCache
from .database import BaseModel

# Make models available at package level
__all__ = [
    "User", "APIKey", "UsageRecord",
    "Company", "IncomeStatement", "BalanceSheet", "CashFlowStatement", "AnalyticsCache", 
    "BaseModel"
]

# Alias for backward compatibility with database.py imports
user = User
company = Company
financial_statements = [IncomeStatement, BalanceSheet, CashFlowStatement]

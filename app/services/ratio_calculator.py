import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
import structlog
from statistics import mean

from app.utils.exceptions import CalculationError, InsufficientDataError

logger = structlog.get_logger()


class RatioCalculator:
    """Comprehensive financial ratio calculator"""
    
    def __init__(self):
        pass
    
    async def calculate_profitability_ratios(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate profitability ratios"""
        
        if not income_statements or not balance_sheets:
            raise InsufficientDataError("Insufficient data for profitability ratios", 1, 0)
        
        try:
            latest_income = income_statements[0]
            latest_balance = balance_sheets[0]
            
            # Get previous period data if available
            prev_balance = balance_sheets[1] if len(balance_sheets) > 1 else latest_balance
            
            ratios = {}
            
            # Revenue-based margins
            revenue = latest_income.get('revenue', 0)
            if revenue > 0:
                ratios['gross_margin'] = self._safe_divide(
                    latest_income.get('gross_profit'), revenue
                )
                ratios['operating_margin'] = self._safe_divide(
                    latest_income.get('operating_income'), revenue
                )
                ratios['net_margin'] = self._safe_divide(
                    latest_income.get('net_income'), revenue
                )
                ratios['ebitda_margin'] = self._calculate_ebitda_margin(latest_income, revenue)
            
            # Return ratios
            avg_total_assets = (latest_balance.get('total_assets', 0) + 
                              prev_balance.get('total_assets', 0)) / 2
            
            avg_shareholders_equity = (latest_balance.get('shareholders_equity', 0) + 
                                     prev_balance.get('shareholders_equity', 0)) / 2
            
            ratios['return_on_assets'] = self._safe_divide(
                latest_income.get('net_income'), avg_total_assets
            )
            
            ratios['return_on_equity'] = self._safe_divide(
                latest_income.get('net_income'), avg_shareholders_equity
            )
            
            ratios['return_on_invested_capital'] = self._calculate_roic(
                latest_income, latest_balance, prev_balance
            )
            
            # Efficiency ratios
            ratios['asset_turnover'] = self._safe_divide(revenue, avg_total_assets)
            ratios['equity_multiplier'] = self._safe_divide(
                avg_total_assets, avg_shareholders_equity
            )
            
            # DuPont analysis
            ratios['dupont_roe'] = self._calculate_dupont_roe(ratios)
            
            # Market ratios (if market data available)
            if market_data:
                ratios.update(self._calculate_market_ratios(latest_income, market_data))
            
            return {
                'ratios': ratios,
                'analysis_period': latest_income.get('period_ending'),
                'calculation_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error calculating profitability ratios", error=str(e))
            raise CalculationError(f"Profitability ratio calculation failed: {str(e)}", "profitability")
    
    async def calculate_liquidity_ratios(
        self,
        balance_sheets: List[Dict[str, Any]],
        cash_flows: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Calculate liquidity ratios"""
        
        if not balance_sheets:
            raise InsufficientDataError("No balance sheet data for liquidity ratios", 1, 0)
        
        try:
            latest_balance = balance_sheets[0]
            ratios = {}
            
            # Basic liquidity ratios
            current_assets = latest_balance.get('current_assets', 0)
            current_liabilities = latest_balance.get('current_liabilities', 0)
            inventory = latest_balance.get('inventory', 0)
            cash_and_equivalents = latest_balance.get('cash_and_equivalents', 0)
            
            ratios['current_ratio'] = self._safe_divide(current_assets, current_liabilities)
            
            ratios['quick_ratio'] = self._safe_divide(
                current_assets - inventory, current_liabilities
            )
            
            ratios['cash_ratio'] = self._safe_divide(
                cash_and_equivalents, current_liabilities
            )
            
            # Working capital metrics
            ratios['working_capital'] = current_assets - current_liabilities
            ratios['working_capital_to_sales'] = self._calculate_working_capital_to_sales(
                latest_balance, balance_sheets
            )
            
            # Advanced liquidity ratios
            if cash_flows and len(cash_flows) > 0:
                latest_cf = cash_flows[0]
                ratios['operating_cash_flow_ratio'] = self._safe_divide(
                    latest_cf.get('operating_cash_flow'), current_liabilities
                )
                
                ratios['cash_coverage_ratio'] = self._calculate_cash_coverage_ratio(
                    latest_cf, current_liabilities
                )
            
            # Defensive interval ratio
            ratios['defensive_interval'] = self._calculate_defensive_interval(latest_balance)
            
            return {
                'ratios': ratios,
                'analysis_period': latest_balance.get('period_ending'),
                'calculation_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error calculating liquidity ratios", error=str(e))
            raise CalculationError(f"Liquidity ratio calculation failed: {str(e)}", "liquidity")
    
    async def calculate_leverage_ratios(
        self,
        balance_sheets: List[Dict[str, Any]],
        income_statements: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Calculate leverage/solvency ratios"""
        
        if not balance_sheets:
            raise InsufficientDataError("No balance sheet data for leverage ratios", 1, 0)
        
        try:
            latest_balance = balance_sheets[0]
            ratios = {}
            
            total_assets = latest_balance.get('total_assets', 0)
            total_liabilities = latest_balance.get('total_liabilities', 0)
            shareholders_equity = latest_balance.get('shareholders_equity', 0)
            long_term_debt = latest_balance.get('long_term_debt', 0)
            short_term_debt = latest_balance.get('short_term_debt', 0)
            
            # Basic leverage ratios
            ratios['debt_to_equity'] = self._safe_divide(total_liabilities, shareholders_equity)
            ratios['debt_to_assets'] = self._safe_divide(total_liabilities, total_assets)
            ratios['equity_ratio'] = self._safe_divide(shareholders_equity, total_assets)
            
            # Debt composition ratios
            total_debt = (long_term_debt or 0) + (short_term_debt or 0)
            total_debt_plus_equity = total_debt + (shareholders_equity or 0)
            
            ratios['debt_to_capital'] = self._safe_divide(total_debt, total_debt_plus_equity)
            
            ratios['long_term_debt_to_equity'] = self._safe_divide(
                long_term_debt, shareholders_equity
            )
            
            long_term_debt_plus_equity = (long_term_debt or 0) + (shareholders_equity or 0)
            ratios['long_term_debt_to_capital'] = self._safe_divide(
                long_term_debt, long_term_debt_plus_equity
            )
            
            # Asset quality ratios
            ratios['tangible_assets_ratio'] = self._calculate_tangible_assets_ratio(latest_balance)
            
            # Coverage ratios (if income statement available)
            if income_statements and len(income_statements) > 0:
                latest_income = income_statements[0]
                
                ratios['interest_coverage'] = self._calculate_interest_coverage(
                    latest_income
                )
                
                ratios['debt_service_coverage'] = self._calculate_debt_service_coverage(
                    latest_income, latest_balance
                )
                
                ratios['times_interest_earned'] = ratios['interest_coverage']  # Same as interest coverage
            
            return {
                'ratios': ratios,
                'analysis_period': latest_balance.get('period_ending'),
                'calculation_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error calculating leverage ratios", error=str(e))
            raise CalculationError(f"Leverage ratio calculation failed: {str(e)}", "leverage")
    
    async def calculate_efficiency_ratios(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate efficiency/activity ratios"""
        
        if not income_statements or not balance_sheets:
            raise InsufficientDataError("Insufficient data for efficiency ratios", 1, 0)
        
        try:
            latest_income = income_statements[0]
            latest_balance = balance_sheets[0]
            prev_balance = balance_sheets[1] if len(balance_sheets) > 1 else latest_balance
            
            ratios = {}
            revenue = latest_income.get('revenue', 0)
            cost_of_revenue = latest_income.get('cost_of_revenue', 0)
            
            # Asset turnover ratios
            current_assets = latest_balance.get('total_assets', 0) or 0
            previous_assets = prev_balance.get('total_assets', 0) or 0
            avg_total_assets = (current_assets + previous_assets) / 2
            
            ratios['asset_turnover'] = self._safe_divide(revenue, avg_total_assets)
            
            # Working capital efficiency
            current_ar = latest_balance.get('accounts_receivable', 0) or 0
            previous_ar = prev_balance.get('accounts_receivable', 0) or 0
            avg_accounts_receivable = (current_ar + previous_ar) / 2
            
            current_inv = latest_balance.get('inventory', 0) or 0
            previous_inv = prev_balance.get('inventory', 0) or 0
            avg_inventory = (current_inv + previous_inv) / 2
            
            current_ap = latest_balance.get('accounts_payable', 0) or 0
            previous_ap = prev_balance.get('accounts_payable', 0) or 0
            avg_accounts_payable = (current_ap + previous_ap) / 2
            
            # Receivables ratios
            ratios['receivables_turnover'] = self._safe_divide(revenue, avg_accounts_receivable)
            ratios['days_sales_outstanding'] = self._safe_divide(365, ratios.get('receivables_turnover'))
            
            # Inventory ratios
            ratios['inventory_turnover'] = self._safe_divide(cost_of_revenue, avg_inventory)
            ratios['days_inventory_outstanding'] = self._safe_divide(365, ratios.get('inventory_turnover'))
            
            # Payables ratios
            ratios['payables_turnover'] = self._safe_divide(cost_of_revenue, avg_accounts_payable)
            ratios['days_payable_outstanding'] = self._safe_divide(365, ratios.get('payables_turnover'))
            
            # Cash conversion cycle
            dso = ratios.get('days_sales_outstanding', 0) or 0
            dio = ratios.get('days_inventory_outstanding', 0) or 0
            dpo = ratios.get('days_payable_outstanding', 0) or 0
            ratios['cash_conversion_cycle'] = dso + dio - dpo
            
            # Fixed asset efficiency
            current_ppe = latest_balance.get('property_plant_equipment', 0) or 0
            previous_ppe = prev_balance.get('property_plant_equipment', 0) or 0
            avg_ppe = (current_ppe + previous_ppe) / 2
            
            ratios['fixed_asset_turnover'] = self._safe_divide(revenue, avg_ppe)
            
            # Total capital efficiency
            avg_total_capital = avg_total_assets  # Could be refined
            ratios['total_capital_turnover'] = self._safe_divide(revenue, avg_total_capital)
            
            return {
                'ratios': ratios,
                'analysis_period': latest_income.get('period_ending'),
                'calculation_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error calculating efficiency ratios", error=str(e))
            raise CalculationError(f"Efficiency ratio calculation failed: {str(e)}", "efficiency")
    
    async def calculate_market_ratios(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate market valuation ratios"""
        
        if not income_statements or not balance_sheets or not market_data:
            raise InsufficientDataError("Insufficient data for market ratios", 1, 0)
        
        try:
            latest_income = income_statements[0]
            latest_balance = balance_sheets[0]
            ratios = {}
            
            # Basic market data
            stock_price = market_data.get('stock_price', 0)
            shares_outstanding = market_data.get('shares_outstanding', 0)
            market_cap = market_data.get('market_cap', stock_price * shares_outstanding)
            
            # Per-share metrics
            net_income = latest_income.get('net_income', 0)
            revenue = latest_income.get('revenue', 0)
            book_value = latest_balance.get('shareholders_equity', 0)
            
            if shares_outstanding > 0:
                ratios['earnings_per_share'] = net_income / shares_outstanding
                ratios['book_value_per_share'] = book_value / shares_outstanding
                ratios['sales_per_share'] = revenue / shares_outstanding
            
            # Valuation ratios
            if ratios.get('earnings_per_share', 0) > 0:
                ratios['price_to_earnings'] = stock_price / ratios['earnings_per_share']
            
            if ratios.get('book_value_per_share', 0) > 0:
                ratios['price_to_book'] = stock_price / ratios['book_value_per_share']
            
            if ratios.get('sales_per_share', 0) > 0:
                ratios['price_to_sales'] = stock_price / ratios['sales_per_share']
            
            # Enterprise value ratios
            total_debt = (latest_balance.get('long_term_debt', 0) + 
                         latest_balance.get('short_term_debt', 0))
            cash = latest_balance.get('cash_and_equivalents', 0)
            
            enterprise_value = market_cap + total_debt - cash
            
            if revenue > 0:
                ratios['ev_to_sales'] = enterprise_value / revenue
            
            ebitda = self._calculate_ebitda(latest_income)
            if ebitda and ebitda > 0:
                ratios['ev_to_ebitda'] = enterprise_value / ebitda
            
            # Dividend ratios (if dividend data available)
            dividend_per_share = market_data.get('dividend_per_share', 0)
            if dividend_per_share > 0:
                ratios['dividend_yield'] = dividend_per_share / stock_price
                
                if ratios.get('earnings_per_share', 0) > 0:
                    ratios['payout_ratio'] = dividend_per_share / ratios['earnings_per_share']
            
            return {
                'ratios': ratios,
                'market_data': {
                    'stock_price': stock_price,
                    'market_cap': market_cap,
                    'enterprise_value': enterprise_value
                },
                'analysis_period': latest_income.get('period_ending'),
                'calculation_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error calculating market ratios", error=str(e))
            raise CalculationError(f"Market ratio calculation failed: {str(e)}", "market")
    
    async def calculate_growth_ratios(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate growth ratios"""
        
        if len(income_statements) < 2:
            return {'message': 'Insufficient data for growth calculations'}
        
        try:
            # Sort by period_ending to ensure correct order
            sorted_income = sorted(income_statements, key=lambda x: x.get('period_ending', date.min))
            sorted_balance = sorted(balance_sheets, key=lambda x: x.get('period_ending', date.min))
            
            ratios = {}
            
            # Year-over-year growth rates
            if len(sorted_income) >= 2:
                current = sorted_income[-1]
                previous = sorted_income[-2]
                
                ratios['revenue_growth'] = self._calculate_growth_rate(
                    current.get('revenue'), previous.get('revenue')
                )
                
                ratios['gross_profit_growth'] = self._calculate_growth_rate(
                    current.get('gross_profit'), previous.get('gross_profit')
                )
                
                ratios['operating_income_growth'] = self._calculate_growth_rate(
                    current.get('operating_income'), previous.get('operating_income')
                )
                
                ratios['net_income_growth'] = self._calculate_growth_rate(
                    current.get('net_income'), previous.get('net_income')
                )
            
            # Asset growth
            if len(sorted_balance) >= 2:
                current_bs = sorted_balance[-1]
                previous_bs = sorted_balance[-2]
                
                ratios['total_assets_growth'] = self._calculate_growth_rate(
                    current_bs.get('total_assets'), previous_bs.get('total_assets')
                )
                
                ratios['equity_growth'] = self._calculate_growth_rate(
                    current_bs.get('shareholders_equity'), previous_bs.get('shareholders_equity')
                )
            
            # Multi-year compound growth rates
            if len(sorted_income) >= 3:
                ratios['revenue_cagr_3y'] = self._calculate_cagr(
                    [stmt.get('revenue', 0) for stmt in sorted_income[-3:]]
                )
            
            if len(sorted_income) >= 5:
                ratios['revenue_cagr_5y'] = self._calculate_cagr(
                    [stmt.get('revenue', 0) for stmt in sorted_income[-5:]]
                )
            
            # Sustainable growth rate
            if len(sorted_income) >= 1 and len(sorted_balance) >= 1:
                ratios['sustainable_growth_rate'] = self._calculate_sustainable_growth_rate(
                    sorted_income[-1], sorted_balance[-1]
                )
            
            return {
                'ratios': ratios,
                'analysis_period': sorted_income[-1].get('period_ending'),
                'calculation_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error calculating growth ratios", error=str(e))
            raise CalculationError(f"Growth ratio calculation failed: {str(e)}", "growth")
    
    async def calculate_all_ratios(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        cash_flows: Optional[List[Dict[str, Any]]] = None,
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate all financial ratios"""
        
        try:
            all_ratios = {}
            
            # Calculate each category of ratios
            if income_statements and balance_sheets:
                profitability = await self.calculate_profitability_ratios(
                    income_statements, balance_sheets, market_data
                )
                all_ratios['profitability'] = profitability
                
                efficiency = await self.calculate_efficiency_ratios(
                    income_statements, balance_sheets
                )
                all_ratios['efficiency'] = efficiency
                
                growth = await self.calculate_growth_ratios(
                    income_statements, balance_sheets
                )
                all_ratios['growth'] = growth
            
            if balance_sheets:
                liquidity = await self.calculate_liquidity_ratios(balance_sheets, cash_flows)
                all_ratios['liquidity'] = liquidity
                
                leverage = await self.calculate_leverage_ratios(balance_sheets, income_statements)
                all_ratios['leverage'] = leverage
            
            if market_data and income_statements and balance_sheets:
                market = await self.calculate_market_ratios(
                    income_statements, balance_sheets, market_data
                )
                all_ratios['market'] = market
            
            # Calculate ratio scores and rankings
            ratio_scores = self._calculate_ratio_scores(all_ratios)
            
            return {
                'ratios': all_ratios,
                'scores': ratio_scores,
                'summary': self._generate_ratio_summary(all_ratios, ratio_scores),
                'calculation_date': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error calculating all ratios", error=str(e))
            raise CalculationError(f"Comprehensive ratio calculation failed: {str(e)}", "all_ratios")
    
    # Helper methods
    def _safe_divide(self, numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
        """Safely divide two numbers"""
        if numerator is None or denominator is None or denominator == 0:
            return None
        return numerator / denominator
    
    def _calculate_ebitda(self, income_statement: Dict[str, Any]) -> Optional[float]:
        """Calculate EBITDA"""
        operating_income = income_statement.get('operating_income')
        depreciation = income_statement.get('depreciation_amortization', 0)
        
        if operating_income is not None:
            return operating_income + depreciation
        return None
    
    def _calculate_ebitda_margin(self, income_statement: Dict[str, Any], revenue: float) -> Optional[float]:
        """Calculate EBITDA margin"""
        ebitda = self._calculate_ebitda(income_statement)
        return self._safe_divide(ebitda, revenue)
    
    def _calculate_roic(
        self,
        income_statement: Dict[str, Any],
        current_balance: Dict[str, Any],
        previous_balance: Dict[str, Any]
    ) -> Optional[float]:
        """Calculate Return on Invested Capital"""
        net_income = income_statement.get('net_income') or 0
        
        # Calculate invested capital (average)
        current_ic = ((current_balance.get('shareholders_equity') or 0) + 
                     (current_balance.get('long_term_debt') or 0) + 
                     (current_balance.get('short_term_debt') or 0))
        
        previous_ic = ((previous_balance.get('shareholders_equity') or 0) + 
                      (previous_balance.get('long_term_debt') or 0) + 
                      (previous_balance.get('short_term_debt') or 0))
        
        avg_invested_capital = (current_ic + previous_ic) / 2
        
        return self._safe_divide(net_income, avg_invested_capital)
    
    def _calculate_dupont_roe(self, ratios: Dict[str, Any]) -> Optional[float]:
        """Calculate DuPont ROE (Net Margin × Asset Turnover × Equity Multiplier)"""
        net_margin = ratios.get('net_margin')
        asset_turnover = ratios.get('asset_turnover')
        equity_multiplier = ratios.get('equity_multiplier')
        
        if all(x is not None for x in [net_margin, asset_turnover, equity_multiplier]):
            return net_margin * asset_turnover * equity_multiplier
        return None
    
    def _calculate_market_ratios(
        self,
        income_statement: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate basic market ratios from market data"""
        ratios = {}
        
        # This would be expanded based on available market data
        return ratios
    
    def _calculate_working_capital_to_sales(
        self,
        current_balance: Dict[str, Any],
        balance_sheets: List[Dict[str, Any]]
    ) -> Optional[float]:
        """Calculate working capital to sales ratio"""
        # This would require revenue data - simplified implementation
        working_capital = (current_balance.get('current_assets', 0) - 
                          current_balance.get('current_liabilities', 0))
        
        # Would need to get revenue from income statement
        return None  # Placeholder
    
    def _calculate_cash_coverage_ratio(
        self,
        cash_flow: Dict[str, Any],
        current_liabilities: float
    ) -> Optional[float]:
        """Calculate cash coverage ratio"""
        operating_cf = cash_flow.get('operating_cash_flow', 0)
        return self._safe_divide(operating_cf, current_liabilities)
    
    def _calculate_defensive_interval(self, balance_sheet: Dict[str, Any]) -> Optional[float]:
        """Calculate defensive interval (in days)"""
        liquid_assets = (balance_sheet.get('cash_and_equivalents', 0) + 
                        balance_sheet.get('accounts_receivable', 0))
        
        # Would need daily operating expenses - simplified
        return None  # Placeholder
    
    def _calculate_tangible_assets_ratio(self, balance_sheet: Dict[str, Any]) -> Optional[float]:
        """Calculate tangible assets ratio"""
        total_assets = balance_sheet.get('total_assets')
        intangible_assets = balance_sheet.get('intangible_assets') or 0
        goodwill = balance_sheet.get('goodwill') or 0
        
        if total_assets and total_assets > 0:
            return (total_assets - intangible_assets - goodwill) / total_assets
        return None
    
    def _calculate_interest_coverage(self, income_statement: Dict[str, Any]) -> Optional[float]:
        """Calculate interest coverage ratio"""
        operating_income = income_statement.get('operating_income')
        interest_expense = income_statement.get('interest_expense')
        
        return self._safe_divide(operating_income, interest_expense)
    
    def _calculate_debt_service_coverage(
        self,
        income_statement: Dict[str, Any],
        balance_sheet: Dict[str, Any]
    ) -> Optional[float]:
        """Calculate debt service coverage ratio"""
        # Simplified - would need cash flow data for accurate calculation
        operating_income = income_statement.get('operating_income') or 0
        interest_expense = income_statement.get('interest_expense') or 0
        
        # Estimate principal payments (simplified)
        short_term_debt = balance_sheet.get('short_term_debt') or 0
        debt_service = interest_expense + short_term_debt
        
        return self._safe_divide(operating_income, debt_service)
    
    def _calculate_growth_rate(self, current: Optional[float], previous: Optional[float]) -> Optional[float]:
        """Calculate growth rate between two periods"""
        if current is None or previous is None or previous == 0:
            return None
        return (current - previous) / previous
    
    def _calculate_cagr(self, values: List[float]) -> Optional[float]:
        """Calculate Compound Annual Growth Rate"""
        # Filter out None values and ensure we have valid numbers
        valid_values = [v for v in values if v is not None and v > 0]
        
        if len(valid_values) < 2:
            return None
        
        periods = len(valid_values) - 1
        return ((valid_values[-1] / valid_values[0]) ** (1/periods)) - 1
    
    def _calculate_sustainable_growth_rate(
        self,
        income_statement: Dict[str, Any],
        balance_sheet: Dict[str, Any]
    ) -> Optional[float]:
        """Calculate sustainable growth rate"""
        net_income = income_statement.get('net_income') or 0
        shareholders_equity = balance_sheet.get('shareholders_equity') or 0
        
        if shareholders_equity and shareholders_equity > 0:
            roe = net_income / shareholders_equity
            # Assume 100% retention rate (no dividends) for simplification
            retention_rate = 1.0
            return roe * retention_rate
        
        return None
    
    def _calculate_ratio_scores(self, all_ratios: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate scores for different ratio categories"""
        scores = {}
        
        # Profitability score
        prof_ratios = all_ratios.get('profitability', {}).get('ratios', {})
        scores['profitability_score'] = self._score_profitability_ratios(prof_ratios)
        
        # Liquidity score
        liq_ratios = all_ratios.get('liquidity', {}).get('ratios', {})
        scores['liquidity_score'] = self._score_liquidity_ratios(liq_ratios)
        
        # Leverage score
        lev_ratios = all_ratios.get('leverage', {}).get('ratios', {})
        scores['leverage_score'] = self._score_leverage_ratios(lev_ratios)
        
        # Efficiency score
        eff_ratios = all_ratios.get('efficiency', {}).get('ratios', {})
        scores['efficiency_score'] = self._score_efficiency_ratios(eff_ratios)
        
        # Overall score
        scores['overall_score'] = self._calculate_overall_ratio_score(scores)
        
        return scores
    
    def _score_profitability_ratios(self, ratios: Dict[str, Any]) -> float:
        """Score profitability ratios on 1-10 scale"""
        score = 5.0
        
        net_margin = ratios.get('net_margin', 0) or 0
        roe = ratios.get('return_on_equity', 0) or 0
        roa = ratios.get('return_on_assets', 0) or 0
        
        # Net margin scoring
        if net_margin >= 0.20:
            score += 2.0
        elif net_margin >= 0.10:
            score += 1.0
        elif net_margin >= 0.05:
            score += 0.5
        elif net_margin < 0:
            score -= 2.0
        
        # ROE scoring
        if roe >= 0.20:
            score += 1.5
        elif roe >= 0.15:
            score += 1.0
        elif roe >= 0.10:
            score += 0.5
        elif roe < 0:
            score -= 1.5
        
        return max(1.0, min(10.0, score))
    
    def _score_liquidity_ratios(self, ratios: Dict[str, Any]) -> float:
        """Score liquidity ratios on 1-10 scale"""
        score = 5.0
        
        current_ratio = ratios.get('current_ratio', 0) or 0
        quick_ratio = ratios.get('quick_ratio', 0) or 0
        
        # Current ratio scoring
        if current_ratio >= 2.0:
            score += 2.0
        elif current_ratio >= 1.5:
            score += 1.0
        elif current_ratio >= 1.0:
            score += 0.0
        else:
            score -= 2.0
        
        # Quick ratio scoring
        if quick_ratio >= 1.0:
            score += 1.5
        elif quick_ratio >= 0.7:
            score += 0.5
        else:
            score -= 1.0
        
        return max(1.0, min(10.0, score))
    
    def _score_leverage_ratios(self, ratios: Dict[str, Any]) -> float:
        """Score leverage ratios on 1-10 scale"""
        score = 5.0
        
        debt_to_equity = ratios.get('debt_to_equity', 0) or 0
        debt_to_assets = ratios.get('debt_to_assets', 0) or 0
        
        # Lower debt ratios are better
        if debt_to_equity <= 0.3:
            score += 2.5
        elif debt_to_equity <= 0.6:
            score += 1.0
        elif debt_to_equity <= 1.0:
            score += 0.0
        elif debt_to_equity <= 2.0:
            score -= 1.5
        else:
            score -= 3.0
        
        return max(1.0, min(10.0, score))
    
    def _score_efficiency_ratios(self, ratios: Dict[str, Any]) -> float:
        """Score efficiency ratios on 1-10 scale"""
        score = 5.0
        
        asset_turnover = ratios.get('asset_turnover', 0) or 0
        receivables_turnover = ratios.get('receivables_turnover', 0) or 0
        
        # Asset turnover scoring
        if asset_turnover >= 1.5:
            score += 2.0
        elif asset_turnover >= 1.0:
            score += 1.0
        elif asset_turnover >= 0.5:
            score += 0.0
        else:
            score -= 1.0
        
        return max(1.0, min(10.0, score))
    
    def _calculate_overall_ratio_score(self, scores: Dict[str, Any]) -> float:
        """Calculate weighted overall ratio score"""
        weights = {
            'profitability_score': 0.30,
            'liquidity_score': 0.25,
            'leverage_score': 0.25,
            'efficiency_score': 0.20
        }
        
        overall = 0.0
        total_weight = 0.0
        
        for score_name, weight in weights.items():
            if score_name in scores:
                overall += scores[score_name] * weight
                total_weight += weight
        
        return overall / total_weight if total_weight > 0 else 5.0
    
    def _generate_ratio_summary(self, all_ratios: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of ratio analysis"""
        summary = {
            'overall_score': scores.get('overall_score', 5.0),
            'strengths': [],
            'weaknesses': [],
            'key_ratios': {}
        }
        
        # Identify strengths and weaknesses
        if scores.get('profitability_score', 5.0) >= 7.0:
            summary['strengths'].append('Strong profitability')
        elif scores.get('profitability_score', 5.0) <= 3.0:
            summary['weaknesses'].append('Weak profitability')
        
        if scores.get('liquidity_score', 5.0) >= 7.0:
            summary['strengths'].append('Strong liquidity')
        elif scores.get('liquidity_score', 5.0) <= 3.0:
            summary['weaknesses'].append('Liquidity concerns')
        
        # Extract key ratios
        if 'profitability' in all_ratios:
            prof_ratios = all_ratios['profitability'].get('ratios', {})
            summary['key_ratios']['net_margin'] = prof_ratios.get('net_margin')
            summary['key_ratios']['return_on_equity'] = prof_ratios.get('return_on_equity')
        
        if 'liquidity' in all_ratios:
            liq_ratios = all_ratios['liquidity'].get('ratios', {})
            summary['key_ratios']['current_ratio'] = liq_ratios.get('current_ratio')
        
        return summary

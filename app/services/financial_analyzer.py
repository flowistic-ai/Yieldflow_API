import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
import structlog
from statistics import mean, stdev

from app.utils.exceptions import CalculationError, InsufficientDataError
from app.services.ratio_calculator import RatioCalculator

logger = structlog.get_logger()


class FinancialAnalyzer:
    """Comprehensive financial analysis engine"""
    
    def __init__(self):
        self.ratio_calculator = RatioCalculator()
    
    async def analyze_income_trends(self, income_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze income statement trends and patterns"""
        
        if len(income_statements) < 2:
            return {
                'revenue_trend': 'insufficient_data',
                'margin_trend': 'insufficient_data',
                'data_completeness': 0.0
            }
        
        try:
            # Sort by period_ending
            sorted_statements = sorted(income_statements, key=lambda x: x.get('period_ending', date.min))
            
            # Calculate revenue trend
            revenue_trend = self._calculate_revenue_trend(sorted_statements)
            
            # Calculate margin trends
            margin_trends = self._calculate_margin_trends(sorted_statements)
            
            # Calculate growth rates
            growth_rates = self._calculate_growth_rates(sorted_statements)
            
            # Assess earnings quality
            earnings_quality = self._assess_earnings_quality(sorted_statements)
            
            # Calculate data completeness
            data_completeness = self._calculate_data_completeness(sorted_statements)
            
            return {
                'revenue_trend': revenue_trend['trend'],
                'revenue_cagr_3y': revenue_trend.get('cagr_3y', 0.0),
                'margin_trend': margin_trends['overall_trend'],
                'gross_margin_trend': margin_trends['gross_margin_trend'],
                'operating_margin_trend': margin_trends['operating_margin_trend'],
                'net_margin_trend': margin_trends['net_margin_trend'],
                'earnings_quality': earnings_quality,
                'growth_rates': growth_rates,
                'data_completeness': data_completeness,
                'confidence': min(data_completeness * 1.2, 1.0),
                'last_updated': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error in income trend analysis", error=str(e))
            raise CalculationError(f"Income trend analysis failed: {str(e)}", "income_trends")
    
    async def calculate_profitability_ratios(self, income_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate key profitability ratios from income statements"""
        
        if not income_statements:
            return {
                'gross_margin': None,
                'operating_margin': None,
                'net_margin': None,
                'eps_growth': None
            }
        
        try:
            latest_statement = income_statements[0]  # Most recent
            
            # Calculate margins
            gross_margin = self._safe_divide(
                latest_statement.get('gross_profit'),
                latest_statement.get('revenue')
            )
            
            operating_margin = self._safe_divide(
                latest_statement.get('operating_income'),
                latest_statement.get('revenue')
            )
            
            net_margin = self._safe_divide(
                latest_statement.get('net_income'),
                latest_statement.get('revenue')
            )
            
            # Calculate EPS growth if multiple periods available
            eps_growth = None
            if len(income_statements) >= 2:
                latest_eps = latest_statement.get('diluted_eps') or latest_statement.get('basic_eps')
                previous_eps = income_statements[1].get('diluted_eps') or income_statements[1].get('basic_eps')
                
                if latest_eps and previous_eps and previous_eps != 0:
                    eps_growth = ((latest_eps - previous_eps) / previous_eps) * 100
            
            # Calculate additional profitability metrics
            roa = self._safe_divide(
                latest_statement.get('net_income'),
                latest_statement.get('total_assets')  # This would come from balance sheet if available
            )
            
            return {
                'gross_margin': gross_margin * 100 if gross_margin else None,  # Convert to percentage
                'operating_margin': operating_margin * 100 if operating_margin else None,
                'net_margin': net_margin * 100 if net_margin else None,
                'eps_growth': eps_growth,
                'return_on_assets': roa * 100 if roa else None,
                'revenue': latest_statement.get('revenue'),
                'net_income': latest_statement.get('net_income'),
                'gross_profit': latest_statement.get('gross_profit'),
                'operating_income': latest_statement.get('operating_income')
            }
            
        except Exception as e:
            logger.error("Error calculating profitability ratios", error=str(e))
            return {
                'gross_margin': None,
                'operating_margin': None,
                'net_margin': None,
                'eps_growth': None,
                'error': str(e)
            }
    
    async def analyze_liquidity(self, balance_sheets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze liquidity position and trends"""
        
        if not balance_sheets:
            raise InsufficientDataError("No balance sheet data available", 1, 0)
        
        try:
            latest_bs = balance_sheets[0]  # Most recent
            
            # Calculate liquidity ratios
            current_ratio = self._safe_divide(
                latest_bs.get('current_assets'),
                latest_bs.get('current_liabilities')
            )
            
            quick_ratio = self._safe_divide(
                (latest_bs.get('current_assets', 0) - latest_bs.get('inventory', 0)),
                latest_bs.get('current_liabilities')
            )
            
            cash_ratio = self._safe_divide(
                latest_bs.get('cash_and_equivalents'),
                latest_bs.get('current_liabilities')
            )
            
            working_capital = (latest_bs.get('current_assets', 0) - 
                             latest_bs.get('current_liabilities', 0))
            
            # Calculate liquidity score (1-10 scale)
            liquidity_score = self._calculate_liquidity_score(current_ratio, quick_ratio, cash_ratio)
            
            # Assess liquidity position
            assessment = self._assess_liquidity_position(current_ratio, quick_ratio, cash_ratio)
            
            # Calculate trends if multiple periods available
            trends = {}
            if len(balance_sheets) > 1:
                trends = self._calculate_liquidity_trends(balance_sheets)
            
            return {
                'current_ratio': current_ratio,
                'quick_ratio': quick_ratio,
                'cash_ratio': cash_ratio,
                'working_capital': working_capital,
                'score': liquidity_score,
                'assessment': assessment,
                'trends': trends,
                'benchmark_comparison': self._get_liquidity_benchmarks(current_ratio, quick_ratio)
            }
            
        except Exception as e:
            logger.error("Error in liquidity analysis", error=str(e))
            raise CalculationError(f"Liquidity analysis failed: {str(e)}", "liquidity")
    
    async def analyze_solvency(self, balance_sheets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze solvency and financial leverage"""
        
        if not balance_sheets:
            raise InsufficientDataError("No balance sheet data available", 1, 0)
        
        try:
            latest_bs = balance_sheets[0]  # Most recent
            
            # Calculate solvency ratios
            debt_to_equity = self._safe_divide(
                latest_bs.get('total_liabilities'),
                latest_bs.get('shareholders_equity')
            )
            
            debt_to_assets = self._safe_divide(
                latest_bs.get('total_liabilities'),
                latest_bs.get('total_assets')
            )
            
            equity_ratio = self._safe_divide(
                latest_bs.get('shareholders_equity'),
                latest_bs.get('total_assets')
            )
            
            # Calculate asset quality metrics
            tangible_assets_ratio = self._calculate_tangible_assets_ratio(latest_bs)
            goodwill_percentage = self._calculate_goodwill_percentage(latest_bs)
            
            # Calculate solvency score
            solvency_score = self._calculate_solvency_score(debt_to_equity, debt_to_assets, equity_ratio)
            
            # Assess solvency position
            assessment = self._assess_solvency_position(debt_to_equity, debt_to_assets)
            
            return {
                'debt_to_equity': debt_to_equity,
                'debt_to_assets': debt_to_assets,
                'equity_ratio': equity_ratio,
                'tangible_assets_ratio': tangible_assets_ratio,
                'goodwill_percentage': goodwill_percentage,
                'score': solvency_score,
                'assessment': assessment,
                'financial_leverage': debt_to_equity,
                'capital_structure_analysis': self._analyze_capital_structure(latest_bs)
            }
            
        except Exception as e:
            logger.error("Error in solvency analysis", error=str(e))
            raise CalculationError(f"Solvency analysis failed: {str(e)}", "solvency")
    
    async def analyze_cash_flow_quality(self, cash_flows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cash flow quality and sustainability"""
        
        if not cash_flows:
            raise InsufficientDataError("No cash flow data available", 1, 0)
        
        try:
            latest_cf = cash_flows[0]  # Most recent
            
            # Calculate free cash flow
            operating_cf = latest_cf.get('operating_cash_flow', 0) or 0
            capex = abs(latest_cf.get('capital_expenditures', 0) or 0)
            free_cash_flow = operating_cf - capex
            
            # Calculate cash flow ratios
            ocf_to_sales = self._safe_divide(
                latest_cf.get('operating_cash_flow'),
                latest_cf.get('revenue')  # This would need to come from income statement
            )
            
            ocf_to_net_income = self._safe_divide(
                latest_cf.get('operating_cash_flow'),
                latest_cf.get('net_income')
            )
            
            # Calculate capex intensity
            capex_intensity = self._safe_divide(
                abs(latest_cf.get('capital_expenditures', 0)),
                latest_cf.get('operating_cash_flow', 1)
            ) or 0
            
            # Assess operating cash flow quality
            operating_quality = self._assess_operating_cf_quality(latest_cf, cash_flows)
            
            # Calculate cash flow stability
            fcf_stability = self._calculate_fcf_stability(cash_flows)
            
            # Calculate cash conversion metrics
            cash_conversion_cycle = self._estimate_cash_conversion_cycle(cash_flows)
            
            return {
                'latest_fcf': free_cash_flow,
                'fcf_margin': self._safe_divide(free_cash_flow, latest_cf.get('revenue', 1)),
                'operating_quality': operating_quality,
                'ocf_to_sales': ocf_to_sales,
                'ocf_to_net_income': ocf_to_net_income,
                'capex_intensity': capex_intensity,
                'fcf_stability': fcf_stability,
                'cash_conversion_cycle': cash_conversion_cycle,
                'cash_generation_trends': self._analyze_cash_generation_trends(cash_flows)
            }
            
        except Exception as e:
            logger.error("Error in cash flow analysis", error=str(e))
            raise CalculationError(f"Cash flow analysis failed: {str(e)}", "cash_flow")
    
    async def comprehensive_analysis(
        self,
        income_statements: List[Dict[str, Any]],
        balance_sheets: List[Dict[str, Any]],
        cash_flows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comprehensive financial analysis across all statements"""
        
        try:
            # Perform individual analyses
            income_analysis = await self.analyze_income_trends(income_statements) if income_statements else {}
            liquidity_analysis = await self.analyze_liquidity(balance_sheets) if balance_sheets else {}
            solvency_analysis = await self.analyze_solvency(balance_sheets) if balance_sheets else {}
            cash_flow_analysis = await self.analyze_cash_flow_quality(cash_flows) if cash_flows else {}
            
            # Calculate overall scores
            profitability_score = self._calculate_profitability_score(income_statements)
            liquidity_score = liquidity_analysis.get('score', 5.0)
            solvency_score = solvency_analysis.get('score', 5.0)
            efficiency_score = self._calculate_efficiency_score(income_statements, balance_sheets)
            growth_score = self._calculate_growth_score(income_statements)
            
            # Calculate overall financial health score
            overall_score = self._calculate_overall_score(
                profitability_score, liquidity_score, solvency_score, 
                efficiency_score, growth_score
            )
            
            # Generate insights and recommendations
            insights = self._generate_insights(
                income_analysis, liquidity_analysis, solvency_analysis, cash_flow_analysis
            )
            
            # Identify risk factors and opportunities
            risk_factors = self._identify_risk_factors(
                income_analysis, liquidity_analysis, solvency_analysis, cash_flow_analysis
            )
            
            opportunities = self._identify_opportunities(
                income_analysis, liquidity_analysis, solvency_analysis, cash_flow_analysis
            )
            
            return {
                'overall_score': overall_score,
                'profitability_score': profitability_score,
                'liquidity_score': liquidity_score,
                'solvency_score': solvency_score,
                'efficiency_score': efficiency_score,
                'growth_score': growth_score,
                'insights': insights,
                'risk_factors': risk_factors,
                'opportunities': opportunities,
                'summary': self._generate_executive_summary(overall_score, insights),
                'analysis_date': datetime.utcnow(),
                'confidence_level': self._calculate_analysis_confidence(
                    income_statements, balance_sheets, cash_flows
                )
            }
            
        except Exception as e:
            logger.error("Error in comprehensive analysis", error=str(e))
            raise CalculationError(f"Comprehensive analysis failed: {str(e)}", "comprehensive")
    
    # Helper methods for trend calculations
    def _calculate_revenue_trend(self, statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate revenue trend and growth rates"""
        revenues = [stmt.get('revenue') for stmt in statements if stmt.get('revenue') is not None and stmt.get('revenue') > 0]
        
        if len(revenues) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate year-over-year growth rates
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] != 0:
                growth_rate = (revenues[i] - revenues[i-1]) / revenues[i-1]
                growth_rates.append(growth_rate)
        
        if not growth_rates:
            return {'trend': 'insufficient_data'}
        
        avg_growth = mean(growth_rates)
        
        # Determine trend
        if avg_growth > 0.05:
            trend = 'increasing'
        elif avg_growth < -0.05:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        # Calculate CAGR for 3 years if available
        cagr_3y = None
        if len(revenues) >= 3:
            initial_revenue = revenues[-3]
            final_revenue = revenues[-1]
            if initial_revenue and initial_revenue > 0 and final_revenue and final_revenue > 0:
                cagr_3y = ((final_revenue / initial_revenue) ** (1/2)) - 1
        
        return {
            'trend': trend,
            'avg_growth_rate': avg_growth,
            'cagr_3y': cagr_3y,
            'growth_rates': growth_rates
        }
    
    def _calculate_margin_trends(self, statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate margin trends"""
        gross_margins = []
        operating_margins = []
        net_margins = []
        
        for stmt in statements:
            revenue = stmt.get('revenue')
            if revenue is not None and revenue > 0:
                if stmt.get('gross_profit') is not None:
                    gross_margins.append(stmt['gross_profit'] / revenue)
                if stmt.get('operating_income') is not None:
                    operating_margins.append(stmt['operating_income'] / revenue)
                if stmt.get('net_income') is not None:
                    net_margins.append(stmt['net_income'] / revenue)
        
        return {
            'gross_margin_trend': self._determine_trend(gross_margins),
            'operating_margin_trend': self._determine_trend(operating_margins),
            'net_margin_trend': self._determine_trend(net_margins),
            'overall_trend': self._determine_trend(net_margins)  # Use net margin as overall
        }
    
    def _calculate_growth_rates(self, statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate various growth rates"""
        if len(statements) < 2:
            return {}
        
        latest = statements[0]
        previous = statements[1]
        
        growth_rates = {}
        
        for metric in ['revenue', 'gross_profit', 'operating_income', 'net_income']:
            current = latest.get(metric)
            prior = previous.get(metric)
            
            if current is not None and prior is not None and prior != 0:
                growth_rates[f'{metric}_growth'] = (current - prior) / prior
        
        return growth_rates
    
    def _assess_earnings_quality(self, statements: List[Dict[str, Any]]) -> str:
        """Assess the quality of earnings"""
        if not statements:
            return 'unknown'
        
        latest = statements[0]
        
        # Check for consistent profitability
        net_income = latest.get('net_income') or 0
        operating_income = latest.get('operating_income') or 0
        
        if net_income <= 0:
            return 'poor'
        
        if operating_income <= 0:
            return 'weak'
        
        # Check operating income vs net income ratio
        if net_income > 0 and operating_income > 0:
            ratio = net_income / operating_income
            if ratio > 1.2:  # Net income significantly higher than operating income
                return 'questionable'
            elif ratio >= 0.8:
                return 'strong'
            else:
                return 'medium'
        
        return 'medium'
    
    def _calculate_liquidity_score(self, current_ratio: float, quick_ratio: float, cash_ratio: float) -> float:
        """Calculate liquidity score on 1-10 scale"""
        score = 5.0  # Base score
        
        # Current ratio scoring
        if current_ratio:
            if current_ratio >= 2.0:
                score += 2.0
            elif current_ratio >= 1.5:
                score += 1.0
            elif current_ratio >= 1.0:
                score += 0.0
            else:
                score -= 2.0
        
        # Quick ratio scoring
        if quick_ratio:
            if quick_ratio >= 1.0:
                score += 1.5
            elif quick_ratio >= 0.7:
                score += 0.5
            else:
                score -= 1.0
        
        # Cash ratio scoring
        if cash_ratio:
            if cash_ratio >= 0.3:
                score += 1.5
            elif cash_ratio >= 0.1:
                score += 0.5
            else:
                score -= 0.5
        
        return max(1.0, min(10.0, score))
    
    def _assess_liquidity_position(self, current_ratio: float, quick_ratio: float, cash_ratio: float) -> str:
        """Assess overall liquidity position"""
        if not current_ratio:
            return 'unknown'
        
        if current_ratio >= 2.0 and quick_ratio >= 1.0:
            return 'excellent'
        elif current_ratio >= 1.5 and quick_ratio >= 0.8:
            return 'good'
        elif current_ratio >= 1.0 and quick_ratio >= 0.5:
            return 'adequate'
        elif current_ratio >= 0.8:
            return 'tight'
        else:
            return 'poor'
    
    def _calculate_solvency_score(self, debt_to_equity: float, debt_to_assets: float, equity_ratio: float) -> float:
        """Calculate solvency score on 1-10 scale"""
        score = 5.0  # Base score
        
        # Debt-to-equity scoring (lower is better)
        if debt_to_equity:
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
        
        # Debt-to-assets scoring
        if debt_to_assets:
            if debt_to_assets <= 0.3:
                score += 1.5
            elif debt_to_assets <= 0.5:
                score += 0.5
            elif debt_to_assets <= 0.7:
                score += 0.0
            else:
                score -= 1.5
        
        return max(1.0, min(10.0, score))
    
    def _assess_solvency_position(self, debt_to_equity: float, debt_to_assets: float) -> str:
        """Assess overall solvency position"""
        if not debt_to_equity or not debt_to_assets:
            return 'unknown'
        
        if debt_to_equity <= 0.3 and debt_to_assets <= 0.3:
            return 'excellent'
        elif debt_to_equity <= 0.6 and debt_to_assets <= 0.5:
            return 'good'
        elif debt_to_equity <= 1.0 and debt_to_assets <= 0.7:
            return 'adequate'
        elif debt_to_equity <= 2.0:
            return 'concerning'
        else:
            return 'poor'
    
    # Utility methods
    def _safe_divide(self, numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
        """Safely divide two numbers"""
        if numerator is None or denominator is None or denominator == 0:
            return None
        return numerator / denominator
    
    def _determine_trend(self, values: List[float]) -> str:
        """Determine trend from a list of values"""
        if len(values) < 2:
            return 'insufficient_data'
        
        # Calculate trend using linear regression slope
        x = list(range(len(values)))
        n = len(values)
        
        slope = (n * sum(x[i] * values[i] for i in range(n)) - sum(x) * sum(values)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
        
        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_data_completeness(self, statements: List[Dict[str, Any]]) -> float:
        """Calculate data completeness score"""
        if not statements:
            return 0.0
        
        key_fields = ['revenue', 'net_income', 'operating_income', 'gross_profit']
        total_fields = len(key_fields) * len(statements)
        filled_fields = 0
        
        for stmt in statements:
            for field in key_fields:
                if stmt.get(field) is not None:
                    filled_fields += 1
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    # Additional helper methods would continue here...
    # For brevity, I'll include key remaining methods
    
    def _calculate_profitability_score(self, income_statements: List[Dict[str, Any]]) -> float:
        """Calculate profitability score"""
        if not income_statements:
            return 5.0
        
        latest = income_statements[0]
        revenue = latest.get('revenue') or 1
        
        if revenue <= 0:
            return 1.0
        
        net_income = latest.get('net_income') or 0
        net_margin = net_income / revenue
        
        if net_margin >= 0.20:
            return 9.0
        elif net_margin >= 0.15:
            return 8.0
        elif net_margin >= 0.10:
            return 7.0
        elif net_margin >= 0.05:
            return 6.0
        elif net_margin >= 0:
            return 5.0
        else:
            return 2.0
    
    def _calculate_efficiency_score(self, income_statements: List[Dict[str, Any]], balance_sheets: List[Dict[str, Any]]) -> float:
        """Calculate operational efficiency score"""
        if not income_statements or not balance_sheets:
            return 5.0
        
        # Asset turnover calculation
        revenue = income_statements[0].get('revenue') or 0
        total_assets = balance_sheets[0].get('total_assets') or 1
        
        asset_turnover = revenue / total_assets if total_assets > 0 else 0
        
        if asset_turnover >= 1.5:
            return 9.0
        elif asset_turnover >= 1.0:
            return 7.0
        elif asset_turnover >= 0.5:
            return 5.0
        else:
            return 3.0
    
    def _calculate_growth_score(self, income_statements: List[Dict[str, Any]]) -> float:
        """Calculate growth score"""
        if len(income_statements) < 2:
            return 5.0
        
        revenue_trend = self._calculate_revenue_trend(income_statements)
        avg_growth = revenue_trend.get('avg_growth_rate', 0)
        
        if avg_growth >= 0.20:
            return 9.0
        elif avg_growth >= 0.10:
            return 8.0
        elif avg_growth >= 0.05:
            return 7.0
        elif avg_growth >= 0:
            return 5.0
        else:
            return 3.0
    
    def _calculate_overall_score(self, profitability: float, liquidity: float, solvency: float, efficiency: float, growth: float) -> float:
        """Calculate weighted overall financial health score"""
        weights = {
            'profitability': 0.25,
            'liquidity': 0.20,
            'solvency': 0.25,
            'efficiency': 0.15,
            'growth': 0.15
        }
        
        overall = (
            profitability * weights['profitability'] +
            liquidity * weights['liquidity'] +
            solvency * weights['solvency'] +
            efficiency * weights['efficiency'] +
            growth * weights['growth']
        )
        
        return round(overall, 1)
    
    def _generate_insights(self, income_analysis: Dict, liquidity_analysis: Dict, solvency_analysis: Dict, cash_flow_analysis: Dict) -> List[str]:
        """Generate key financial insights"""
        insights = []
        
        # Revenue insights
        if income_analysis.get('revenue_trend') == 'increasing':
            insights.append("Strong revenue growth indicates expanding business operations")
        elif income_analysis.get('revenue_trend') == 'decreasing':
            insights.append("Declining revenue trend requires attention to business strategy")
        
        # Margin insights
        if income_analysis.get('margin_trend') == 'improving':
            insights.append("Improving profit margins demonstrate operational efficiency gains")
        
        # Liquidity insights
        if liquidity_analysis.get('assessment') == 'excellent':
            insights.append("Excellent liquidity position provides financial flexibility")
        elif liquidity_analysis.get('assessment') == 'poor':
            insights.append("Poor liquidity position may indicate cash flow challenges")
        
        # Solvency insights
        if solvency_analysis.get('assessment') == 'excellent':
            insights.append("Conservative debt levels indicate strong financial stability")
        
        return insights
    
    def _identify_risk_factors(self, income_analysis: Dict, liquidity_analysis: Dict, solvency_analysis: Dict, cash_flow_analysis: Dict) -> List[str]:
        """Identify key financial risk factors"""
        risks = []
        
        if income_analysis.get('revenue_trend') == 'decreasing':
            risks.append("Declining revenue trend")
        
        if liquidity_analysis.get('current_ratio', 0) < 1.0:
            risks.append("Current ratio below 1.0 indicates potential liquidity issues")
        
        if solvency_analysis.get('debt_to_equity', 0) > 2.0:
            risks.append("High debt-to-equity ratio indicates elevated financial leverage")
        
        return risks
    
    def _identify_opportunities(self, income_analysis: Dict, liquidity_analysis: Dict, solvency_analysis: Dict, cash_flow_analysis: Dict) -> List[str]:
        """Identify key financial opportunities"""
        opportunities = []
        
        if liquidity_analysis.get('cash_ratio', 0) > 0.5:
            opportunities.append("Strong cash position enables strategic investments")
        
        if income_analysis.get('margin_trend') == 'improving':
            opportunities.append("Improving margins suggest successful cost management")
        
        return opportunities
    
    def _generate_executive_summary(self, overall_score: float, insights: List[str]) -> str:
        """Generate executive summary"""
        if overall_score >= 8.0:
            health = "excellent"
        elif overall_score >= 6.0:
            health = "good"
        elif overall_score >= 4.0:
            health = "fair"
        else:
            health = "poor"
        
        summary = f"Overall financial health is {health} with a score of {overall_score}/10. "
        
        if insights:
            summary += f"Key highlights: {'. '.join(insights[:3])}."
        
        return summary
    
    def _calculate_analysis_confidence(self, income_statements: List, balance_sheets: List, cash_flows: List) -> float:
        """Calculate confidence level of the analysis"""
        data_sources = 0
        if income_statements:
            data_sources += 1
        if balance_sheets:
            data_sources += 1
        if cash_flows:
            data_sources += 1
        
        base_confidence = data_sources / 3.0
        
        # Adjust for data quality
        total_periods = len(income_statements) + len(balance_sheets) + len(cash_flows)
        if total_periods >= 12:  # 4 years of all statements
            base_confidence *= 1.2
        elif total_periods >= 6:  # 2 years of all statements
            base_confidence *= 1.1
        
        return min(base_confidence, 1.0)
    
    # Additional placeholder methods for completeness
    def _calculate_liquidity_trends(self, balance_sheets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate liquidity trends over time"""
        return {}  # Implementation would analyze trends over multiple periods
    
    def _get_liquidity_benchmarks(self, current_ratio: float, quick_ratio: float) -> Dict[str, Any]:
        """Get industry benchmarks for liquidity ratios"""
        return {
            'industry_avg_current_ratio': 1.5,
            'industry_avg_quick_ratio': 1.0
        }
    
    def _calculate_tangible_assets_ratio(self, balance_sheet: Dict[str, Any]) -> Optional[float]:
        """Calculate tangible assets ratio"""
        total_assets = balance_sheet.get('total_assets', 0)
        intangible_assets = balance_sheet.get('intangible_assets', 0) or 0
        goodwill = balance_sheet.get('goodwill', 0) or 0
        
        if total_assets > 0:
            return (total_assets - intangible_assets - goodwill) / total_assets
        return None
    
    def _calculate_goodwill_percentage(self, balance_sheet: Dict[str, Any]) -> Optional[float]:
        """Calculate goodwill as percentage of total assets"""
        return self._safe_divide(
            balance_sheet.get('goodwill'),
            balance_sheet.get('total_assets')
        )
    
    def _analyze_capital_structure(self, balance_sheet: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze capital structure"""
        return {
            'debt_composition': 'mixed',
            'equity_composition': 'common_stock_dominant'
        }
    
    def _assess_operating_cf_quality(self, latest_cf: Dict[str, Any], cash_flows: List[Dict[str, Any]]) -> str:
        """Assess operating cash flow quality"""
        ocf = latest_cf.get('operating_cash_flow', 0)
        net_income = latest_cf.get('net_income', 0)
        
        if ocf > net_income and ocf > 0:
            return 'strong'
        elif ocf > 0:
            return 'medium'
        else:
            return 'weak'
    
    def _calculate_fcf_stability(self, cash_flows: List[Dict[str, Any]]) -> str:
        """Calculate free cash flow stability"""
        if len(cash_flows) < 3:
            return 'insufficient_data'
        
        fcf_values = []
        for cf in cash_flows:
            ocf = cf.get('operating_cash_flow', 0) or 0
            capex = abs(cf.get('capital_expenditures', 0) or 0)
            fcf = ocf - capex
            fcf_values.append(fcf)
        
        positive_count = sum(1 for fcf in fcf_values if fcf > 0)
        
        if positive_count == len(fcf_values):
            return 'very_stable'
        elif positive_count >= len(fcf_values) * 0.8:
            return 'stable'
        else:
            return 'volatile'
    
    def _estimate_cash_conversion_cycle(self, cash_flows: List[Dict[str, Any]]) -> Optional[int]:
        """Estimate cash conversion cycle"""
        # This would require more detailed working capital analysis
        # For now, return a placeholder
        return 45  # Days
    
    def _analyze_cash_generation_trends(self, cash_flows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cash generation trends"""
        return {
            'operating_cf_trend': 'stable',
            'fcf_trend': 'improving'
        }

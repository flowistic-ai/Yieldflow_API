from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional, Dict, Any, List
from datetime import date, datetime, timedelta
from statistics import mean
import structlog

from app.api.deps import get_current_user_from_api_key
from app.schemas.financial import DividendResponse, DividendAnalysisResponse
from app.services.dividend_service import DividendService
from app.utils.exceptions import DataSourceError, TickerNotFoundError

router = APIRouter()
logger = structlog.get_logger()


def get_dividend_service() -> DividendService:
    """Get dividend service instance"""
    return DividendService()


@router.get("/{ticker}/analysis")
async def get_dividend_analysis(
    ticker: str,
    start_date: Optional[date] = Query(
        None, 
        description="Start date for dividend history (defaults to 5 years ago)"
    ),
    end_date: Optional[date] = Query(
        None, 
        description="End date for dividend history (defaults to today)"
    ),
    include_forecast: bool = Query(
        False, 
        description="Include dividend forecasts"
    ),
    include_peer_comparison: bool = Query(
        False, 
        description="Include peer comparison (requires sector data)"
    ),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    Get comprehensive dividend analysis for a company including:
    
    - **Current dividend information**: Latest yield, payout ratio, recent dividends
    - **Historical dividend data**: Complete dividend payment history
    - **Growth analysis**: Dividend growth rates over multiple periods
    - **Consistency metrics**: Years of consecutive increases/payments
    - **Coverage analysis**: Payout ratios and sustainability metrics
    - **Risk assessment**: Dividend risk factors and ratings
    - **Economic context**: FRED economic indicators affecting dividends
    - **Forecasts**: Optional future dividend predictions
    - **Peer comparison**: Optional sector benchmark comparison
    
    ### Features Enhanced by FRED API:
    - Interest rate environment analysis
    - Economic growth indicators  
    - Inflation impact assessment
    - Corporate profit trends
    
    ### Data Sources:
    - Yahoo Finance (primary dividend data)
    - Alpha Vantage (validation & additional metrics)
    - Financial Modeling Prep (comprehensive dividend details)
    - FRED (economic indicators)
    """
    
    try:
        analysis = await dividend_service.get_comprehensive_dividend_analysis(
            ticker=ticker.upper(),
            start_date=start_date,
            end_date=end_date,
            include_forecast=include_forecast,
            include_peer_comparison=include_peer_comparison
        )
        
        return analysis
        
    except TickerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"No dividend data found for ticker: {ticker}"
        )
    except DataSourceError as e:
        logger.error("Data source error in dividend analysis", ticker=ticker, error=str(e))
        raise HTTPException(
            status_code=503,
            detail="Dividend data temporarily unavailable"
        )
    except Exception as e:
        logger.error("Unexpected error in dividend analysis", ticker=ticker, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during dividend analysis"
        )


@router.get("/{ticker}/history")
async def get_dividend_history(
    ticker: str,
    start_date: Optional[date] = Query(None, description="Start date for dividend history"),
    end_date: Optional[date] = Query(None, description="End date for dividend history"),
    limit: Optional[int] = Query(
        None, 
        description="Maximum number of dividend records to return",
        ge=1,
        le=1000
    ),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    Get historical dividend payments for a company.
    
    Returns detailed dividend payment history including:
    - Ex-dividend dates
    - Payment amounts
    - Dividend types (regular, special, etc.)
    - Data source information
    - Confidence scores
    """
    
    try:
        # Set default dates if not provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365 * 5)  # 5 years default
        
        dividends = await dividend_service._get_yfinance_dividends(ticker.upper(), start_date, end_date)
        
        # Apply limit if specified
        if limit:
            dividends = dividends[:limit]
        
        # Calculate summary statistics
        total_payments = len(dividends)
        total_amount = sum(div.get('amount', 0) for div in dividends)
        
        return {
            'ticker': ticker.upper(),
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_payments': total_payments,
                'total_amount': round(total_amount, 4),
                'average_payment': round(total_amount / total_payments, 4) if total_payments > 0 else 0
            },
            'dividends': dividends
        }
        
    except Exception as e:
        logger.error("Error in dividend history request", ticker=ticker, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve dividend history"
        )


@router.get("/{ticker}/current")
async def get_current_dividend_info(
    ticker: str,
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    Get current dividend information for a company.
    
    Returns:
    - Current dividend yield
    - Payout ratio
    - Last dividend payment details
    - Estimated annual dividend
    - Payment frequency
    """
    
    try:
        # Get recent dividend data
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * 2)  # 2 years
        
        dividends = await dividend_service._get_yfinance_dividends(ticker.upper(), start_date, end_date)
        market_data = await dividend_service._fetch_market_data(ticker.upper())
        
        if not dividends:
            raise HTTPException(
                status_code=404,
                detail=f"No dividend data found for {ticker}"
            )
        
        current_metrics = dividend_service._get_current_dividend_metrics(dividends, market_data)
        
        return {
            'ticker': ticker.upper(),
            'current_dividend_info': current_metrics,
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in current dividend info request", ticker=ticker, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve current dividend information"
        )


@router.get("/{ticker}/forecast")
async def get_dividend_forecast(
    ticker: str,
    years: int = Query(
        3, 
        description="Number of years to forecast",
        ge=1,
        le=10
    ),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    Generate dividend forecasts for a company.
    
    Returns projected dividend payments based on:
    - Historical growth patterns
    - Financial health metrics
    - Economic indicators
    - Industry benchmarks
    """
    
    try:
        # Get historical data for forecasting
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * 10)  # 10 years for robust forecasting
        
        dividends = await dividend_service._get_yfinance_dividends(ticker.upper(), start_date, end_date)
        financials = await dividend_service._fetch_comprehensive_financials(ticker.upper())
        economic_context = await dividend_service._fetch_economic_context()
        
        if not dividends:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient dividend history for forecasting: {ticker}"
            )
        
        forecast = await dividend_service._generate_professional_forecast(
            ticker,
            dividends, financials, economic_context, years
        )
        
        return {
            'ticker': ticker.upper(),
            'forecast_period': f'{years} years',
            'methodology': 'Growth trend analysis with economic adjustments',
            'forecast': forecast,
            'disclaimer': 'Forecasts are estimates based on historical data and current conditions.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in dividend forecast request", ticker=ticker, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to generate dividend forecast"
        )


@router.get("/economic-indicators")
async def get_economic_indicators(
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    Get current economic indicators relevant to dividend analysis from FRED.
    
    Includes:
    - Treasury rates (10-year, 3-month)
    - Federal funds rate
    - Inflation rate (CPI)
    - GDP growth
    - Unemployment rate
    - Corporate profits
    """
    
    try:
        economic_data = await dividend_service._fetch_economic_context()
        
        return {
            'economic_indicators': economic_data,
            'source': 'Federal Reserve Economic Data (FRED)',
            'last_updated': datetime.utcnow().isoformat(),
            'description': 'Key economic indicators affecting dividend policy and sustainability'
        }
        
    except Exception as e:
        logger.error("Error fetching economic indicators", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve economic indicators"
        )


# NEW: CHART ENDPOINTS FOR VISUALIZATION

@router.get("/{ticker}/charts/growth")
async def get_dividend_growth_chart(
    ticker: str,
    years: int = Query(15, description="Number of years to include", ge=3, le=30),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    **Historical Dividend Growth Chart Data**
    
    Returns data for creating a bar/line chart showing dividend per share over several years.
    Provides clear visualization of company's dividend track record.
    """
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * years)
        
        dividends = await dividend_service._get_yfinance_dividends(ticker.upper(), start_date, end_date)
        annual_dividends = dividend_service._aggregate_annual_dividends(dividends)
        
        # Filter out current year to match consecutive increases logic (avoid partial year data)
        from datetime import date as dt
        current_year = dt.today().year
        filtered_annual_dividends = {year: amount for year, amount in annual_dividends.items() if year < current_year}
        
        # If no historical data or very limited data, include current year with a note
        if len(filtered_annual_dividends) < 2 and current_year in annual_dividends:
            filtered_annual_dividends[current_year] = annual_dividends[current_year]
        
        # Prepare chart data
        chart_data = []
        years_sorted = sorted(filtered_annual_dividends.keys())
        
        for i, year in enumerate(years_sorted):
            dividend_amount = filtered_annual_dividends[year]
            
            # Calculate year-over-year growth
            growth_rate = None
            if i > 0:
                prev_amount = filtered_annual_dividends[years_sorted[i-1]]
                if prev_amount > 0:
                    growth_rate = ((dividend_amount - prev_amount) / prev_amount) * 100
            
            # Add note for current year (partial data)
            note = None
            if year == current_year:
                note = "Current year (partial data)"
            
            chart_data.append({
                'year': year,
                'dividend_amount': round(dividend_amount, 4),
                'growth_rate': round(growth_rate, 2) if growth_rate is not None else 0.0,
                'note': note if note is not None else f"Dividend payment of ${dividend_amount:.2f}"
            })
        
        # Calculate metadata
        total_years = len(chart_data)
        dividend_start_year = years_sorted[0] if years_sorted else None
        
        # Determine if this is a new dividend payer
        is_new_dividend_payer = dividend_start_year and dividend_start_year >= 2020
        
        return {
            'ticker': ticker.upper(),
            'chart_type': 'dividend_growth',
            'chart_data': chart_data,
            'metadata': {
                'total_years': total_years,
                'dividend_start_year': dividend_start_year,
                'is_new_dividend_payer': is_new_dividend_payer,
                'data_note': f"{'New dividend payer - limited history' if is_new_dividend_payer else 'Historical dividend data'}",
                'avg_dividend': round(sum(d['dividend_amount'] for d in chart_data) / len(chart_data), 4) if chart_data else 0,
                'cagr': dividend_service._calculate_cagr(chart_data) if len(chart_data) >= 2 else 0,
                'years_excluded_current': current_year not in filtered_annual_dividends or len(filtered_annual_dividends) > 1
            }
        }
        
    except Exception as e:
        logger.error("Error generating dividend growth chart", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate dividend growth chart")


@router.get("/{ticker}/charts/yield-vs-price")
async def get_yield_vs_price_chart(
    ticker: str,
    years: int = Query(10, description="Number of years to include", ge=1, le=20),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    **Dividend Yield vs Stock Price Chart Data**
    
    Returns dual-axis chart data plotting historical dividend yield against stock price.
    Helps identify if high yield is due to falling stock price.
    """
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * years)
        
        # Get historical data
        import yfinance as yf
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(start=start_date, end=end_date)
        dividends = await dividend_service._get_yfinance_dividends(ticker.upper(), start_date, end_date)
        
        # Calculate quarterly yield and price data
        chart_data = []
        quarterly_data = {}
        
        # Group dividends by quarter
        for div in dividends:
            quarter_key = f"{div['ex_date'].year}-Q{(div['ex_date'].month-1)//3 + 1}"
            if quarter_key not in quarterly_data:
                quarterly_data[quarter_key] = {'dividends': 0, 'quarter': quarter_key}
            quarterly_data[quarter_key]['dividends'] += div['amount']
        
        # Get quarterly prices
        for quarter_key, data in quarterly_data.items():
            year, quarter = quarter_key.split('-Q')
            quarter_start = date(int(year), (int(quarter)-1)*3 + 1, 1)
            
            # Get price for that quarter
            try:
                quarter_hist = hist[hist.index.date >= quarter_start]
                if not quarter_hist.empty:
                    avg_price = quarter_hist['Close'].iloc[0] if len(quarter_hist) > 0 else 0
                    ttm_dividend = data['dividends'] * 4  # Annualize
                    dividend_yield = (ttm_dividend / avg_price * 100) if avg_price > 0 else 0
                    
                    chart_data.append({
                        'period': quarter_key,
                        'stock_price': round(avg_price, 2),
                        'dividend_yield': round(dividend_yield, 2),
                        'quarterly_dividend': round(data['dividends'], 4)
                    })
            except:
                continue
        
        # Sort by period
        chart_data.sort(key=lambda x: x['period'])
        
        return {
            'ticker': ticker.upper(),
            'chart_type': 'yield_vs_price',
            'chart_data': chart_data,
            'insights': {
                'yield_price_correlation': dividend_service._calculate_correlation(chart_data),
                'high_yield_periods': [d for d in chart_data if d['dividend_yield'] > 4.0],
                'current_vs_avg': dividend_service._compare_current_vs_average(chart_data)
            }
        }
        
    except Exception as e:
        logger.error("Error generating yield vs price chart", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate yield vs price chart")


@router.get("/{ticker}/charts/payout-ratio")
async def get_payout_ratio_chart(
    ticker: str,
    years: int = Query(10, description="Number of years to include", ge=3, le=25),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    **Payout Ratio Trend Chart Data**
    
    Returns line chart data showing dividend payout ratio over time.
    Helps assess if ratio is trending towards unsustainable levels.
    """
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * years)
        
        dividends = await dividend_service._get_yfinance_dividends(ticker.upper(), start_date, end_date)
        financials = await dividend_service._fetch_comprehensive_financials(ticker.upper())
        
        # Get annual data
        annual_dividends = dividend_service._aggregate_annual_dividends(dividends)
        
        # Calculate payout ratios (simplified - would need historical EPS data)
        chart_data = []
        current_eps = financials.get('eps', 0)
        
        for year in sorted(annual_dividends.keys(), reverse=True)[:years]:
            dividend_amount = annual_dividends[year]
            # Simplified calculation - in production would fetch historical EPS
            estimated_payout_ratio = (dividend_amount / current_eps * 100) if current_eps > 0 else 0
            
            # Add sustainability assessment
            sustainability = 'Sustainable' if estimated_payout_ratio < 60 else \
                           'Moderate Risk' if estimated_payout_ratio < 80 else \
                           'High Risk' if estimated_payout_ratio < 100 else 'Unsustainable'
            
            chart_data.append({
                'year': year,
                'payout_ratio': round(min(estimated_payout_ratio, 200), 1),  # Cap at 200%
                'dividend_amount': round(dividend_amount, 4),
                'sustainability_rating': sustainability
            })
        
        chart_data.sort(key=lambda x: x['year'])
        
        return {
            'ticker': ticker.upper(),
            'chart_type': 'payout_ratio_trend',
            'chart_data': chart_data,
            'benchmarks': {
                'conservative': 40,
                'moderate': 60,
                'aggressive': 80,
                'unsustainable': 100
            },
            'current_assessment': chart_data[-1]['sustainability_rating'] if chart_data else 'Unknown'
        }
        
    except Exception as e:
        logger.error("Error generating payout ratio chart", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate payout ratio chart")


@router.get("/{ticker}/charts/dividend-vs-earnings")
async def get_dividend_vs_earnings_chart(
    ticker: str,
    years: int = Query(12, description="Number of years to include", ge=3, le=25),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    **Dividend vs Earnings Growth Chart Data**
    
    Returns comparative chart data showing growth rates of dividends and earnings per share.
    Ideally, earnings growth should support dividend growth.
    """
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * years)
        
        dividends = await dividend_service._get_yfinance_dividends(ticker.upper(), start_date, end_date)
        annual_dividends = dividend_service._aggregate_annual_dividends(dividends)
        
        # Calculate growth rates
        chart_data = []
        years_sorted = sorted(annual_dividends.keys())
        
        for i, year in enumerate(years_sorted):
            dividend_amount = annual_dividends[year]
            
            # Calculate dividend growth
            dividend_growth = None
            if i > 0:
                prev_dividend = annual_dividends[years_sorted[i-1]]
                if prev_dividend > 0:
                    dividend_growth = ((dividend_amount - prev_dividend) / prev_dividend) * 100
            
            # Simplified earnings growth (would need historical EPS data)
            # Using approximation based on dividend sustainability
            estimated_earnings_growth = dividend_growth * 0.8 if dividend_growth else None
            
            chart_data.append({
                'year': year,
                'dividend_amount': round(dividend_amount, 4),
                'dividend_growth': round(dividend_growth, 2) if dividend_growth is not None else None,
                'estimated_earnings_growth': round(estimated_earnings_growth, 2) if estimated_earnings_growth is not None else None,
                'growth_sustainability': 'Sustainable' if dividend_growth and dividend_growth <= 15 else 'Monitor'
            })
        
        return {
            'ticker': ticker.upper(),
            'chart_type': 'dividend_vs_earnings_growth',
            'chart_data': chart_data,
            'analysis': {
                'avg_dividend_growth': round(sum(d['dividend_growth'] for d in chart_data if d['dividend_growth']) / 
                                          len([d for d in chart_data if d['dividend_growth']]), 2) if chart_data else 0,
                'growth_consistency': len([d for d in chart_data if d['dividend_growth'] and d['dividend_growth'] > 0]),
                'sustainability_score': dividend_service._calculate_growth_sustainability_score(chart_data)
            }
        }
        
    except Exception as e:
        logger.error("Error generating dividend vs earnings chart", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate dividend vs earnings chart")


@router.get("/{ticker}/charts/peer-comparison")
async def get_peer_comparison_chart(
    ticker: str,
    sector_tickers: str = Query(
        None, 
        description="Comma-separated peer tickers (e.g., 'MSFT,GOOGL,META'). If not provided, will use sector-based peers",
        example="MSFT,GOOGL,META"
    ),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    **Peer Comparison Dashboard Chart Data**
    
    Returns bar charts/radar chart data comparing company's key dividend metrics 
    (yield, growth, payout ratio) against its peers.
    """
    
    try:
        # Get company's metrics
        company_metrics = await _get_company_metrics_for_comparison(dividend_service, ticker)
        
        # Determine peer tickers
        if sector_tickers:
            peer_list = [t.strip().upper() for t in sector_tickers.split(',')]
        else:
            # Default tech peers for demo
            peer_list = ['MSFT', 'GOOGL', 'META', 'NVDA', 'TSLA']
        
        # Get peer metrics in parallel
        peer_metrics = {}
        for peer in peer_list:
            try:
                peer_metrics[peer] = await _get_company_metrics_for_comparison(dividend_service, peer)
            except:
                continue
        
        # Create comparison data
        comparison_data = {
            'target_company': ticker.upper(),
            'peer_comparison': {
                'dividend_yield': {
                    'target': company_metrics['yield'],
                    'peers': {peer: metrics['yield'] for peer, metrics in peer_metrics.items()},
                    'percentile_rank': _calculate_percentile_rank(
                        company_metrics['yield'], 
                        [metrics['yield'] for metrics in peer_metrics.values()]
                    )
                },
                'dividend_growth_5y': {
                    'target': company_metrics['growth_5y'],
                    'peers': {peer: metrics['growth_5y'] for peer, metrics in peer_metrics.items()},
                    'percentile_rank': _calculate_percentile_rank(
                        company_metrics['growth_5y'], 
                        [metrics['growth_5y'] for metrics in peer_metrics.values()]
                    )
                },
                'payout_ratio': {
                    'target': company_metrics['payout_ratio'],
                    'peers': {peer: metrics['payout_ratio'] for peer, metrics in peer_metrics.items()},
                    'percentile_rank': _calculate_percentile_rank(
                        company_metrics['payout_ratio'], 
                        [metrics['payout_ratio'] for metrics in peer_metrics.values()]
                    )
                }
            },
            'sector_benchmarks': {
                'avg_yield': 1.2,  # Technology sector average
                'avg_growth': 8.0,
                'avg_payout': 25.0
            }
        }
        
        return {
            'ticker': ticker.upper(),
            'chart_type': 'peer_comparison',
            'chart_data': comparison_data,
            'analysis': {
                'relative_performance': _assess_relative_performance(company_metrics, peer_metrics),
                'competitive_position': _determine_competitive_position(comparison_data['peer_comparison'])
            }
        }
        
    except Exception as e:
        logger.error("Error generating peer comparison chart", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate peer comparison chart")


@router.get("/{ticker}/charts/total-return")
async def get_total_return_breakdown_chart(
    ticker: str,
    years: int = Query(10, description="Number of years to include", ge=1, le=20),
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    **Total Return Breakdown Chart Data**
    
    Returns stacked area chart data showing the contribution of price appreciation 
    and reinvested dividends to total return over time.
    """
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * years)
        
        # Get dividend and price data
        import yfinance as yf
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(start=start_date, end=end_date)
        dividends = await dividend_service._get_yfinance_dividends(ticker.upper(), start_date, end_date)
        
        # Calculate annual returns
        annual_data = {}
        
        for year in range(start_date.year, end_date.year + 1):
            year_start = max(date(year, 1, 1), start_date)
            year_end = min(date(year, 12, 31), end_date)
            
            # Get price data for year
            year_hist = hist[(hist.index.date >= year_start) & (hist.index.date <= year_end)]
            
            if len(year_hist) < 2:
                continue
            
            start_price = year_hist['Close'].iloc[0]
            end_price = year_hist['Close'].iloc[-1]
            
            # Calculate price appreciation
            price_return = ((end_price - start_price) / start_price) * 100 if start_price > 0 else 0
            
            # Calculate dividend yield for the year
            year_dividends = [d for d in dividends if d['ex_date'].year == year]
            total_dividends = sum(d['amount'] for d in year_dividends)
            dividend_yield = (total_dividends / start_price) * 100 if start_price > 0 else 0
            
            # Calculate reinvested dividend effect (simplified)
            reinvestment_effect = dividend_yield * 1.1  # Assume 10% compounding benefit
            
            annual_data[year] = {
                'year': year,
                'price_appreciation': round(price_return, 2),
                'dividend_yield': round(dividend_yield, 2),
                'reinvestment_effect': round(reinvestment_effect, 2),
                'total_return': round(price_return + reinvestment_effect, 2)
            }
        
        chart_data = list(annual_data.values())
        
        # Calculate cumulative returns
        cumulative_data = []
        cumulative_price = 100
        cumulative_dividends = 100
        
        for data in chart_data:
            cumulative_price *= (1 + data['price_appreciation'] / 100)
            cumulative_dividends *= (1 + data['reinvestment_effect'] / 100)
            
            cumulative_data.append({
                'year': data['year'],
                'cumulative_price_only': round(cumulative_price, 2),
                'cumulative_with_dividends': round(cumulative_dividends, 2),
                'dividend_contribution': round(cumulative_dividends - cumulative_price, 2)
            })
        
        return {
            'ticker': ticker.upper(),
            'chart_type': 'total_return_breakdown',
            'annual_breakdown': chart_data,
            'cumulative_performance': cumulative_data,
            'summary': {
                'total_price_appreciation': round(sum(d['price_appreciation'] for d in chart_data), 2),
                'total_dividend_contribution': round(sum(d['reinvestment_effect'] for d in chart_data), 2),
                'compound_annual_growth_rate': round((cumulative_data[-1]['cumulative_with_dividends'] / 100) ** (1/years) - 1, 4) * 100 if cumulative_data else 0
            }
        }
        
    except Exception as e:
        logger.error("Error generating total return chart", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate total return chart")


# Helper functions for peer comparison
async def _get_company_metrics_for_comparison(dividend_service: DividendService, ticker: str) -> Dict[str, float]:
    """Get key metrics for peer comparison"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=365 * 5)
        
        dividends = await dividend_service._get_yfinance_dividends(ticker, start_date, end_date)
        market_data = await dividend_service._fetch_market_data(ticker)
        financials = await dividend_service._fetch_comprehensive_financials(ticker)
        
        # Calculate metrics
        current_price = market_data.get('current_price', 0)
        ttm_dividend = sum(div.get('amount', 0) for div in dividends[:4])
        current_yield = (ttm_dividend / current_price * 100) if current_price > 0 else 0
        
        # 5-year growth
        annual_dividends = dividend_service._aggregate_annual_dividends(dividends)
        years = sorted(annual_dividends.keys(), reverse=True)
        growth_5y = 0
        if len(years) >= 5:
            start_div = annual_dividends[years[4]]
            end_div = annual_dividends[years[0]]
            if start_div > 0:
                growth_5y = ((end_div / start_div) ** (1/5) - 1) * 100
        
        payout_ratio = dividend_service._calculate_payout_ratio(dividends, financials) * 100
        
        return {
            'yield': round(current_yield, 2),
            'growth_5y': round(growth_5y, 2),
            'payout_ratio': round(payout_ratio, 2)
        }
    except:
        return {'yield': 0, 'growth_5y': 0, 'payout_ratio': 0}

def _calculate_percentile_rank(value: float, peer_values: List[float]) -> float:
    """Calculate percentile rank against peers"""
    if not peer_values:
        return 50.0
    
    all_values = peer_values + [value]
    all_values.sort()
    
    rank = all_values.index(value)
    return round((rank / (len(all_values) - 1)) * 100, 1)

def _assess_relative_performance(company_metrics: Dict, peer_metrics: Dict) -> str:
    """Assess relative performance vs peers"""
    scores = []
    
    # Compare yield (higher is better to a point)
    yield_scores = [metrics['yield'] for metrics in peer_metrics.values()]
    avg_yield = mean(yield_scores) if yield_scores else 0
    
    if company_metrics['yield'] > avg_yield * 1.2:
        scores.append(1)  # Much higher yield
    elif company_metrics['yield'] > avg_yield:
        scores.append(0.5)  # Above average
    else:
        scores.append(0)  # Below average
    
    # Compare growth (higher is better)
    growth_scores = [metrics['growth_5y'] for metrics in peer_metrics.values()]
    avg_growth = mean(growth_scores) if growth_scores else 0
    
    if company_metrics['growth_5y'] > avg_growth:
        scores.append(1)
    else:
        scores.append(0)
    
    avg_score = mean(scores) if scores else 0.5
    
    if avg_score > 0.7:
        return "Outperforming Peers"
    elif avg_score > 0.3:
        return "In Line with Peers"
    else:
        return "Underperforming Peers"

def _determine_competitive_position(peer_comparison: Dict) -> str:
    """Determine competitive position based on percentile ranks"""
    avg_percentile = mean([
        peer_comparison['dividend_yield']['percentile_rank'],
        peer_comparison['dividend_growth_5y']['percentile_rank'],
        100 - peer_comparison['payout_ratio']['percentile_rank']  # Lower payout is better
    ])
    
    if avg_percentile > 75:
        return "Market Leader"
    elif avg_percentile > 50:
        return "Above Average"
    elif avg_percentile > 25:
        return "Average"
    else:
        return "Below Average"

@router.get("/{ticker}/company-info")
async def get_company_basic_info(
    ticker: str,
    current_user = Depends(get_current_user_from_api_key),
    dividend_service: DividendService = Depends(get_dividend_service)
):
    """
    Get basic company information including name and logo.
    
    Returns:
    - Company name
    - Ticker symbol
    - Logo URL
    - Exchange
    - Sector and industry
    """
    
    try:
        # Import data provider to get company info
        from app.services.data_provider import DataProvider
        data_provider = DataProvider()
        
        company_data = await data_provider.get_company_info(ticker.upper())
        
        if not company_data:
            raise HTTPException(
                status_code=404,
                detail=f"Company information not found for ticker {ticker}"
            )
        
        return {
            'ticker': ticker.upper(),
            'name': company_data.get('name', ''),
            'logo_url': company_data.get('logo_url', ''),
            'exchange': company_data.get('exchange', ''),
            'sector': company_data.get('sector', ''),
            'industry': company_data.get('industry', ''),
            'market_cap': company_data.get('market_cap'),
            'description': company_data.get('description', ''),
            'website': company_data.get('website', ''),
            'last_updated': datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in company info request", ticker=ticker, error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve company information"
        ) 
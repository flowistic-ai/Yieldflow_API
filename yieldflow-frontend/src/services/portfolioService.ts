import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_KEY = process.env.REACT_APP_API_KEY || 'yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc';

// Create axios instance with API key
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-API-KEY': API_KEY,
    'Content-Type': 'application/json',
  },
});

// Optimization objectives
export enum OptimizationObjective {
  SHARPE_RATIO = 'sharpe_ratio',
  DIVIDEND_YIELD = 'dividend_yield',
  DIVIDEND_GROWTH = 'dividend_growth',
  BALANCED = 'balanced',
}

// Shrinkage methods
export enum ShrinkageMethod {
  AUTO = 'auto',
  FIXED = 'fixed',
  CUSTOM = 'custom',
}

// Types for portfolio optimization
export interface PortfolioOptimizationRequest {
  tickers: string[];
  objective: OptimizationObjective;
  shrinkage_method?: ShrinkageMethod;
  shrinkage_value?: number;
  anchor_portfolio?: Record<string, number>;
  max_weight?: number;
  min_dividend_yield?: number;
}

// NEPO (News-Enhanced Portfolio Optimization) types
export interface NewsAnalysis {
  ticker: string;
  sentiment_score: number;
  geopolitical_risk: number;
  confidence: number;
  ai_thesis: string;
  news_summary: string;
  last_updated: string;
}

export interface NEPOResult {
  traditional_epo: PortfolioOptimizationResult;
  news_enhanced_portfolio: PortfolioOptimizationResult;
  combined_portfolio: PortfolioOptimizationResult;
  news_analysis: NewsAnalysis[];
  methodology: string;
  gemini_status: string;
  processing_time: number;
  position_sizing: Record<string, {
    shares: number;
    dollar_amount: number;
    percentage: number;
  }>;
}

export interface TimeHorizon {
  SHORT: 'short';
  MEDIUM: 'medium';
  LONG: 'long';
}

export interface AssetContribution {
  weight: number;
  return_contribution: number;
  risk_contribution: number;
  dividend_yield: number;
  dividend_growth: number;
  quality_score: number;
}

export interface RiskMetrics {
  max_weight: number;
  effective_positions: number;
  concentration_risk: number;
  avg_dividend_consistency: number;
}

export interface PortfolioOptimizationResult {
  weights: Record<string, number>;
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  expected_dividend_yield: number;
  risk_metrics: RiskMetrics;
  individual_contributions: Record<string, AssetContribution>;
  optimization_method: string;
  shrinkage_parameter: number;
}

export interface EfficientFrontierPoint {
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  weights: Record<string, number>;
}

export interface EfficientFrontier {
  frontier_points: EfficientFrontierPoint[];
  risk_free_rate: number;
  max_sharpe_portfolio: EfficientFrontierPoint;
}

export interface PortfolioComparison {
  epo_portfolio: PortfolioOptimizationResult;
  equal_weight_portfolio: PortfolioOptimizationResult;
  traditional_mvo?: PortfolioOptimizationResult;
  performance_improvement: Record<string, number>;
}

export interface BacktestResult {
  dates: string[];
  portfolio_values: number[];
  benchmark_values: number[];
  returns: number[];
  cumulative_dividends: number[];
  sharpe_ratio: number;
  max_drawdown: number;
  total_return: number;
  dividend_income: number;
}

export interface PortfolioRiskAnalysis {
  var_95: number;
  cvar_95: number;
  beta: number;
  correlation_with_market: number;
  sector_concentration: Record<string, number>;
  top_10_holdings_weight: number;
}

export interface PortfolioInsights {
  summary: string;
  strengths: string[];
  risks: string[];
  recommendations: string[];
  diversification_score: number;
  quality_score: number;
  esg_score?: number;
}

export interface PortfolioOptimizationFullResult {
  optimization_result: PortfolioOptimizationResult;
  efficient_frontier?: EfficientFrontier;
  comparison?: PortfolioComparison;
  risk_analysis?: PortfolioRiskAnalysis;
  backtest?: BacktestResult;
  insights?: PortfolioInsights;
  timestamp: string;
}

class PortfolioService {
  /**
   * Basic portfolio optimization using Enhanced Portfolio Optimization (EPO)
   */
  async optimizePortfolio(request: PortfolioOptimizationRequest): Promise<PortfolioOptimizationResult> {
    try {
      const response = await apiClient.post('/api/v1/portfolio/optimize', request);
      return response.data;
    } catch (error: any) {
      console.error('Portfolio optimization error:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to optimize portfolio'
      );
    }
  }

  /**
   * Comprehensive portfolio optimization with full analysis
   */
  async optimizePortfolioFull(
    request: PortfolioOptimizationRequest,
    options: {
      include_efficient_frontier?: boolean;
      include_comparison?: boolean;
      include_backtest?: boolean;
    } = {}
  ): Promise<PortfolioOptimizationFullResult> {
    try {
      const params = new URLSearchParams();
      if (options.include_efficient_frontier !== undefined) {
        params.append('include_efficient_frontier', options.include_efficient_frontier.toString());
      }
      if (options.include_comparison !== undefined) {
        params.append('include_comparison', options.include_comparison.toString());
      }
      if (options.include_backtest !== undefined) {
        params.append('include_backtest', options.include_backtest.toString());
      }

      const url = `/api/v1/portfolio/optimize-full${params.toString() ? '?' + params.toString() : ''}`;
      const response = await apiClient.post(url, request);
      return response.data;
    } catch (error: any) {
      console.error('Full portfolio optimization error:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to perform full portfolio analysis'
      );
    }
  }

  /**
   * News-Enhanced Portfolio Optimization (NEPO)
   * Combines traditional EPO with real-time news sentiment analysis
   */
  async optimizeNewsEnhancedPortfolio(
    request: PortfolioOptimizationRequest,
    options: {
      investment_amount?: number;
      time_horizon?: 'short' | 'medium' | 'long';
      include_news_analysis?: boolean;
    } = {}
  ): Promise<NEPOResult> {
    try {
      const params = new URLSearchParams();
      if (options.investment_amount !== undefined) {
        params.append('investment_amount', options.investment_amount.toString());
      }
      if (options.time_horizon !== undefined) {
        params.append('time_horizon', options.time_horizon);
      }
      if (options.include_news_analysis !== undefined) {
        params.append('include_news_analysis', options.include_news_analysis.toString());
      }

      const url = `/api/v1/portfolio/optimize-news-enhanced${params.toString() ? '?' + params.toString() : ''}`;
      const response = await apiClient.post(url, request);
      return response.data;
    } catch (error: any) {
      console.error('NEPO optimization error:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to perform news-enhanced portfolio optimization'
      );
    }
  }

  /**
   * Generate efficient frontier for portfolio
   */
  async getEfficientFrontier(
    tickers: string[],
    objective: OptimizationObjective = OptimizationObjective.SHARPE_RATIO,
    nPoints: number = 20
  ): Promise<EfficientFrontier> {
    try {
      const params = new URLSearchParams();
      tickers.forEach(ticker => params.append('tickers', ticker));
      params.append('objective', objective);
      params.append('n_points', nPoints.toString());

      const response = await apiClient.get(`/api/v1/portfolio/efficient-frontier?${params.toString()}`);
      return response.data;
    } catch (error: any) {
      console.error('Efficient frontier error:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to generate efficient frontier'
      );
    }
  }

  /**
   * Compare optimization methods (EPO vs traditional)
   */
  async compareOptimizationMethods(request: PortfolioOptimizationRequest): Promise<PortfolioComparison> {
    try {
      const response = await apiClient.post('/api/v1/portfolio/compare-methods', request);
      return response.data;
    } catch (error: any) {
      console.error('Method comparison error:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to compare optimization methods'
      );
    }
  }

  /**
   * Backtest portfolio performance
   */
  async backtestPortfolio(
    weights: Record<string, number>,
    tickers: string[],
    startDate: string,
    endDate: string
  ): Promise<BacktestResult> {
    try {
      const params = new URLSearchParams();
      params.append('start_date', startDate);
      params.append('end_date', endDate);

      const response = await apiClient.post(`/api/v1/portfolio/backtest?${params.toString()}`, {
        weights,
        tickers,
      });
      return response.data;
    } catch (error: any) {
      console.error('Portfolio backtest error:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to backtest portfolio'
      );
    }
  }

  /**
   * Validate tickers before optimization
   */
  validateTickers(tickers: string[]): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (tickers.length < 2) {
      errors.push('Portfolio must contain at least 2 securities');
    }

    if (tickers.length > 20) {
      errors.push('Portfolio cannot contain more than 20 securities');
    }

    const invalidTickers = tickers.filter(ticker => 
      !ticker || 
      ticker.trim().length === 0 || 
      !/^[A-Z]{1,5}$/.test(ticker.trim().toUpperCase())
    );

    if (invalidTickers.length > 0) {
      errors.push(`Invalid ticker symbols: ${invalidTickers.join(', ')}`);
    }

    const duplicates = tickers.filter((ticker, index) => tickers.indexOf(ticker) !== index);
    if (duplicates.length > 0) {
      errors.push(`Duplicate tickers: ${duplicates.join(', ')}`);
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Format optimization results for display
   */
  formatOptimizationResult(result: PortfolioOptimizationResult): {
    portfolioWeights: Array<{ ticker: string; weight: number; formattedWeight: string }>;
    expectedReturn: string;
    volatility: string;
    sharpeRatio: string;
    dividendYield: string;
  } {
    const portfolioWeights = Object.entries(result.weights).map(([ticker, weight]) => ({
      ticker,
      weight,
      formattedWeight: `${(weight * 100).toFixed(1)}%`
    }));

    return {
      portfolioWeights,
      expectedReturn: `${(result.expected_return * 100).toFixed(2)}%`,
      volatility: `${(result.volatility * 100).toFixed(2)}%`,
      sharpeRatio: result.sharpe_ratio.toFixed(3),
      dividendYield: `${(result.expected_dividend_yield * 100).toFixed(2)}%`,
    };
  }

  /**
   * Format risk metrics for display
   */
  formatRiskMetrics(riskMetrics: RiskMetrics): {
    maxWeight: string;
    effectivePositions: string;
    concentrationRisk: string;
    avgDividendConsistency: string;
  } {
    return {
      maxWeight: `${(riskMetrics.max_weight * 100).toFixed(1)}%`,
      effectivePositions: riskMetrics.effective_positions.toFixed(1),
      concentrationRisk: riskMetrics.concentration_risk.toFixed(2),
      avgDividendConsistency: `${(riskMetrics.avg_dividend_consistency * 100).toFixed(1)}%`,
    };
  }
}

export const portfolioService = new PortfolioService();
export default portfolioService; 
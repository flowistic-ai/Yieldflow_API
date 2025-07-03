interface FinancialRatiosResponse {
  symbol: string;
  period: string;
  profitability_ratios: {
    gross_margin?: number;
    operating_margin?: number;
    net_margin?: number;
    return_on_assets?: number;
    return_on_equity?: number;
    return_on_invested_capital?: number;
    eps_growth?: number;
  };
  liquidity_ratios: {
    current_ratio?: number;
    quick_ratio?: number;
    cash_ratio?: number;
    working_capital?: number;
    operating_cash_flow_ratio?: number;
  };
  solvency_ratios: {
    debt_to_equity?: number;
    debt_to_assets?: number;
    equity_ratio?: number;
    debt_to_capital?: number;
    long_term_debt_to_equity?: number;
    interest_coverage?: number;
  };
  efficiency_ratios: {
    asset_turnover?: number;
    inventory_turnover?: number;
    receivables_turnover?: number;
    working_capital_turnover?: number;
  };
  cash_flow_ratios: {
    operating_cash_flow?: number;
    free_cash_flow?: number;
    fcf_margin?: number;
    cash_flow_score?: number;
  };
  ratio_scores?: {
    profitability?: number;
    liquidity?: number;
    solvency?: number;
    efficiency?: number;
    overall?: number;
  };
}

interface ComprehensiveFinancialResponse {
  ticker: string;
  period: string;
  income_analysis: any;
  liquidity_analysis: any;
  solvency_analysis: any;
  cash_flow_analysis: any;
  overall_score: number;
  insights: string[];
  risk_factors: string[];
  opportunities: string[];
}

interface SnowflakeData {
  profitability: {
    score: number;
    metrics: {
      gross_margin: number;
      operating_margin: number;
      net_margin: number;
      roe: number;
      roa: number;
    };
  };
  liquidity: {
    score: number;
    metrics: {
      current_ratio: number;
      quick_ratio: number;
      cash_ratio: number;
      working_capital: number;
    };
  };
  solvency: {
    score: number;
    metrics: {
      debt_to_equity: number;
      debt_to_assets: number;
      equity_ratio: number;
      interest_coverage: number;
    };
  };
  growth: {
    score: number;
    metrics: {
      revenue_growth: number;
      earnings_growth: number;
      eps_growth: number;
      sustainable_growth: number;
    };
  };
  efficiency: {
    score: number;
    metrics: {
      asset_turnover: number;
      inventory_turnover: number;
      receivables_turnover: number;
      working_capital_turnover: number;
    };
  };
}

export default class FinancialDataService {
  private baseUrl: string;
  private apiKey: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.apiKey = process.env.REACT_APP_API_KEY || 'yk_eXZGE3PhU1E39cg5lEdTRSFl6BRKBX3w6Gk8GK0fD_g'; // Default to basic test key
  }

  private async makeRequest(endpoint: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
        'x-api-key': this.apiKey,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async getFinancialRatios(symbol: string, period: string = 'annual'): Promise<FinancialRatiosResponse> {
    try {
      const data = await this.makeRequest(`/api/v1/ratios/calculate/${symbol}?period=${period}&limit=4`);
      return data;
    } catch (error) {
      console.error(`Error fetching financial ratios for ${symbol}:`, error);
      throw error;
    }
  }

  async getComprehensiveFinancials(symbol: string, period: string = 'annual'): Promise<ComprehensiveFinancialResponse> {
    try {
      const data = await this.makeRequest(`/api/v1/financials/comprehensive/${symbol}?period=${period}&limit=4`);
      return data;
    } catch (error) {
      console.error(`Error fetching comprehensive financials for ${symbol}:`, error);
      throw error;
    }
  }

  async getIncomeStatements(symbol: string, period: string = 'annual') {
    try {
      const data = await this.makeRequest(`/api/v1/financials/income-statements?ticker=${symbol}&period=${period}&limit=4`);
      return data;
    } catch (error) {
      console.error(`Error fetching income statements for ${symbol}:`, error);
      throw error;
    }
  }

  async getBalanceSheets(symbol: string, period: string = 'annual') {
    try {
      const data = await this.makeRequest(`/api/v1/financials/balance-sheets?ticker=${symbol}&period=${period}&limit=4`);
      return data;
    } catch (error) {
      console.error(`Error fetching balance sheets for ${symbol}:`, error);
      throw error;
    }
  }

  async getCashFlows(symbol: string, period: string = 'annual') {
    try {
      const data = await this.makeRequest(`/api/v1/financials/cash-flows?ticker=${symbol}&period=${period}&limit=4`);
      return data;
    } catch (error) {
      console.error(`Error fetching cash flows for ${symbol}:`, error);
      throw error;
    }
  }

  // Transform API data to snowflake format
  transformToSnowflakeData(ratiosData: FinancialRatiosResponse, comprehensiveData?: ComprehensiveFinancialResponse): SnowflakeData {
    // Calculate scores based on ratios (0-6 scale like SimplyWall.St)
    const calculateProfitabilityScore = (ratios: any): number => {
      let score = 0;
      let factors = 0;

      // Gross margin score (weight: 1)
      if (ratios.gross_margin !== null && ratios.gross_margin !== undefined) {
        if (ratios.gross_margin > 40) score += 1.2;
        else if (ratios.gross_margin > 25) score += 1.0;
        else if (ratios.gross_margin > 15) score += 0.7;
        else score += 0.3;
        factors += 1;
      }

      // Operating margin score (weight: 1.2)
      if (ratios.operating_margin !== null && ratios.operating_margin !== undefined) {
        if (ratios.operating_margin > 20) score += 1.4;
        else if (ratios.operating_margin > 10) score += 1.2;
        else if (ratios.operating_margin > 5) score += 0.8;
        else score += 0.3;
        factors += 1.2;
      }

      // Net margin score (weight: 1.2)
      if (ratios.net_margin !== null && ratios.net_margin !== undefined) {
        if (ratios.net_margin > 15) score += 1.4;
        else if (ratios.net_margin > 8) score += 1.2;
        else if (ratios.net_margin > 3) score += 0.8;
        else score += 0.3;
        factors += 1.2;
      }

      // ROE score (weight: 1.1)
      if (ratios.return_on_equity !== null && ratios.return_on_equity !== undefined) {
        if (ratios.return_on_equity > 20) score += 1.3;
        else if (ratios.return_on_equity > 15) score += 1.1;
        else if (ratios.return_on_equity > 10) score += 0.8;
        else score += 0.4;
        factors += 1.1;
      }

      // ROA score (weight: 1)
      if (ratios.return_on_assets !== null && ratios.return_on_assets !== undefined) {
        if (ratios.return_on_assets > 10) score += 1.2;
        else if (ratios.return_on_assets > 5) score += 1.0;
        else if (ratios.return_on_assets > 2) score += 0.7;
        else score += 0.3;
        factors += 1;
      }

      return factors > 0 ? Math.min(6, (score / factors) * 6) : 3;
    };

    const calculateLiquidityScore = (ratios: any): number => {
      let score = 0;
      let factors = 0;

      // Current ratio score
      if (ratios.current_ratio !== null && ratios.current_ratio !== undefined) {
        if (ratios.current_ratio > 2.5) score += 1.2;
        else if (ratios.current_ratio > 1.5) score += 1.0;
        else if (ratios.current_ratio > 1.0) score += 0.7;
        else score += 0.2;
        factors += 1;
      }

      // Quick ratio score
      if (ratios.quick_ratio !== null && ratios.quick_ratio !== undefined) {
        if (ratios.quick_ratio > 1.5) score += 1.2;
        else if (ratios.quick_ratio > 1.0) score += 1.0;
        else if (ratios.quick_ratio > 0.5) score += 0.6;
        else score += 0.2;
        factors += 1;
      }

      // Cash ratio score
      if (ratios.cash_ratio !== null && ratios.cash_ratio !== undefined) {
        if (ratios.cash_ratio > 0.5) score += 1.0;
        else if (ratios.cash_ratio > 0.2) score += 0.8;
        else if (ratios.cash_ratio > 0.1) score += 0.5;
        else score += 0.2;
        factors += 1;
      }

      return factors > 0 ? Math.min(6, (score / factors) * 6) : 3;
    };

    const calculateSolvencyScore = (ratios: any): number => {
      let score = 0;
      let factors = 0;

      // Debt to equity score (lower is better)
      if (ratios.debt_to_equity !== null && ratios.debt_to_equity !== undefined) {
        if (ratios.debt_to_equity < 0.3) score += 1.2;
        else if (ratios.debt_to_equity < 0.6) score += 1.0;
        else if (ratios.debt_to_equity < 1.0) score += 0.6;
        else score += 0.2;
        factors += 1;
      }

      // Debt to assets score (lower is better)
      if (ratios.debt_to_assets !== null && ratios.debt_to_assets !== undefined) {
        if (ratios.debt_to_assets < 0.3) score += 1.2;
        else if (ratios.debt_to_assets < 0.5) score += 1.0;
        else if (ratios.debt_to_assets < 0.7) score += 0.6;
        else score += 0.2;
        factors += 1;
      }

      // Interest coverage score
      if (ratios.interest_coverage !== null && ratios.interest_coverage !== undefined) {
        if (ratios.interest_coverage > 10) score += 1.2;
        else if (ratios.interest_coverage > 5) score += 1.0;
        else if (ratios.interest_coverage > 2) score += 0.6;
        else score += 0.2;
        factors += 1;
      }

      return factors > 0 ? Math.min(6, (score / factors) * 6) : 3;
    };

    const calculateEfficiencyScore = (ratios: any): number => {
      let score = 0;
      let factors = 0;

      // Asset turnover score
      if (ratios.asset_turnover !== null && ratios.asset_turnover !== undefined) {
        if (ratios.asset_turnover > 1.5) score += 1.2;
        else if (ratios.asset_turnover > 1.0) score += 1.0;
        else if (ratios.asset_turnover > 0.5) score += 0.6;
        else score += 0.2;
        factors += 1;
      }

      // Inventory turnover score
      if (ratios.inventory_turnover !== null && ratios.inventory_turnover !== undefined) {
        if (ratios.inventory_turnover > 8) score += 1.2;
        else if (ratios.inventory_turnover > 5) score += 1.0;
        else if (ratios.inventory_turnover > 3) score += 0.6;
        else score += 0.2;
        factors += 1;
      }

      return factors > 0 ? Math.min(6, (score / factors) * 6) : 3;
    };

    const calculateGrowthScore = (ratios: any, comprehensiveData?: any): number => {
      let score = 0;
      let factors = 0;

      // EPS growth score
      if (ratios.eps_growth !== null && ratios.eps_growth !== undefined) {
        if (ratios.eps_growth > 15) score += 1.2;
        else if (ratios.eps_growth > 5) score += 1.0;
        else if (ratios.eps_growth > 0) score += 0.6;
        else score += 0.2;
        factors += 1;
      }

      // Revenue growth (from comprehensive data if available)
      if (comprehensiveData?.income_analysis?.growth_rate_3y !== undefined) {
        const revenueGrowth = comprehensiveData.income_analysis.growth_rate_3y;
        if (revenueGrowth > 10) score += 1.2;
        else if (revenueGrowth > 5) score += 1.0;
        else if (revenueGrowth > 0) score += 0.6;
        else score += 0.2;
        factors += 1;
      }

      return factors > 0 ? Math.min(6, (score / factors) * 6) : 2; // Default to lower growth score
    };

    // Transform the data
    return {
      profitability: {
        score: calculateProfitabilityScore(ratiosData.profitability_ratios),
        metrics: {
          gross_margin: ratiosData.profitability_ratios.gross_margin || 0,
          operating_margin: ratiosData.profitability_ratios.operating_margin || 0,
          net_margin: ratiosData.profitability_ratios.net_margin || 0,
          roe: ratiosData.profitability_ratios.return_on_equity || 0,
          roa: ratiosData.profitability_ratios.return_on_assets || 0,
        },
      },
      liquidity: {
        score: calculateLiquidityScore(ratiosData.liquidity_ratios),
        metrics: {
          current_ratio: ratiosData.liquidity_ratios.current_ratio || 0,
          quick_ratio: ratiosData.liquidity_ratios.quick_ratio || 0,
          cash_ratio: ratiosData.liquidity_ratios.cash_ratio || 0,
          working_capital: ratiosData.liquidity_ratios.working_capital || 0,
        },
      },
      solvency: {
        score: calculateSolvencyScore(ratiosData.solvency_ratios),
        metrics: {
          debt_to_equity: ratiosData.solvency_ratios.debt_to_equity || 0,
          debt_to_assets: ratiosData.solvency_ratios.debt_to_assets || 0,
          equity_ratio: ratiosData.solvency_ratios.equity_ratio || 0,
          interest_coverage: ratiosData.solvency_ratios.interest_coverage || 0,
        },
      },
      growth: {
        score: calculateGrowthScore(ratiosData.profitability_ratios, comprehensiveData),
        metrics: {
          revenue_growth: comprehensiveData?.income_analysis?.growth_rate_3y || 0,
          earnings_growth: comprehensiveData?.income_analysis?.earnings_growth || 0,
          eps_growth: ratiosData.profitability_ratios.eps_growth || 0,
          sustainable_growth: 0, // Calculate if needed
        },
      },
      efficiency: {
        score: calculateEfficiencyScore(ratiosData.efficiency_ratios || {}),
        metrics: {
          asset_turnover: ratiosData.efficiency_ratios?.asset_turnover || 0,
          inventory_turnover: ratiosData.efficiency_ratios?.inventory_turnover || 0,
          receivables_turnover: ratiosData.efficiency_ratios?.receivables_turnover || 0,
          working_capital_turnover: ratiosData.efficiency_ratios?.working_capital_turnover || 0,
        },
      },
    };
  }

  async getSnowflakeData(symbol: string, period: string = 'annual'): Promise<SnowflakeData> {
    try {
      const [ratiosData, comprehensiveData] = await Promise.allSettled([
        this.getFinancialRatios(symbol, period),
        this.getComprehensiveFinancials(symbol, period).catch(() => undefined), // Optional
      ]);

      if (ratiosData.status === 'rejected') {
        throw new Error(`Failed to fetch financial ratios: ${ratiosData.reason}`);
      }

      const comprehensive = comprehensiveData.status === 'fulfilled' ? comprehensiveData.value : undefined;
      
      return this.transformToSnowflakeData(ratiosData.value, comprehensive);
    } catch (error) {
      console.error(`Error getting snowflake data for ${symbol}:`, error);
      throw error;
    }
  }
} 
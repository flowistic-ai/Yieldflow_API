import axios from 'axios';

const API_BASE_URL = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/v1`;

// API Key from environment variable
const API_KEY = process.env.REACT_APP_API_KEY || 'yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc';

// Configure axios defaults
axios.defaults.headers.common['X-API-KEY'] = API_KEY;
axios.defaults.headers.common['Content-Type'] = 'application/json';

export interface DividendAnalysis {
  ticker: string;
  current_dividend_info: {
    yield: number;
    payout_ratio: number;
    last_payment: {
      date: string;
      amount: number;
    };
    estimated_annual: number;
    payment_frequency: string;
  };
  historical_data: {
    years_of_increases: number;
    consecutive_payments: number;
    average_growth_rate: number;
  };
  sustainability_metrics: {
    coverage_ratio: number;
    risk_rating: string;
    sustainability_score: number;
  };
}

export interface DividendChart {
  ticker: string;
  chart_type: string;
  chart_data: any[];
  metadata?: any;
}

class DividendService {
  async getCurrentDividendInfo(ticker: string): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/current`, {
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    return response.data;
  }

  async getDividendAnalysis(ticker: string, includeForecast: boolean = false, includePeerComparison: boolean = false): Promise<DividendAnalysis> {
    const params = new URLSearchParams();
    if (includeForecast) {
      params.append('include_forecast', 'true');
    }
    if (includePeerComparison) {
      params.append('include_peer_comparison', 'true');
    }
    
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/analysis?${params.toString()}`, {
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    return response.data;
  }

  async getDividendHistory(ticker: string): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/history`, {
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    return response.data;
  }

  async getDividendForecast(ticker: string): Promise<any> {
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/forecast`, {
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    return response.data;
  }

  async getDividendGrowthChart(ticker: string, years?: number): Promise<DividendChart> {
    const params = new URLSearchParams();
    if (years && years > 0) {
      params.append('years', years.toString());
    }
    
    const url = `${API_BASE_URL}/dividends/${ticker}/charts/growth${params.toString() ? '?' + params.toString() : ''}`;
    const response = await axios.get(url, {
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    return response.data;
  }

  async getYieldVsPriceChart(ticker: string): Promise<DividendChart> {
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/charts/yield-vs-price`, {
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    return response.data;
  }

  async getPayoutRatioChart(ticker: string): Promise<DividendChart> {
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/charts/payout-ratio`, {
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    return response.data;
  }

  async getPeerComparisonChart(ticker: string): Promise<DividendChart> {
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/charts/peer-comparison`, {
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    return response.data;
  }

  async getNEPOAnalysis(ticker: string, investmentAmount: number = 100000): Promise<any> {
    const params = new URLSearchParams();
    params.append('investment_amount', investmentAmount.toString());
    params.append('time_horizon', 'medium');
    params.append('include_news_analysis', 'true');
    
    // For single-stock NEPO analysis, we'll create a mini-portfolio with the target stock + SPY as benchmark
    // This allows the optimization engine to work while focusing on the target stock
    const response = await axios.post(`${API_BASE_URL}/portfolio/optimize-news-enhanced?${params.toString()}`, {
      tickers: [ticker, 'SPY'], // Add SPY as a benchmark for portfolio optimization
      objective: 'sharpe_ratio',
      shrinkage_method: 'auto',
      max_weight: 0.5 // Maximum allowed weight per asset
    }, {
      headers: {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  }
}

export const dividendService = new DividendService();

export const getCompanyInfo = async (ticker: string): Promise<{
  ticker: string;
  name: string;
  logo_url: string;
  exchange: string;
  sector: string;
  industry: string;
  market_cap: number;
  description: string;
  website: string;
  last_updated: string;
}> => {
  const response = await fetch(`${API_BASE_URL}/dividends/${ticker}/company-info`, {
    headers: {
      'X-API-KEY': API_KEY,
    },
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch company info: ${response.statusText}`);
  }
  
  return response.json();
};
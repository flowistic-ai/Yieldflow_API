import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// API Key from the backend - using the basic plan key
const API_KEY = 'yk_eXZGE3PhU1E39cg5lEdTRSFl6BRKBX3w6Gk8GK0fD_g';

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

  async getDividendAnalysis(ticker: string): Promise<DividendAnalysis> {
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/analysis`, {
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

  async getDividendGrowthChart(ticker: string): Promise<DividendChart> {
    const response = await axios.get(`${API_BASE_URL}/dividends/${ticker}/charts/growth`, {
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
}

export const dividendService = new DividendService(); 
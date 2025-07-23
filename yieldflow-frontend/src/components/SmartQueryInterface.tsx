import React, { useState, useRef, useEffect, useCallback } from 'react';
import './SmartQueryInterface.css';

// TypeScript interfaces
interface QueryResponse {
  success: boolean;
  data?: any;
  explanation: string;
  suggestions: string[];
  visualization_config?: any;
  quality_score: number;
  processing_time?: number;
  timestamp: string;
}

interface QueryRequest {
  query: string;
  user_context?: Record<string, any>;
}

interface QuestionTemplate {
  id: string;
  category: string;
  title: string;
  description: string;
  template: string;
  parameters: TemplateParameter[];
  examples: string[];
}

interface TemplateParameter {
  name: string;
  type: 'number' | 'text' | 'select' | 'multiselect';
  label: string;
  placeholder?: string;
  options?: string[];
  min?: number;
  max?: number;
  required: boolean;
}

const SmartQueryInterface: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<QuestionTemplate | null>(null);
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);
  const [showTemplateSelector, setShowTemplateSelector] = useState(true);
  const [selectedRiskLevel, setSelectedRiskLevel] = useState<string>('conservative');

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const API_KEY = process.env.REACT_APP_API_KEY || 'yk_wMUsnDqpdIjHFj2lFB-CxjHdKQte4BkpJBY1rNFA3bw';

  // Pre-tested, guaranteed-to-work question templates
  const questionTemplates: QuestionTemplate[] = [
    // Stock Screening Templates
    {
      id: 'dividend_screening',
      category: 'Stock Screening',
      title: 'Find Dividend Stocks by Yield',
      description: 'Screen stocks based on dividend yield criteria',
      template: 'Find dividend stocks with yield above {min_yield}%',
      parameters: [
        {
          name: 'min_yield',
          type: 'number',
          label: 'Minimum Dividend Yield (%)',
          placeholder: '4.0',
          min: 0.5,
          max: 15,
          required: true
        }
      ],
      examples: ['4.0', '3.5', '5.0', '6.0']
    },
    {
      id: 'sector_pe_screening',
      category: 'Stock Screening',
      title: 'Find Stocks by Sector and P/E Ratio',
      description: 'Screen stocks in specific sectors with P/E criteria',
      template: 'Show {sector} stocks with P/E below {max_pe}',
      parameters: [
        {
          name: 'sector',
          type: 'select',
          label: 'Sector',
          options: ['Technology', 'Healthcare', 'Utilities', 'Financial Services', 'Energy', 'Consumer Defensive', 'Real Estate'],
          required: true
        },
        {
          name: 'max_pe',
          type: 'number',
          label: 'Maximum P/E Ratio',
          placeholder: '20',
          min: 5,
          max: 50,
          required: true
        }
      ],
      examples: ['Tech + 20', 'Healthcare + 15', 'Utilities + 25']
    },
    {
      id: 'price_yield_screening',
      category: 'Stock Screening',
      title: 'Find Stocks by Price and Yield',
      description: 'Screen stocks under specific price with dividend yield',
      template: 'Find stocks under ${max_price} with yield above {min_yield}%',
      parameters: [
        {
          name: 'max_price',
          type: 'number',
          label: 'Maximum Stock Price ($)',
          placeholder: '100',
          min: 10,
          max: 500,
          required: true
        },
        {
          name: 'min_yield',
          type: 'number',
          label: 'Minimum Dividend Yield (%)',
          placeholder: '3.0',
          min: 0.5,
          max: 15,
          required: true
        }
      ],
      examples: ['$100 + 3%', '$50 + 4%', '$200 + 2.5%']
    },

    // Stock Analysis Templates
    {
      id: 'multi_stock_analysis',
      category: 'Stock Analysis',
      title: 'Analyze Multiple Stocks',
      description: 'Evaluate dividend quality of specific stocks',
      template: 'Analyze {tickers} dividend quality',
      parameters: [
        {
          name: 'tickers',
          type: 'text',
          label: 'Stock Tickers (comma-separated)',
          placeholder: 'AAPL, MSFT, JNJ',
          required: true
        }
      ],
      examples: ['KO, PEP', 'JNJ, PFE, MRK', 'VZ, T', 'O, MAIN, STAG']
    },
    {
      id: 'single_stock_analysis',
      category: 'Stock Analysis',
      title: 'Evaluate Single Stock',
      description: 'Deep analysis of individual stock dividend sustainability',
      template: 'Evaluate {ticker} dividend sustainability',
      parameters: [
        {
          name: 'ticker',
          type: 'text',
          label: 'Stock Ticker',
          placeholder: 'AAPL',
          required: true
        }
      ],
      examples: ['PG', 'JNJ', 'KO', 'MSFT', 'VZ']
    },
    {
      id: 'stock_comparison',
      category: 'Stock Analysis',
      title: 'Compare Two Stocks',
      description: 'Side-by-side dividend metrics comparison',
      template: 'Compare {ticker1} vs {ticker2} dividend metrics',
      parameters: [
        {
          name: 'ticker1',
          type: 'text',
          label: 'First Stock Ticker',
          placeholder: 'KO',
          required: true
        },
        {
          name: 'ticker2',
          type: 'text',
          label: 'Second Stock Ticker',
          placeholder: 'PEP',
          required: true
        }
      ],
      examples: ['KO vs PEP', 'VZ vs T', 'JNJ vs PFE']
    },

    // Investment Guidance Templates
    {
      id: 'income_target',
      category: 'Investment Guidance',
      title: 'Income Target Planning',
      description: 'Plan investment for specific monthly income goal',
      template: 'I have ${initial_investment} and want to earn ${monthly_target} monthly',
      parameters: [
        {
          name: 'initial_investment',
          type: 'number',
          label: 'Investment Amount ($)',
          placeholder: '10000',
          min: 100,
          max: 1000000,
          required: true
        },
        {
          name: 'monthly_target',
          type: 'number',
          label: 'Monthly Income Target ($)',
          placeholder: '400',
          min: 10,
          max: 10000,
          required: true
        }
      ],
      examples: ['$10,000 → $400/month', '$5,000 → $200/month', '$25,000 → $1,000/month']
    },
    {
      id: 'return_expectation',
      category: 'Investment Guidance',
      title: 'Return Expectation Check',
      description: 'Check if your return expectations are realistic',
      template: 'I have ${investment_amount} and want {annual_return}% annual return',
      parameters: [
        {
          name: 'investment_amount',
          type: 'number',
          label: 'Investment Amount ($)',
          placeholder: '10000',
          min: 1000,
          max: 1000000,
          required: true
        },
        {
          name: 'annual_return',
          type: 'number',
          label: 'Target Annual Return (%)',
          placeholder: '8',
          min: 1,
          max: 30,
          required: true
        }
      ],
      examples: ['$10,000 → 8%', '$50,000 → 5%', '$5,000 → 12%']
    },
    {
      id: 'realistic_income',
      category: 'Investment Guidance',
      title: 'Realistic Income Estimate',
      description: 'Get realistic income expectations from your investment',
      template: 'What\'s realistic income from ${investment_amount} investment?',
      parameters: [
        {
          name: 'investment_amount',
          type: 'number',
          label: 'Investment Amount ($)',
          placeholder: '15000',
          min: 1000,
          max: 1000000,
          required: true
        }
      ],
      examples: ['$15,000', '$25,000', '$50,000', '$100,000']
    }
  ];

  // Reset selected risk level when response changes
  useEffect(() => {
    if (response?.data?.exploratory_guidance) {
      setSelectedRiskLevel('conservative');
    }
  }, [response]);

  const handleTemplateSelect = (template: QuestionTemplate) => {
    setSelectedTemplate(template);
    setParameters({});
    setShowTemplateSelector(false);
    setResponse(null);
  };

  const handleParameterChange = (paramName: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const buildQueryFromTemplate = (): string => {
    if (!selectedTemplate) return '';
    
    let query = selectedTemplate.template;
    
    // Replace template variables with actual values
    selectedTemplate.parameters.forEach(param => {
      const value = parameters[param.name];
      if (value !== undefined && value !== '') {
        const placeholder = `{${param.name}}`;
        query = query.replace(placeholder, value);
      }
    });
    
    return query;
  };

  const isFormValid = (): boolean => {
    if (!selectedTemplate) return false;
    
    return selectedTemplate.parameters.every(param => {
      if (!param.required) return true;
      const value = parameters[param.name];
      return value !== undefined && value !== '' && value !== null;
    });
  };

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isFormValid() || isLoading) return;

    setIsLoading(true);
    setResponse(null);

    const query = buildQueryFromTemplate();
    
    // Add to history
    setQueryHistory(prev => [query, ...prev.slice(0, 4)]);

    try {
      const requestBody: QueryRequest = {
        query: query.trim(),
        user_context: {
          timestamp: new Date().toISOString(),
          template_id: selectedTemplate?.id,
          session_id: 'guided_session'
        }
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/query/ask`, {
        method: 'POST',
        headers: {
          'X-API-KEY': API_KEY,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const result: QueryResponse = await response.json();
      setResponse(result);

    } catch (error) {
      console.error('Query processing failed:', error);
      setResponse({
        success: false,
        explanation: `Sorry, I encountered an error processing your query: ${error instanceof Error ? error.message : 'Unknown error'}`,
        suggestions: [
          'Try adjusting your parameters',
          'Check your internet connection',
          'Select a different question template'
        ],
        quality_score: 0,
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackToTemplates = () => {
    setSelectedTemplate(null);
    setParameters({});
    setShowTemplateSelector(true);
    setResponse(null);
  };

  const handleHistoryClick = (historyQuery: string) => {
    // Try to match history query to a template and populate parameters
    // For now, just show the query - could enhance later
    alert(`Previous query: ${historyQuery}`);
  };

  const renderScreeningResults = (data: any) => {
    if (!data?.screening_results) return null;

    return (
      <div className="results-table">
        <h4>Screening Results ({data.total_found} stocks found)</h4>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Company</th>
                <th>Price</th>
                <th>Dividend Yield</th>
                <th>Sector</th>
              </tr>
            </thead>
            <tbody>
              {(data.screening_results || []).map((stock: any, index: number) => (
                <tr key={index}>
                  <td className="ticker">{stock.ticker}</td>
                  <td>{stock.company_name}</td>
                  <td>${stock.current_price?.toFixed(2) || 'N/A'}</td>
                  <td className="yield">{stock.dividend_yield?.toFixed(2) || '0.00'}%</td>
                  <td>{stock.sector}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderOptimizationResults = (data: any) => {
    if (!data?.weights) return null;

    const weights = Object.entries(data.weights) as [string, number][];
    
    return (
      <div className="optimization-results">
        <h4>Portfolio Optimization Results</h4>
        <div className="metrics-grid">
          <div className="metric">
            <span className="label">Expected Return</span>
            <span className="value">{(data.expected_return * 100).toFixed(1)}%</span>
          </div>
          <div className="metric">
            <span className="label">Volatility</span>
            <span className="value">{(data.volatility * 100).toFixed(1)}%</span>
          </div>
          <div className="metric">
            <span className="label">Sharpe Ratio</span>
            <span className="value">{data.sharpe_ratio?.toFixed(2) || 'N/A'}</span>
          </div>
          <div className="metric">
            <span className="label">Dividend Yield</span>
            <span className="value">{(data.expected_dividend_yield * 100).toFixed(1)}%</span>
          </div>
        </div>
        
        <div className="allocation-chart">
          <h5>Allocation Weights</h5>
          <div className="weight-bars">
            {(weights || []).map(([ticker, weight]) => (
              <div key={ticker} className="weight-bar">
                <div className="weight-info">
                  <span className="ticker">{ticker}</span>
                  <span className="percentage">{(weight * 100).toFixed(1)}%</span>
                </div>
                <div className="bar-container">
                  <div 
                    className="bar" 
                    style={{ width: `${weight * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderAnalysisResults = (data: any) => {
    if (!data?.analysis_results) return null;

    return (
      <div className="analysis-results">
        <h4>Stock Analysis Results</h4>
        {Object.entries(data.analysis_results).map(([ticker, analysis]: [string, any]) => (
          <div key={ticker} className="stock-analysis">
            <h5>{ticker}</h5>
            <div className="analysis-content">
              <div className="quality-score">
                <span className="label">Quality Score</span>
                <span className={`score score-${analysis.quality_score >= 7 ? 'high' : analysis.quality_score >= 5 ? 'medium' : 'low'}`}>
                  {analysis.quality_score?.toFixed(1) || 'N/A'}/10
                </span>
              </div>
              
              {analysis.strengths?.length > 0 && (
                <div className="strengths">
                  <h6>Strengths</h6>
                  <ul>
                    {(analysis.strengths || []).map((strength: string, index: number) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {analysis.risks?.length > 0 && (
                <div className="risks">
                  <h6>Risks</h6>
                  <ul>
                    {(analysis.risks || []).map((risk: string, index: number) => (
                      <li key={index}>{risk}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderETFRecommendations = (data: any) => {
    if (!data?.etf_recommendations) return null;

    const { etf_recommendations } = data;
    const primaryRecommendations = etf_recommendations.primary_recommendations || [];
    const allCategories = etf_recommendations.all_categories || {};

    return (
      <div className="etf-recommendations">
        <h4>📊 Recommended Dividend ETFs</h4>
        
        {/* Primary Recommendations */}
        <div className="primary-etfs">
          <h5>Top Recommendations</h5>
          <div className="etf-grid">
            {(primaryRecommendations || []).map((etf: any, index: number) => (
              <div key={etf.ticker} className="etf-card">
                <div className="etf-header">
                  <span className="etf-ticker">{etf.ticker}</span>
                  <span className="etf-yield">{etf.yield}%</span>
                </div>
                <h6 className="etf-name">{etf.name}</h6>
                <div className="etf-metrics">
                  <div className="metric">
                    <span className="label">Expense Ratio</span>
                    <span className="value">{etf.expense_ratio}%</span>
                  </div>
                  <div className="metric">
                    <span className="label">AUM</span>
                    <span className="value">${etf.aum}</span>
                  </div>
                  <div className="metric">
                    <span className="label">Focus</span>
                    <span className="value">{etf.focus}</span>
                  </div>
                </div>
                <p className="etf-rationale">{etf.rationale}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Additional Categories */}
        {Object.entries(allCategories).length > 1 && (
          <div className="additional-categories">
            <h5>Alternative Categories</h5>
            {Object.entries(allCategories).map(([category, etfs]: [string, any]) => {
              if (category === 'dividend_etfs') return null; // Skip main category
              
              const categoryName = category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
              
              return (
                <div key={category} className="etf-category">
                  <h6>{categoryName}</h6>
                  <div className="etf-list">
                    {(etfs || []).map((etf: any) => (
                      <div key={etf.ticker} className="etf-item">
                        <div className="etf-summary">
                          <span className="ticker">{etf.ticker}</span>
                          <span className="name">{etf.name}</span>
                          <span className="yield">{etf.yield}% yield</span>
                        </div>
                        <p className="rationale">{etf.rationale}</p>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Comparison Factors */}
        {data.comparison_factors && (
          <div className="comparison-factors">
            <h5>Key Comparison Factors</h5>
            <div className="factors-grid">
              {Object.entries(data.comparison_factors).map(([factor, description]: [string, any]) => (
                <div key={factor} className="factor">
                  <strong>{factor.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                  <span>{description}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderInvestmentGuidance = (data: any): React.ReactElement | null => {
    if (data?.investment_reality_check) {
      // Legacy format - redirect to new format
      return renderInvestmentGuidance({ concise_guidance: data.investment_reality_check });
    }
    
    // Handle exploratory guidance (realistic income ranges)
    if (data?.exploratory_guidance) {
      return renderExploratoryGuidance(data.exploratory_guidance);
    }
    
    if (!data?.concise_guidance) return null;

    const guidance = data.concise_guidance;
    
    return (
      <div className="investment-guidance">
        <div className="concise-summary">
          <h4>💰 Investment Analysis</h4>
          <div className="key-metrics">
            <div className="metric-row">
              <span className="label">Investment:</span>
              <span className="value">${guidance.investment_amount?.toLocaleString()}</span>
            </div>
            <div className="metric-row">
              <span className="label">Target:</span>
              <span className="value">${guidance.target_monthly}/month</span>
            </div>
            <div className="metric-row">
              <span className="label">Required Yield:</span>
              <span className="value">{guidance.required_yield}% annually</span>
            </div>
            <div className="metric-row risk-level" data-risk={
              guidance.risk_assessment?.toLowerCase().includes('low') ? 'low' :
              guidance.risk_assessment?.toLowerCase().includes('moderate') ? 'moderate' :
              guidance.risk_assessment?.toLowerCase().includes('high') && !guidance.risk_assessment?.toLowerCase().includes('very') ? 'high' :
              'very-high'
            }>
              <span className="label">Risk Assessment:</span>
              <span className="value">{guidance.risk_assessment}</span>
            </div>
          </div>
          
          <div className="potential-earnings">
            <h5>🎯 Earnings Potential</h5>
            <div className="earnings-grid">
              <div className="earnings-box max-potential">
                <span className="amount">${guidance.max_potential_monthly}/month</span>
                <span className="label">Maximum Potential</span>
                <span className="risk">({guidance.risk_assessment})</span>
              </div>
              <div className="earnings-box realistic">
                <span className="amount">${guidance.realistic_monthly}/month</span>
                <span className="label">Realistic Target</span>
                <span className="strategy">({guidance.strategy})</span>
              </div>
            </div>
          </div>
        </div>

        {guidance.dividend_picks && guidance.dividend_picks.length > 0 && (
          <div className="dividend-picks">
            <h5>📈 Recommended Dividend Stocks</h5>
            <div className="picks-grid">
              {guidance.dividend_picks.map((stock: any, index: number) => (
                <div key={index} className="dividend-pick">
                  <div className="stock-info">
                    <span className="ticker">{stock.ticker}</span>
                    <span className="yield">{stock.yield}%</span>
                  </div>
                  <div className="income-projection">
                    <span className="monthly">${stock.monthly_income}/mo</span>
                    <span className="annual">${stock.annual_income}/yr</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderExploratoryGuidance = (guidance: any): React.ReactElement => {
    const { investment_amount, income_scenarios, realistic_monthly_estimate, portfolio_examples } = guidance;
    
    const selectedPortfolio = portfolio_examples?.[selectedRiskLevel];
    
    return (
      <div className="exploratory-guidance">
        <div className="exploration-summary">
          <h4>💰 Realistic Income Analysis</h4>
          <div className="key-metrics">
            <div className="metric-row">
              <span className="label">Investment Amount:</span>
              <span className="value">${investment_amount?.toLocaleString()}</span>
            </div>
            <div className="metric-row">
              <span className="label">Realistic Estimate:</span>
              <span className="value">${realistic_monthly_estimate}/month</span>
            </div>
          </div>
          
          <div className="income-scenarios">
            <h5>📊 Income Ranges by Risk Level</h5>
            <p className="scenario-instruction">Click on a risk level to see example portfolio</p>
            <div className="scenarios-grid">
              {Object.entries(income_scenarios).map(([level, scenario]: [string, any]) => (
                <div 
                  key={level} 
                  className={`scenario-box ${level} ${selectedRiskLevel === level ? 'selected' : ''}`}
                  onClick={() => setSelectedRiskLevel(level)}
                >
                  <div className="scenario-header">
                    <span className="level-name">{level.charAt(0).toUpperCase() + level.slice(1)}</span>
                    <span className="risk-label">({scenario.risk_label})</span>
                  </div>
                  <div className="income-range">
                    <span className="range">${scenario.min_monthly} - ${scenario.max_monthly}</span>
                    <span className="period">/month</span>
                  </div>
                  <div className="typical-income">
                    <span className="typical-label">Typical:</span>
                    <span className="typical-value">${scenario.typical_monthly}/month</span>
                  </div>
                  {selectedRiskLevel === level && (
                    <div className="selected-indicator">
                      <span>👆 Selected</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {selectedPortfolio && selectedPortfolio.stocks && selectedPortfolio.stocks.length > 0 && (
          <div className="portfolio-showcase">
            <div className="portfolio-header">
              <h5>📈 {selectedRiskLevel.charAt(0).toUpperCase() + selectedRiskLevel.slice(1)} Portfolio Example</h5>
              <div className="portfolio-stats">
                <span className="avg-yield">Avg Yield: {selectedPortfolio.avg_yield}%</span>
                <span className="total-income">Total Income: ${selectedPortfolio.total_monthly}/month</span>
              </div>
            </div>
            <p className="portfolio-description">{selectedPortfolio.description}</p>
            <div className="picks-grid">
              {selectedPortfolio.stocks.map((stock: any, index: number) => (
                <div key={index} className="dividend-pick enhanced">
                  <div className="stock-info">
                    <span className="ticker">{stock.ticker}</span>
                    <span className="yield">{stock.yield}%</span>
                  </div>
                  <div className="stock-details">
                    <span className="company-name">{stock.name}</span>
                    <span className="stock-price">${stock.price}</span>
                  </div>
                  <div className="income-projection">
                    <span className="monthly">${stock.monthly_income}/mo</span>
                    <span className="annual">${stock.annual_income}/yr</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderResults = () => {
    if (!response?.data) return null;

    const { data } = response;

    // Handle investment guidance (both new and legacy formats)
    if (data.concise_guidance || data.exploratory_guidance || data.investment_reality_check) {
      return renderInvestmentGuidance(data);
    }
    
    // Handle screening with enhanced analysis
    if (data.screening_results) {
      return (
        <div className="combined-results">
          {renderScreeningResults(data)}
          {data.analysis_results && (
            <div className="enhanced-analysis-section">
              <h4>🔬 Detailed Stock Analysis</h4>
              {renderAnalysisResults(data)}
            </div>
          )}
        </div>
      );
    }
    
    // Handle pure analysis
    if (data.analysis_results) {
      return renderAnalysisResults(data);
    }
    
    // Handle other result types
    if (data.weights) {
      return renderOptimizationResults(data);
    }
    
    if (data.etf_recommendations) {
      return renderETFRecommendations(data);
    }

    return (
      <div className="generic-results">
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  };

  const renderTemplateSelector = () => {
    const categories = Array.from(new Set(questionTemplates.map(t => t.category)));
    
    return (
      <div className="template-selector">
        <h3>Choose Your Investment Question</h3>
        <p>Select a pre-tested question template and customize the parameters for guaranteed accurate results.</p>
        
        {categories.map(category => (
          <div key={category} className="template-category">
            <h4>{category}</h4>
            <div className="template-grid">
              {questionTemplates
                .filter(template => template.category === category)
                .map(template => (
                  <div
                    key={template.id}
                    className="template-card"
                    onClick={() => handleTemplateSelect(template)}
                  >
                    <h5>{template.title}</h5>
                    <p>{template.description}</p>
                    <div className="template-examples">
                      <strong>Examples:</strong> {template.examples.join(', ')}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderParameterForm = () => {
    if (!selectedTemplate) return null;

    const queryPreview = buildQueryFromTemplate();

    return (
      <div className="parameter-form">
        <div className="form-header">
          <button 
            onClick={handleBackToTemplates}
            className="back-button"
          >
            ← Back to Templates
          </button>
          <h3>{selectedTemplate.title}</h3>
          <p>{selectedTemplate.description}</p>
        </div>

        <form onSubmit={handleQuerySubmit} className="parameter-inputs">
          {selectedTemplate.parameters.map(param => (
            <div key={param.name} className="parameter-input">
              <label htmlFor={param.name}>{param.label}</label>
              
              {param.type === 'number' && (
                <input
                  id={param.name}
                  type="number"
                  placeholder={param.placeholder}
                  min={param.min}
                  max={param.max}
                  value={parameters[param.name] || ''}
                  onChange={(e) => handleParameterChange(param.name, parseFloat(e.target.value) || '')}
                  required={param.required}
                />
              )}
              
              {param.type === 'text' && (
                <input
                  id={param.name}
                  type="text"
                  placeholder={param.placeholder}
                  value={parameters[param.name] || ''}
                  onChange={(e) => handleParameterChange(param.name, e.target.value)}
                  required={param.required}
                />
              )}
              
              {param.type === 'select' && (
                <select
                  id={param.name}
                  value={parameters[param.name] || ''}
                  onChange={(e) => handleParameterChange(param.name, e.target.value)}
                  required={param.required}
                >
                  <option value="">Select {param.label}</option>
                  {param.options?.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              )}
            </div>
          ))}

          <div className="query-preview">
            <h4>Your Question:</h4>
            <div className="preview-text">{queryPreview || 'Fill in the parameters above...'}</div>
          </div>

          <button 
            type="submit" 
            disabled={!isFormValid() || isLoading}
            className="submit-button"
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              <>
                <span>🚀</span>
                Get Analysis
              </>
            )}
          </button>
        </form>
      </div>
    );
  };

  return (
    <div className="smart-query-interface">
      <div className="query-header">
        <div className="header-top">
          <h2>🤖 AI Investment Assistant</h2>
          <button 
            className="home-button"
            onClick={() => window.location.reload()}
            title="Return to main dashboard"
          >
            🏠 Home
          </button>
        </div>
        <p>Get guaranteed accurate investment insights with our guided question templates</p>
      </div>

      {/* Template Selection or Parameter Form */}
      {showTemplateSelector ? renderTemplateSelector() : renderParameterForm()}

      {/* Query History */}
      {queryHistory.length > 0 && (
        <div className="query-history">
          <h4>Recent Queries</h4>
          <div className="history-items">
            {queryHistory.map((historyQuery, index) => (
              <button
                key={index}
                onClick={() => handleHistoryClick(historyQuery)}
                className="history-item"
              >
                {historyQuery}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Response Section */}
      {response && (
        <div className={`response-section ${response.success ? 'success' : 'error'}`}>
          <div className="response-header">
            <div className="quality-indicator">
              <span className="quality-label">Analysis Quality:</span>
              <div className="quality-bar">
                <div 
                  className="quality-fill" 
                  style={{ width: `${response.quality_score * 100}%` }}
                ></div>
              </div>
              <span className="quality-value">{(response.quality_score * 100).toFixed(0)}%</span>
              {response.processing_time && (
                <span className="processing-time">({response.processing_time.toFixed(2)}s)</span>
              )}
            </div>
          </div>

          <div className="explanation">
            <p>{response.explanation}</p>
          </div>

          {renderResults()}

          {(response.suggestions || []).length > 0 && (
            <div className="suggestions">
              <h4>💡 Suggestions</h4>
              <ul>
                {(response.suggestions || []).map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SmartQueryInterface; 
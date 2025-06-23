import React, { useState, useRef, useEffect, useCallback } from 'react';
import './SmartQueryInterface.css';

// TypeScript interfaces
interface QueryResponse {
  success: boolean;
  data?: any;
  explanation: string;
  suggestions: string[];
  visualization_config?: any;
  confidence: number;
  timestamp: string;
}

interface QueryRequest {
  query: string;
  user_context?: Record<string, any>;
}

interface QueryExamples {
  screening: string[];
  optimization: string[];
  analysis: string[];
  advanced: string[];
}

const SmartQueryInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [examples, setExamples] = useState<QueryExamples | null>(null);
  const [showExamples, setShowExamples] = useState(true);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const API_KEY = process.env.REACT_APP_API_KEY || 'yk_DqSugEeLU7cYgCVWqHQ3Nz6Nju0Gq3Iz20OK97BeHDc';

  const loadExamples = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/query/examples`, {
        headers: {
          'X-API-KEY': API_KEY,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setExamples(data.examples);
      }
    } catch (error) {
      console.error('Failed to load examples:', error);
    }
  }, [API_BASE_URL, API_KEY]);

  // Load examples on component mount
  useEffect(() => {
    loadExamples();
  }, [loadExamples]);

  // Auto-focus input
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    setShowExamples(false);
    setResponse(null);

    // Add to history
    setQueryHistory(prev => [query, ...prev.slice(0, 4)]);

    try {
      const requestBody: QueryRequest = {
        query: query.trim(),
        user_context: {
          timestamp: new Date().toISOString(),
          session_id: 'demo_session'
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
          'Try rephrasing your question',
          'Check your internet connection',
          'Use one of the example queries below'
        ],
        confidence: 0,
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
    setShowExamples(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleHistoryClick = (historyQuery: string) => {
    setQuery(historyQuery);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleQuerySubmit(e);
    }
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
              {data.screening_results.map((stock: any, index: number) => (
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
            {weights.map(([ticker, weight]) => (
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
                    {analysis.strengths.map((strength: string, index: number) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {analysis.risks?.length > 0 && (
                <div className="risks">
                  <h6>Risks</h6>
                  <ul>
                    {analysis.risks.map((risk: string, index: number) => (
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
            {primaryRecommendations.map((etf: any, index: number) => (
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
                    {etfs.map((etf: any) => (
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

  const renderResults = () => {
    if (!response?.data) return null;

    const { data } = response;

    if (data.screening_results) {
      return renderScreeningResults(data);
    } else if (data.weights) {
      return renderOptimizationResults(data);
    } else if (data.analysis_results) {
      return renderAnalysisResults(data);
    } else if (data.etf_recommendations) {
      return renderETFRecommendations(data);
    }

    return (
      <div className="generic-results">
        <pre>{JSON.stringify(data, null, 2)}</pre>
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
        <p>Ask me anything about stocks, portfolios, or dividend investing in natural language</p>
      </div>

      <form onSubmit={handleQuerySubmit} className="query-form">
        <div className="input-container">
          <textarea
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything... e.g., 'Find dividend stocks with yield above 4%' or 'Optimize a portfolio with AAPL, MSFT, JNJ'"
            rows={3}
            disabled={isLoading}
            className="query-input"
          />
          <button 
            type="submit" 
            disabled={!query.trim() || isLoading}
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
                Ask AI
              </>
            )}
          </button>
        </div>
        <div className="input-help">
          <span>Press Cmd/Ctrl + Enter to submit</span>
        </div>
      </form>

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
            <div className="confidence-indicator">
              <span className="confidence-label">Confidence:</span>
              <div className="confidence-bar">
                <div 
                  className="confidence-fill" 
                  style={{ width: `${response.confidence * 100}%` }}
                ></div>
              </div>
              <span className="confidence-value">{(response.confidence * 100).toFixed(0)}%</span>
            </div>
          </div>

          <div className="explanation">
            <p>{response.explanation}</p>
          </div>

          {renderResults()}

          {response.suggestions.length > 0 && (
            <div className="suggestions">
              <h4>💡 Suggestions</h4>
              <ul>
                {response.suggestions.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Examples Section */}
      {showExamples && examples && (
        <div className="examples-section">
          <h3>Example Queries</h3>
          
          <div className="examples-grid">
            <div className="example-category">
              <h4>📊 Stock Screening</h4>
              {examples.screening.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  className="example-item"
                >
                  {example}
                </button>
              ))}
            </div>

            <div className="example-category">
              <h4>⚖️ Portfolio Optimization</h4>
              {examples.optimization.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  className="example-item"
                >
                  {example}
                </button>
              ))}
            </div>

            <div className="example-category">
              <h4>🔍 Stock Analysis</h4>
              {examples.analysis.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  className="example-item"
                >
                  {example}
                </button>
              ))}
            </div>

            <div className="example-category">
              <h4>🎯 Advanced Queries</h4>
              {examples.advanced.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  className="example-item"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartQueryInterface; 
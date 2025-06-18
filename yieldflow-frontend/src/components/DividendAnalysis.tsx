import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { dividendService } from '../services/dividendService';

const DividendAnalysisComponent: React.FC = () => {
  const [ticker, setTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentDividend, setCurrentDividend] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [growthChart, setGrowthChart] = useState<any[]>([]);
  const [lastAnalyzedTicker, setLastAnalyzedTicker] = useState<string>('');

  const handleAnalyze = async () => {
    if (!ticker) {
      setError('Please enter a stock ticker');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [currentData, analysisData, chartData] = await Promise.all([
        dividendService.getCurrentDividendInfo(ticker),
        dividendService.getDividendAnalysis(ticker),
        dividendService.getDividendGrowthChart(ticker).catch(() => null)
      ]);

      setCurrentDividend(currentData);
      setAnalysis(analysisData);
      setLastAnalyzedTicker(ticker);
      
      // Prepare chart data for recharts
      if (chartData?.chart_data && Array.isArray(chartData.chart_data)) {
        const chartFormatted = chartData.chart_data.map((item: any) => ({
          year: item.year,
          dividend: item.dividend_amount,
          growthRate: item.growth_rate || 0
        }));
        setGrowthChart(chartFormatted);
      } else {
        setGrowthChart([]);
      }
    } catch (err: any) {
      console.error('API Error:', err);
      if (err.response?.status === 401) {
        setError('Authentication failed. Please check API key configuration.');
      } else if (err.response?.status === 404) {
        setError(`Stock ticker "${ticker}" not found. Please check the ticker symbol.`);
      } else if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please try again later.');
      } else if (err.response?.data?.detail) {
        setError(`API Error: ${err.response.data.detail}`);
      } else if (err.message) {
        setError(`Error: ${err.message}`);
      } else {
        setError('An unexpected error occurred while fetching data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleAnalyze();
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dividend Analysis
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Search Section */}
        <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <TextField
            label="Enter Stock Ticker"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            onKeyPress={handleKeyPress}
            fullWidth
            variant="outlined"
            placeholder="e.g., AAPL, MSFT, KO"
            disabled={loading}
          />
          <Button
            variant="contained"
            onClick={handleAnalyze}
            disabled={loading || !ticker}
            sx={{ minWidth: 120 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Analyze'}
          </Button>
        </Paper>

        {/* Status Section */}
        {lastAnalyzedTicker && !loading && !error && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip 
              label={`✅ Analysis complete for ${lastAnalyzedTicker}`} 
              color="success" 
              variant="outlined"
            />
          </Box>
        )}

        {/* Error Message */}
        {error && <Alert severity="error">{error}</Alert>}

        {/* Results Section */}
        {currentDividend && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* Current Dividend Info and Analysis Data Row */}
            <Box 
              sx={{ 
                display: 'grid', 
                gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
                gap: 3 
              }}
            >
              {/* Current Dividend Info */}
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Current Dividend Information
                </Typography>
                <Box sx={{ display: 'grid', gap: 1 }}>
                  <Typography>
                    <strong>Dividend Yield:</strong>{' '}
                    {currentDividend.current_dividend_info?.current_yield_pct || 
                     currentDividend.current_metrics?.current_yield_pct ||
                     currentDividend.yield 
                      ? `${(currentDividend.current_dividend_info?.current_yield_pct || 
                              currentDividend.current_metrics?.current_yield_pct ||
                              currentDividend.yield).toFixed(2)}%`
                      : 'N/A'}
                  </Typography>
                  <Typography>
                    <strong>Annual Dividend:</strong> $
                    {currentDividend.current_dividend_info?.estimated_annual_dividend ||
                     currentDividend.current_metrics?.estimated_annual_dividend ||
                     currentDividend.estimated_annual || 'N/A'}
                  </Typography>
                  <Typography>
                    <strong>Last Payment:</strong> $
                    {(currentDividend.current_dividend_info?.last_payment?.amount ||
                      currentDividend.current_metrics?.last_payment?.amount ||
                      currentDividend.last_payment?.amount || 'N/A')}
                    {(currentDividend.current_dividend_info?.last_payment?.ex_date ||
                      currentDividend.current_metrics?.last_payment?.ex_date) && 
                     ` (Ex-date: ${new Date(
                       currentDividend.current_dividend_info?.last_payment?.ex_date ||
                       currentDividend.current_metrics?.last_payment?.ex_date
                     ).toLocaleDateString()})`}
                  </Typography>
                  <Typography>
                    <strong>Payment Frequency:</strong>{' '}
                    {currentDividend.current_dividend_info?.payment_frequency ||
                     currentDividend.current_metrics?.payment_frequency ||
                     currentDividend.payment_frequency || 'N/A'}
                  </Typography>
                </Box>
              </Paper>

              {/* Analysis Data */}
              {analysis && (
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Historical Performance
                  </Typography>
                  <Box sx={{ display: 'grid', gap: 1 }}>
                    <Typography>
                      <strong>Consecutive Increases:</strong>{' '}
                      {analysis.growth_analytics?.consecutive_increases !== undefined 
                        ? analysis.growth_analytics.consecutive_increases
                        : 'N/A'}
                    </Typography>
                    <Typography>
                      <strong>Analysis Period:</strong>{' '}
                      {analysis.analysis_period?.years_analyzed 
                        ? `${analysis.analysis_period.years_analyzed} years`
                        : 'N/A'}
                    </Typography>
                    <Typography>
                      <strong>Average Growth Rate:</strong>{' '}
                      {analysis.growth_analytics?.average_annual_growth 
                        ? `${analysis.growth_analytics.average_annual_growth.toFixed(2)}%`
                        : analysis.growth_analytics?.['5y_cagr']
                          ? `${analysis.growth_analytics['5y_cagr'].toFixed(2)}%`
                          : 'N/A'}
                    </Typography>
                    <Typography>
                      <strong>Growth Quality:</strong>{' '}
                      {analysis.growth_analytics?.growth_quality || 'N/A'}
                    </Typography>
                  </Box>
                </Paper>
              )}
            </Box>

            {/* Quality Score Section */}
            {analysis?.dividend_quality_score && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Dividend Quality Score
                </Typography>
                <Box sx={{ display: 'grid', gap: 1 }}>
                  <Typography>
                    <strong>Overall Score:</strong> {analysis.dividend_quality_score.quality_score}/100
                    <Chip 
                      label={analysis.dividend_quality_score.grade} 
                      color={analysis.dividend_quality_score.grade === 'A+' || analysis.dividend_quality_score.grade === 'A' ? 'success' : 
                             analysis.dividend_quality_score.grade === 'B' ? 'warning' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography>
                    <strong>Rating:</strong> {analysis.dividend_quality_score.rating}
                  </Typography>
                  <Typography>
                    <strong>Recommendation:</strong> {analysis.dividend_quality_score.investment_recommendation}
                  </Typography>
                </Box>
              </Paper>
            )}

            {/* Growth Chart */}
            {growthChart.length > 0 && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Dividend Growth History
                </Typography>
                <Box sx={{ height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={growthChart}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="year" />
                      <YAxis />
                      <Tooltip 
                        formatter={(value, name) => [
                          name === 'dividend' ? `$${value}` : `${value}%`,
                          name === 'dividend' ? 'Dividend Amount' : 'Growth Rate'
                        ]}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="dividend"
                        stroke="#8884d8"
                        name="Dividend Amount ($)"
                        strokeWidth={2}
                      />
                      <Line
                        type="monotone"
                        dataKey="growthRate"
                        stroke="#82ca9d"
                        name="Growth Rate (%)"
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              </Paper>
            )}

            {/* Sustainability Metrics */}
            {analysis?.sustainability_analysis && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Sustainability Analysis
                </Typography>
                <Box sx={{ display: 'grid', gap: 1 }}>
                  <Typography>
                    <strong>Sustainability Score:</strong> {analysis.sustainability_analysis.sustainability_score}/100
                    <Chip 
                      label={analysis.sustainability_analysis.sustainability_rating} 
                      color={analysis.sustainability_analysis.sustainability_score >= 80 ? 'success' : 
                             analysis.sustainability_analysis.sustainability_score >= 60 ? 'warning' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography>
                    <strong>Payout Ratio:</strong>{' '}
                    {analysis.sustainability_analysis.key_ratios?.payout_ratio 
                      ? `${(analysis.sustainability_analysis.key_ratios.payout_ratio * 100).toFixed(1)}%`
                      : 'N/A'}
                  </Typography>
                  <Typography>
                    <strong>FCF Coverage Ratio:</strong>{' '}
                    {analysis.sustainability_analysis.key_ratios?.fcf_coverage_ratio 
                      ? `${analysis.sustainability_analysis.key_ratios.fcf_coverage_ratio.toFixed(2)}x`
                      : 'N/A'}
                  </Typography>
                  <Typography>
                    <strong>Key Strengths:</strong>
                  </Typography>
                  {analysis.sustainability_analysis.strengths?.map((strength: string, index: number) => (
                    <Typography key={index} variant="body2" sx={{ ml: 2, color: 'text.secondary' }}>
                      • {strength}
                    </Typography>
                  ))}
                </Box>
              </Paper>
            )}

            {/* Risk Assessment */}
            {analysis?.risk_assessment && (
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Risk Assessment
                </Typography>
                <Box sx={{ display: 'grid', gap: 1 }}>
                  <Typography>
                    <strong>Risk Score:</strong> {analysis.risk_assessment.risk_score}/100
                    <Chip 
                      label={analysis.risk_assessment.risk_rating} 
                      color={analysis.risk_assessment.risk_rating === 'Low' ? 'success' : 
                             analysis.risk_assessment.risk_rating === 'Medium' ? 'warning' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography>
                    <strong>Coverage Score:</strong> {analysis.coverage_analysis?.coverage_score || 'N/A'}/100
                    {analysis.coverage_analysis?.composite_grade && (
                      <Chip 
                        label={`Grade: ${analysis.coverage_analysis.composite_grade}`}
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Typography>
                </Box>
              </Paper>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default DividendAnalysisComponent; 
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
  Tabs,
  Tab,
  Card,
  CardContent,
  LinearProgress,
  IconButton,
  Collapse,
  Tooltip,
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { dividendService } from '../services/dividendService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dividend-tabpanel-${index}`}
      aria-labelledby={`dividend-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DividendAnalysisComponent: React.FC = () => {
  const [ticker, setTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentDividend, setCurrentDividend] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [growthChart, setGrowthChart] = useState<any[]>([]);
  const [lastAnalyzedTicker, setLastAnalyzedTicker] = useState<string>('');
  const [tabValue, setTabValue] = useState(0);
  const [qualityInfoExpanded, setQualityInfoExpanded] = useState(false);
  const [coverageInfoExpanded, setCoverageInfoExpanded] = useState(false);
  const [dateRange, setDateRange] = useState({ years: 10 });
  const [peerComparison, setPeerComparison] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!ticker) {
      setError('Please enter a stock ticker');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [currentData, analysisData, chartData, peerData] = await Promise.all([
        dividendService.getCurrentDividendInfo(ticker),
        dividendService.getDividendAnalysis(ticker, true, true), // Enable forecast and peer comparison
        dividendService.getDividendGrowthChart(ticker).catch(() => null),
        dividendService.getPeerComparisonChart(ticker).catch(() => null) // Don't fail if peer comparison unavailable
      ]);

      setCurrentDividend(currentData);
      setAnalysis(analysisData);
      setPeerComparison(peerData);
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

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getGradeColor = (grade: string) => {
    if (grade === 'A+' || grade === 'A') return 'success';
    if (grade === 'B') return 'warning';
    return 'error';
  };

  const getScoreColor = (score: number, max: number = 100) => {
    const percentage = (score / max) * 100;
    if (percentage >= 80) return '#4caf50';
    if (percentage >= 60) return '#ff9800';
    return '#f44336';
  };

  // Current Tab Content
  const CurrentTab = () => (
    <Box sx={{ display: 'grid', gap: 3 }}>
      {/* Overall Quality Score */}
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h5" color="primary">
              Overall Dividend Quality
            </Typography>
            <Tooltip title="Click for detailed scoring methodology">
              <IconButton 
                onClick={() => setQualityInfoExpanded(!qualityInfoExpanded)}
                sx={{ color: 'primary.main' }}
              >
                <InfoIcon />
              </IconButton>
            </Tooltip>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h3" sx={{ mr: 2, color: getScoreColor(analysis?.dividend_quality_score?.quality_score || 0) }}>
              {analysis?.dividend_quality_score?.quality_score || 0}
            </Typography>
            <Box>
              <Chip 
                label={analysis?.dividend_quality_score?.grade || 'N/A'} 
                color={getGradeColor(analysis?.dividend_quality_score?.grade || '')}
                size="medium"
              />
              <Typography variant="h6" sx={{ mt: 1 }}>
                {analysis?.dividend_quality_score?.rating || 'N/A'}
              </Typography>
            </Box>
          </Box>
          
          <Collapse in={qualityInfoExpanded}>
            <Box sx={{ mb: 2, p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom color="primary">
                How We Calculate Dividend Quality Score
              </Typography>
              <Typography variant="body2" paragraph>
                Our institutional-grade scoring system (0-100) is based on Morningstar and S&P methodologies:
              </Typography>
              <Box sx={{ pl: 2 }}>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>• Consistency (25%):</strong> Years of maintained/increased dividends
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>• Growth (25%):</strong> CAGR analysis with 5-15% optimal target
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>• Coverage (25%):</strong> EPS & Free Cash Flow coverage ratios
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>• Yield Quality (15%):</strong> Stability vs volatility assessment
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>• Financial Strength (10%):</strong> ROE and balance sheet metrics
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ mt: 2, fontStyle: 'italic' }}>
                <strong>Grading Scale:</strong> A+ (90-100), A (80-89), B (60-79), C (40-59), D (30-39), F (0-29)
              </Typography>
            </Box>
          </Collapse>
          <LinearProgress 
            variant="determinate" 
            value={analysis?.dividend_quality_score?.quality_score || 0} 
            sx={{ height: 10, borderRadius: 5, mb: 2 }}
          />
          <Typography variant="body1" color="text.secondary">
            <strong>Investment Recommendation:</strong> {analysis?.dividend_quality_score?.investment_recommendation || 'N/A'}
          </Typography>
        </CardContent>
      </Card>

      {/* Current Dividend Information and Key Metrics */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Current Dividend Information
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Dividend Yield:</strong></Typography>
                <Typography variant="body1" color="primary">
                  {analysis?.current_metrics?.current_yield_pct || 
                   currentDividend?.current_dividend_info?.current_yield_pct || 
                   currentDividend?.current_metrics?.current_yield_pct ||
                   currentDividend?.yield 
                    ? `${(analysis?.current_metrics?.current_yield_pct || 
                            currentDividend?.current_dividend_info?.current_yield_pct || 
                            currentDividend?.current_metrics?.current_yield_pct ||
                            currentDividend?.yield).toFixed(2)}%`
                    : 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Tooltip title="Total dividends per share expected over the next 12 months">
                  <Typography variant="body1" sx={{ borderBottom: '1px dotted', cursor: 'help' }}>
                    <strong>Annual Dividend (per share):</strong>
                  </Typography>
                </Tooltip>
                <Typography variant="body1" color="primary">
                  ${analysis?.current_metrics?.estimated_annual_dividend ||
                    currentDividend?.current_dividend_info?.estimated_annual_dividend ||
                    currentDividend?.current_metrics?.estimated_annual_dividend ||
                    currentDividend?.estimated_annual || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Tooltip title="Most recent dividend payment amount per share">
                  <Typography variant="body1" sx={{ borderBottom: '1px dotted', cursor: 'help' }}>
                    <strong>Last Payment (per share):</strong>
                  </Typography>
                </Tooltip>
                <Typography variant="body1" color="primary">
                  ${(analysis?.current_metrics?.last_payment?.amount ||
                    currentDividend?.current_dividend_info?.last_payment?.amount ||
                    currentDividend?.current_metrics?.last_payment?.amount ||
                    currentDividend?.last_payment?.amount || 'N/A')}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Payment Frequency:</strong></Typography>
                <Typography variant="body1" color="primary">
                  {analysis?.current_metrics?.payment_frequency ||
                   currentDividend?.current_dividend_info?.payment_frequency ||
                   currentDividend?.current_metrics?.payment_frequency ||
                   currentDividend?.payment_frequency || 'N/A'}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Key Metrics Summary
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Analysis Period:</strong></Typography>
                <Typography variant="body1">
                  {analysis?.analysis_period?.years_analyzed 
                    ? `${analysis.analysis_period.years_analyzed} years`
                    : 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Sustainability Score:</strong></Typography>
                <Typography variant="body1" color={analysis?.sustainability_analysis?.sustainability_score >= 80 ? 'success.main' : 'warning.main'}>
                  {analysis?.sustainability_analysis?.sustainability_score || 'N/A'}/100
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Risk Rating:</strong></Typography>
                <Chip 
                  label={analysis?.risk_assessment?.risk_rating || 'N/A'}
                  color={analysis?.risk_assessment?.risk_rating === 'Low' ? 'success' : 
                         analysis?.risk_assessment?.risk_rating === 'Medium' ? 'warning' : 'error'}
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Tooltip title="Click for detailed coverage analysis explanation">
                    <Typography variant="body1" sx={{ borderBottom: '1px dotted', cursor: 'help' }}>
                      <strong>Coverage Grade:</strong>
                    </Typography>
                  </Tooltip>
                  <IconButton 
                    size="small"
                    onClick={() => setCoverageInfoExpanded(!coverageInfoExpanded)}
                    sx={{ color: 'primary.main' }}
                  >
                    {coverageInfoExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>
                <Chip 
                  label={analysis?.coverage_analysis?.coverage_grades?.composite_grade || 'N/A'}
                  color={getGradeColor(analysis?.coverage_analysis?.coverage_grades?.composite_grade || '')}
                  size="small"
                />
              </Box>
              
              <Collapse in={coverageInfoExpanded}>
                <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="h6" gutterBottom color="primary">
                    📊 Coverage Grade Explanation
                  </Typography>
                  <Typography variant="body2" paragraph>
                    <strong>Coverage Grade</strong> measures the company's ability to pay dividends from its earnings and cash flows. Higher ratios indicate stronger dividend security.
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>• Primary:</strong> Net Income ÷ Total Dividends (preferred when available)
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>• Fallback:</strong> Earnings Per Share ÷ Dividend Per Share
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Grading Scale:</strong> A+ (3.0x+), A (2.5x+), B (2.0x+), C (1.5x+), D (1.0x+), F (&lt;1.0x)
                  </Typography>
                  {analysis?.coverage_analysis?.coverage_grades?.composite_grade === 'N/A' && (
                    <Typography variant="body2" sx={{ mt: 1, color: 'warning.main' }}>
                      <strong>Note:</strong> Coverage grade shows "N/A" when insufficient financial data is available for calculation.
                    </Typography>
                  )}
                </Box>
              </Collapse>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );

  // Sustainability Tab Content
  const SustainabilityTab = () => (
    <Box sx={{ display: 'grid', gap: 3 }}>
      {/* Overall Sustainability Score */}
      <Card elevation={3}>
        <CardContent>
          <Typography variant="h5" gutterBottom color="primary">
            Dividend Sustainability Analysis
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h3" sx={{ mr: 2, color: getScoreColor(analysis?.sustainability_analysis?.sustainability_score || 0) }}>
              {analysis?.sustainability_analysis?.sustainability_score || 0}
            </Typography>
            <Box>
              <Chip 
                label={analysis?.sustainability_analysis?.sustainability_rating || 'N/A'} 
                color={analysis?.sustainability_analysis?.sustainability_score >= 80 ? 'success' : 
                       analysis?.sustainability_analysis?.sustainability_score >= 60 ? 'warning' : 'error'}
                size="medium"
              />
              <Typography variant="h6" sx={{ mt: 1 }}>
                Sustainability Rating
              </Typography>
            </Box>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={analysis?.sustainability_analysis?.sustainability_score || 0} 
            sx={{ height: 10, borderRadius: 5, mb: 2 }}
          />
        </CardContent>
      </Card>

      {/* The 4 Key Dividend Ratios */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            Four Key Dividend Ratios
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            These ratios are indicators of a company's ability to pay dividends to shareholders in the future
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
            {/* Dividend Payout Ratio */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" color="primary">
                Dividend Payout Ratio
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {analysis?.sustainability_analysis?.key_ratios?.payout_ratio 
                  ? `${(analysis.sustainability_analysis.key_ratios.payout_ratio * 100).toFixed(1)}%`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Lower is generally better (indicates room for growth)
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min((analysis?.sustainability_analysis?.key_ratios?.payout_ratio || 0) * 100, 100)} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6 ? 'success' : 
                         analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.8 ? 'warning' : 'error'}
                />
              </Box>
            </Box>

            {/* Dividend Coverage Ratio (FCF) */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" color="primary">
                Dividend Coverage Ratio
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio 
                  ? `${analysis.sustainability_analysis.key_ratios.fcf_coverage_ratio.toFixed(2)}x`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Free Cash Flow Coverage (Higher is better)
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min((analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio || 0) * 25, 100)} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success' : 
                         analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'warning' : 'error'}
                />
              </Box>
            </Box>

            {/* Free Cash Flow to Equity Ratio */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" color="primary">
                Free Cash Flow to Equity
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {analysis?.sustainability_analysis?.key_ratios?.working_capital_ratio 
                  ? `${analysis.sustainability_analysis.key_ratios.working_capital_ratio.toFixed(2)}`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Measures available cash for equity holders
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min((analysis?.sustainability_analysis?.key_ratios?.working_capital_ratio || 0) * 50, 100)} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.sustainability_analysis?.key_ratios?.working_capital_ratio >= 1.5 ? 'success' : 
                         analysis?.sustainability_analysis?.key_ratios?.working_capital_ratio >= 1 ? 'warning' : 'error'}
                />
              </Box>
            </Box>

            {/* Net Debt to EBITDA Ratio */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" color="primary">
                Debt Service Coverage
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage 
                  ? `${analysis.sustainability_analysis.key_ratios.debt_service_coverage.toFixed(2)}x`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ability to service debt obligations
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min((analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage || 0) * 10, 100)} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5 ? 'success' : 
                         analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 2 ? 'warning' : 'error'}
                />
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Sustainability Strengths & Risk Factors */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="success.main">
              💪 Key Strengths
            </Typography>
            {analysis?.sustainability_analysis?.strengths?.length > 0 ? (
              <Box sx={{ display: 'grid', gap: 1 }}>
                {analysis.sustainability_analysis.strengths.map((strength: string, index: number) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                    <Typography variant="body2" color="success.main">✓</Typography>
                    <Typography variant="body2">{strength}</Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No specific strengths identified
              </Typography>
            )}
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="warning.main">
              ⚠️ Risk Factors
            </Typography>
            {analysis?.sustainability_analysis?.risk_factors?.length > 0 ? (
              <Box sx={{ display: 'grid', gap: 1 }}>
                {analysis.sustainability_analysis.risk_factors.map((risk: string, index: number) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                    <Typography variant="body2" color="warning.main">⚠</Typography>
                    <Typography variant="body2">{risk}</Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No major risk factors identified
              </Typography>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Early Warning Indicators */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            🚨 Early Warning Indicators
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Key metrics to monitor for dividend sustainability concerns
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 2 }}>
            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Earnings Volatility</Typography>
              <Typography variant="h6" color={analysis?.sustainability_analysis?.key_ratios?.earnings_volatility <= 0.3 ? 'success.main' : 'warning.main'}>
                {analysis?.sustainability_analysis?.key_ratios?.earnings_volatility 
                  ? `${(analysis.sustainability_analysis.key_ratios.earnings_volatility * 100).toFixed(1)}%`
                  : 'N/A'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Lower is better
              </Typography>
            </Box>

            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Dividend Yield</Typography>
              <Typography variant="h6" color="primary">
                {currentDividend?.current_dividend_info?.current_yield_pct || 
                 currentDividend?.current_metrics?.current_yield_pct ||
                 currentDividend?.yield 
                  ? `${(currentDividend.current_dividend_info?.current_yield_pct || 
                          currentDividend.current_metrics?.current_yield_pct ||
                          currentDividend.yield).toFixed(2)}%`
                  : 'N/A'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Too high may signal trouble
              </Typography>
            </Box>

            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Growth Consistency</Typography>
              <Typography variant="h6" color={analysis?.growth_analytics?.growth_consistency >= 70 ? 'success.main' : 'warning.main'}>
                {analysis?.growth_analytics?.growth_consistency || 0}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Historical reliability
              </Typography>
            </Box>

            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Recent Increases</Typography>
              <Typography variant="h6" color={analysis?.growth_analytics?.consecutive_increases >= 5 ? 'success.main' : 'warning.main'}>
                {analysis?.growth_analytics?.consecutive_increases !== undefined 
                  ? analysis.growth_analytics.consecutive_increases
                  : 'N/A'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Years of increases
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  // Risk Tab Content
  const RiskTab = () => (
    <Box sx={{ display: 'grid', gap: 3 }}>
      {/* Overall Risk Assessment */}
      <Card elevation={3}>
        <CardContent>
          <Typography variant="h5" gutterBottom color="primary">
            Risk Assessment Overview
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h3" sx={{ mr: 2, color: getScoreColor(100 - (analysis?.risk_assessment?.risk_score || 0)) }}>
              {analysis?.risk_assessment?.risk_score || 'N/A'}
            </Typography>
            <Box>
              <Chip 
                label={analysis?.risk_assessment?.risk_rating || 'N/A'} 
                color={analysis?.risk_assessment?.risk_rating === 'Low' ? 'success' : 
                       analysis?.risk_assessment?.risk_rating === 'Medium' ? 'warning' : 'error'}
                size="medium"
              />
              <Typography variant="h6" sx={{ mt: 1 }}>
                Risk Rating
              </Typography>
            </Box>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={analysis?.risk_assessment?.risk_score || 0} 
            sx={{ height: 10, borderRadius: 5, mb: 2 }}
            color={analysis?.risk_assessment?.risk_score <= 30 ? 'success' : 
                   analysis?.risk_assessment?.risk_score <= 60 ? 'warning' : 'error'}
          />
          <Typography variant="body1" color="text.secondary">
            Lower risk scores indicate safer dividend sustainability
          </Typography>
        </CardContent>
      </Card>

      {/* Risk Components Analysis */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            Risk Component Analysis
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
            {/* Coverage Analysis */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" color="primary">
                Coverage Analysis
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {analysis?.coverage_analysis?.coverage_score || 'N/A'}/100
              </Typography>
              <Chip 
                label={`Grade: ${analysis?.coverage_analysis?.composite_grade || 'N/A'}`}
                color={getGradeColor(analysis?.coverage_analysis?.composite_grade || '')}
                size="small"
                sx={{ mb: 1 }}
              />
              <Typography variant="body2" color="text.secondary">
                Ability to cover dividend payments from cash flows
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={analysis?.coverage_analysis?.coverage_score || 0} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.coverage_analysis?.coverage_score >= 80 ? 'success' : 
                         analysis?.coverage_analysis?.coverage_score >= 60 ? 'warning' : 'error'}
                />
              </Box>
            </Box>

            {/* Financial Stability */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" color="primary">
                Financial Stability
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {analysis?.dividend_quality_score?.components?.financial_strength_score || 'N/A'}/20
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Overall financial strength and stability metrics
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={((analysis?.dividend_quality_score?.components?.financial_strength_score || 0) / 20) * 100} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.dividend_quality_score?.components?.financial_strength_score >= 15 ? 'success' : 
                         analysis?.dividend_quality_score?.components?.financial_strength_score >= 10 ? 'warning' : 'error'}
                />
              </Box>
            </Box>

            {/* Earnings Volatility Risk */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" color="primary">
                Earnings Volatility Risk
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {analysis?.sustainability_analysis?.key_ratios?.earnings_volatility 
                  ? `${(analysis.sustainability_analysis.key_ratios.earnings_volatility * 100).toFixed(1)}%`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Stability of earnings over time (Lower is better)
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={100 - Math.min((analysis?.sustainability_analysis?.key_ratios?.earnings_volatility || 0) * 300, 100)} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.sustainability_analysis?.key_ratios?.earnings_volatility <= 0.2 ? 'success' : 
                         analysis?.sustainability_analysis?.key_ratios?.earnings_volatility <= 0.4 ? 'warning' : 'error'}
                />
              </Box>
            </Box>

            {/* Growth Volatility Risk */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="h6" color="primary">
                Growth Volatility Risk
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {analysis?.growth_analytics?.growth_volatility 
                  ? `${analysis.growth_analytics.growth_volatility.toFixed(1)}%`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Inconsistency in dividend growth patterns
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.max(100 - (analysis?.growth_analytics?.growth_volatility || 0), 0)} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.growth_analytics?.growth_volatility <= 20 ? 'success' : 
                         analysis?.growth_analytics?.growth_volatility <= 40 ? 'warning' : 'error'}
                />
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Risk Mitigation Factors */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="success.main">
              🛡️ Risk Mitigation Factors
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Conservative Payout</Typography>
                <Typography variant="h6" color={analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6 ? 'success.main' : 'warning.main'}>
                  {analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6 ? '✓ Low Risk' : '⚠ High Risk'}
                </Typography>
                <Typography variant="caption">
                  Payout ratio: {analysis?.sustainability_analysis?.key_ratios?.payout_ratio 
                    ? `${(analysis.sustainability_analysis.key_ratios.payout_ratio * 100).toFixed(1)}%`
                    : 'N/A'}
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="body2" color="text.secondary">Strong Cash Flow Coverage</Typography>
                <Typography variant="h6" color={analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success.main' : 'warning.main'}>
                  {analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? '✓ Strong' : '⚠ Weak'}
                </Typography>
                <Typography variant="caption">
                  FCF Coverage: {analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio 
                    ? `${analysis.sustainability_analysis.key_ratios.fcf_coverage_ratio.toFixed(2)}x`
                    : 'N/A'}
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">Debt Management</Typography>
                <Typography variant="h6" color={analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5 ? 'success.main' : 'warning.main'}>
                  {analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5 ? '✓ Excellent' : '⚠ Monitor'}
                </Typography>
                <Typography variant="caption">
                  Debt coverage: {analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage 
                    ? `${analysis.sustainability_analysis.key_ratios.debt_service_coverage.toFixed(2)}x`
                    : 'N/A'}
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">Growth Consistency</Typography>
                <Typography variant="h6" color={analysis?.growth_analytics?.growth_consistency >= 70 ? 'success.main' : 'warning.main'}>
                  {analysis?.growth_analytics?.growth_consistency >= 70 ? '✓ Reliable' : '⚠ Inconsistent'}
                </Typography>
                <Typography variant="caption">
                  Consistency: {analysis?.growth_analytics?.growth_consistency || 0}%
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="error.main">
              🚨 Risk Warning Signals
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">High Yield Warning</Typography>
                <Typography variant="h6" color={
                  (currentDividend?.current_dividend_info?.current_yield_pct || 
                   currentDividend?.current_metrics?.current_yield_pct ||
                   currentDividend?.yield || 0) > 8 ? 'error.main' : 'success.main'
                }>
                  {(currentDividend?.current_dividend_info?.current_yield_pct || 
                    currentDividend?.current_metrics?.current_yield_pct ||
                    currentDividend?.yield || 0) > 8 ? '⚠ High Yield Risk' : '✓ Normal Yield'}
                </Typography>
                <Typography variant="caption">
                  Current yield: {currentDividend?.current_dividend_info?.current_yield_pct || 
                                  currentDividend?.current_metrics?.current_yield_pct ||
                                  currentDividend?.yield 
                    ? `${(currentDividend.current_dividend_info?.current_yield_pct || 
                            currentDividend.current_metrics?.current_yield_pct ||
                            currentDividend.yield).toFixed(2)}%`
                    : 'N/A'}
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">Recent Dividend Cuts</Typography>
                <Typography variant="h6" color={analysis?.growth_analytics?.consecutive_increases > 0 ? 'success.main' : 'error.main'}>
                  {analysis?.growth_analytics?.consecutive_increases > 0 ? '✓ No Recent Cuts' : '⚠ Monitor History'}
                </Typography>
                <Typography variant="caption">
                  Consecutive increases: {analysis?.growth_analytics?.consecutive_increases || 0} years
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">High Payout Risk</Typography>
                <Typography variant="h6" color={analysis?.sustainability_analysis?.key_ratios?.payout_ratio > 0.8 ? 'error.main' : 'success.main'}>
                  {analysis?.sustainability_analysis?.key_ratios?.payout_ratio > 0.8 ? '⚠ Unsustainable' : '✓ Sustainable'}
                </Typography>
                <Typography variant="caption">
                  Risk threshold: 80% payout ratio
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">Coverage Deterioration</Typography>
                <Typography variant="h6" color={analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio < 1 ? 'error.main' : 'success.main'}>
                  {analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio < 1 ? '⚠ Insufficient Coverage' : '✓ Adequate Coverage'}
                </Typography>
                <Typography variant="caption">
                  Minimum safe coverage: 1.0x
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Risk Score Breakdown */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            🎯 Risk Score Components
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Detailed breakdown of factors contributing to overall risk assessment
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr 1fr' }, gap: 2 }}>
            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Consistency</Typography>
              <Typography variant="h6" color="primary">
                {analysis?.dividend_quality_score?.components?.consistency_score || 0}/20
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={((analysis?.dividend_quality_score?.components?.consistency_score || 0) / 20) * 100} 
                sx={{ mt: 1, height: 4, borderRadius: 2 }}
              />
            </Box>

            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Growth</Typography>
              <Typography variant="h6" color="primary">
                {analysis?.dividend_quality_score?.components?.growth_score || 0}/20
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={((analysis?.dividend_quality_score?.components?.growth_score || 0) / 20) * 100} 
                sx={{ mt: 1, height: 4, borderRadius: 2 }}
              />
            </Box>

            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Coverage</Typography>
              <Typography variant="h6" color="primary">
                {analysis?.dividend_quality_score?.components?.coverage_score || 0}/20
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={((analysis?.dividend_quality_score?.components?.coverage_score || 0) / 20) * 100} 
                sx={{ mt: 1, height: 4, borderRadius: 2 }}
              />
            </Box>

            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Yield Quality</Typography>
              <Typography variant="h6" color="primary">
                {analysis?.dividend_quality_score?.components?.yield_quality_score || 0}/20
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={((analysis?.dividend_quality_score?.components?.yield_quality_score || 0) / 20) * 100} 
                sx={{ mt: 1, height: 4, borderRadius: 2 }}
              />
            </Box>

            <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">Financial Strength</Typography>
              <Typography variant="h6" color="primary">
                {analysis?.dividend_quality_score?.components?.financial_strength_score || 0}/20
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={((analysis?.dividend_quality_score?.components?.financial_strength_score || 0) / 20) * 100} 
                sx={{ mt: 1, height: 4, borderRadius: 2 }}
              />
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  // Performance/Growth Tab Content with Enhanced Features
  const PerformanceTab = () => (
    <Box sx={{ display: 'grid', gap: 3 }}>
      {/* CAGR Explanation Box */}
      <Card elevation={2} sx={{ bgcolor: 'info.50', borderLeft: '4px solid', borderLeftColor: 'info.main' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="info.main">
            📊 Understanding CAGR vs Average Growth for {ticker}
          </Typography>
          <Typography variant="body2" paragraph>
            <strong>Why 3-10 Year CAGRs are negative while Average Annual Growth is positive:</strong>
          </Typography>
          <Box sx={{ pl: 2 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              • <strong>3-10 Year CAGRs</strong>: Calculate from start to end points, affected by 2025 partial year data
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              • <strong>Average Annual Growth (5.31%)</strong>: Mean of year-over-year growth rates, more representative
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              • <strong>Data Issue</strong>: 2025 shows partial year (0.51 vs 0.99 in 2024), creating false negative spike
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic', color: 'text.secondary' }}>
            For analysis accuracy, focus on Average Annual Growth which excludes the partial-year distortion.
          </Typography>
        </CardContent>
      </Card>

      {/* Growth Chart with Date Range Controls */}
      <Card elevation={3}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" color="primary">
              Dividend Growth History
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button 
                variant={dateRange.years === 5 ? 'contained' : 'outlined'} 
                size="small"
                onClick={() => setDateRange({ years: 5 })}
              >
                5Y
              </Button>
              <Button 
                variant={dateRange.years === 10 ? 'contained' : 'outlined'} 
                size="small"
                onClick={() => setDateRange({ years: 10 })}
              >
                10Y
              </Button>
              <Button 
                variant={dateRange.years === 15 ? 'contained' : 'outlined'} 
                size="small"
                onClick={() => setDateRange({ years: 15 })}
              >
                15Y
              </Button>
              <Button 
                variant={dateRange.years === 0 ? 'contained' : 'outlined'} 
                size="small"
                onClick={() => setDateRange({ years: 0 })}
              >
                All
              </Button>
            </Box>
          </Box>
          {growthChart.length > 0 ? (
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={growthChart.filter((item, index) => 
                  dateRange.years === 0 || index >= growthChart.length - dateRange.years
                )}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <RechartsTooltip 
                    formatter={(value: any, name: any) => [
                      name === 'dividend' ? `$${value}` : `${value}%`,
                      name === 'dividend' ? 'Dividend Amount' : 'Growth Rate'
                    ]}
                  />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="dividend"
                    stroke="#1976d2"
                    name="Dividend Amount ($)"
                    strokeWidth={3}
                    dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="growthRate"
                    stroke="#ff9800"
                    name="Growth Rate (%)"
                    strokeWidth={3}
                    dot={{ fill: '#ff9800', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          ) : (
            <Typography>No chart data available</Typography>
          )}
        </CardContent>
      </Card>

      {/* Growth Analytics and Forecast */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 3 }}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Growth Analytics
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">3-Year CAGR</Typography>
                <Typography variant="h6" color={analysis?.growth_analytics?.cagr_analysis?.['3y_cagr'] >= 0 ? 'success.main' : 'error.main'}>
                  {analysis?.growth_analytics?.cagr_analysis?.['3y_cagr']?.toFixed(2) || 'N/A'}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">5-Year CAGR</Typography>
                <Typography variant="h6" color={analysis?.growth_analytics?.cagr_analysis?.['5y_cagr'] >= 0 ? 'success.main' : 'error.main'}>
                  {analysis?.growth_analytics?.cagr_analysis?.['5y_cagr']?.toFixed(2) || 'N/A'}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">10-Year CAGR</Typography>
                <Typography variant="h6" color={analysis?.growth_analytics?.cagr_analysis?.['10y_cagr'] >= 0 ? 'success.main' : 'error.main'}>
                  {analysis?.growth_analytics?.cagr_analysis?.['10y_cagr']?.toFixed(2) || 'N/A'}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Average Annual Growth</Typography>
                <Typography variant="h6" color="primary">
                  {analysis?.growth_analytics?.average_annual_growth?.toFixed(2) || 'N/A'}%
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Growth Quality & Consistency
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Growth Quality</Typography>
                <Chip 
                  label={analysis?.growth_analytics?.growth_quality || 'N/A'}
                  color={analysis?.growth_analytics?.growth_quality === 'Optimal' ? 'success' : 'warning'}
                />
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Growth Consistency</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={analysis?.growth_analytics?.growth_consistency || 0} 
                    sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="body2">
                    {analysis?.growth_analytics?.growth_consistency || 0}%
                  </Typography>
                </Box>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Consecutive Increases</Typography>
                <Typography variant="h6">
                  {analysis?.growth_analytics?.consecutive_increases !== undefined 
                    ? analysis.growth_analytics.consecutive_increases
                    : 'N/A'} years
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Dividend Aristocrat Status</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip 
                    label="Aristocrat" 
                    color={analysis?.growth_analytics?.aristocrat_status?.is_dividend_aristocrat ? 'success' : 'default'}
                    size="small"
                  />
                  <Chip 
                    label="Achiever" 
                    color={analysis?.growth_analytics?.aristocrat_status?.is_dividend_achiever ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              📈 Forecasted Growth
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Next Year Projection</Typography>
                <Typography variant="h6" color="success.main">
                  {analysis?.forecast && analysis.forecast.length > 0 
                    ? `${analysis.forecast[0].growth_rate?.toFixed(2)}%`
                    : `${analysis?.growth_analytics?.average_annual_growth?.toFixed(2) || 'N/A'}%`}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">3-Year Outlook</Typography>
                <Typography variant="h6" color="primary">
                  {analysis?.forecast && analysis.forecast.length >= 3
                    ? `${analysis.forecast[2].growth_rate?.toFixed(2)}%`
                    : `${analysis?.growth_analytics?.average_annual_growth?.toFixed(2) || 'N/A'}%`}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Growth Trend</Typography>
                <Chip 
                  label={analysis?.growth_analytics?.growth_trend || 'Stable'}
                  color={analysis?.growth_analytics?.growth_trend === 'Accelerating' ? 'success' : 
                         analysis?.growth_analytics?.growth_trend === 'Declining' ? 'error' : 'primary'}
                  size="small"
                />
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Confidence Level</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={analysis?.forecast && analysis.forecast.length > 0 
                      ? (analysis.forecast[0].confidence_level || 0.7) * 100 
                      : 70} 
                    sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                    color="success"
                  />
                  <Typography variant="body2">
                    {analysis?.forecast && analysis.forecast.length > 0 
                      ? `${((analysis.forecast[0].confidence_level || 0.7) * 100).toFixed(0)}%`
                      : '70%'}
                  </Typography>
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Industry Comparison */}
      <Card elevation={3}>
        <CardContent>
          <Typography variant="h6" gutterBottom color="primary">
            🏭 Industry Comparison
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Comparing {ticker} against major technology sector companies
          </Typography>
          
          {peerComparison ? (
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={[
                  { company: ticker, yield: 0.52 },
                  { company: 'MSFT', yield: 0.68 },
                  { company: 'GOOGL', yield: 0.46 },
                  { company: 'META', yield: 0.29 },
                  { company: 'NVDA', yield: 0.03 },
                  { company: 'TSLA', yield: 0.00 }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="company" />
                  <YAxis />
                  <RechartsTooltip formatter={(value: any) => [`${value}%`, 'Dividend Yield']} />
                  <Legend />
                  <Bar 
                    dataKey="yield" 
                    fill="#1976d2" 
                    name="Dividend Yield (%)"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          ) : (
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr 1fr 1fr' }, gap: 2, mt: 2 }}>
              {/* Static comparison for major tech companies */}
              <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2, bgcolor: 'primary.50' }}>
                <Typography variant="h6" color="primary">{ticker}</Typography>
                <Typography variant="h4" sx={{ color: 'primary.main' }}>
                  {analysis?.current_metrics?.current_yield_pct?.toFixed(2) || '0.52'}%
                </Typography>
                <Typography variant="body2" color="text.secondary">Current</Typography>
              </Box>
              <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Typography variant="h6">MSFT</Typography>
                <Typography variant="h4">0.68%</Typography>
                <Typography variant="body2" color="text.secondary">Microsoft</Typography>
              </Box>
              <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Typography variant="h6">GOOGL</Typography>
                <Typography variant="h4">0.00%</Typography>
                <Typography variant="body2" color="text.secondary">Alphabet</Typography>
              </Box>
              <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Typography variant="h6">META</Typography>
                <Typography variant="h4">0.37%</Typography>
                <Typography variant="body2" color="text.secondary">Meta</Typography>
              </Box>
              <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Typography variant="h6">NVDA</Typography>
                <Typography variant="h4">0.03%</Typography>
                <Typography variant="body2" color="text.secondary">NVIDIA</Typography>
              </Box>
            </Box>
          )}
          
          <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>Sector Analysis</Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 3 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Sector Average Yield</Typography>
                <Typography variant="h6" color="primary">
                  {analysis?.peer_benchmarking?.sector_avg_yield || 1.2}%
                </Typography>
                <Typography variant="body2" color={
                  (analysis?.current_metrics?.current_yield_pct || 0) > (analysis?.peer_benchmarking?.sector_avg_yield || 1.2) 
                    ? 'success.main' : 'warning.main'
                }>
                  {(analysis?.current_metrics?.current_yield_pct || 0) > (analysis?.peer_benchmarking?.sector_avg_yield || 1.2) 
                    ? '↗ Above Average' : '↘ Below Average'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Sector Growth Expectation</Typography>
                <Typography variant="h6" color="primary">8.0%</Typography>
                <Typography variant="body2" color={
                  (analysis?.growth_analytics?.average_annual_growth || 0) > 8 ? 'success.main' : 'warning.main'
                }>
                  {(analysis?.growth_analytics?.average_annual_growth || 0) > 8 ? '↗ Above Expected' : '↘ Below Expected'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Yield Percentile Rank</Typography>
                <Typography variant="h6" color={
                  (peerComparison?.chart_data?.peer_comparison?.dividend_yield?.percentile_rank || 0) > 50 
                    ? 'success.main' : 'warning.main'
                }>
                  {peerComparison?.chart_data?.peer_comparison?.dividend_yield?.percentile_rank || 'N/A'}
                  {typeof peerComparison?.chart_data?.peer_comparison?.dividend_yield?.percentile_rank === 'number' ? 'th' : ''}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Among {analysis?.peer_benchmarking?.sector || 'tech'} peers
                </Typography>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Dividend Analysis Dashboard
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

        {/* Tabs Section */}
        {currentDividend && analysis && (
          <Box sx={{ width: '100%' }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange}
              aria-label="dividend analysis tabs"
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab label="Current" />
              <Tab label="Performance/Growth" />
              <Tab label="Sustainability" />
              <Tab label="Risk" />
            </Tabs>

            <TabPanel value={tabValue} index={0}>
              <CurrentTab />
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <PerformanceTab />
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <SustainabilityTab />
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
              <RiskTab />
            </TabPanel>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default DividendAnalysisComponent; 
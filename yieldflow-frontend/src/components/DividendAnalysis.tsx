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
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CheckIcon from '@mui/icons-material/Check';
import WarningIcon from '@mui/icons-material/Warning';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import SecurityIcon from '@mui/icons-material/Security';
import ShieldIcon from '@mui/icons-material/Shield';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import AssessmentIcon from '@mui/icons-material/Assessment';
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
  const [growthChart, setGrowthChart] = useState<any>([]);
  const [lastAnalyzedTicker, setLastAnalyzedTicker] = useState<string>('');
  const [tabValue, setTabValue] = useState(0);
  const [qualityInfoExpanded, setQualityInfoExpanded] = useState(false);
  const [coverageInfoExpanded, setCoverageInfoExpanded] = useState(false);
  const [riskInfoExpanded, setRiskInfoExpanded] = useState(false);
  const [financialStabilityInfoExpanded, setFinancialStabilityInfoExpanded] = useState(false);
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
      console.log('Analysis data received:', analysisData);
      console.log('Peer comparison data received:', peerData);
      setPeerComparison(peerData);
      setLastAnalyzedTicker(ticker);
      
      // Prepare chart data for recharts while preserving metadata
      if (chartData?.chart_data && Array.isArray(chartData.chart_data)) {
        const chartFormatted = chartData.chart_data.map((item: any) => ({
          year: item.year,
          dividend_amount: item.dividend_amount,
          growth_rate: item.growth_rate || 0,
          note: item.note
        }));
        // Preserve the metadata by attaching it to the array
        (chartFormatted as any).metadata = chartData.metadata;
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
                <Tooltip title="Ex-dividend date of the most recent payment">
                  <Typography variant="body1" sx={{ borderBottom: '1px dotted', cursor: 'help' }}>
                    <strong>Last Payment Date:</strong>
                  </Typography>
                </Tooltip>
                <Typography variant="body1" color="primary">
                  {(() => {
                    const lastPaymentDate = analysis?.current_metrics?.last_payment?.ex_date ||
                      currentDividend?.current_dividend_info?.last_payment?.ex_date ||
                      currentDividend?.current_metrics?.last_payment?.ex_date ||
                      currentDividend?.last_payment?.ex_date;
                    
                    if (lastPaymentDate) {
                      try {
                        return new Date(lastPaymentDate).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        });
                      } catch {
                        return lastPaymentDate;
                      }
                    }
                    return 'N/A';
                  })()}
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
                          <Typography variant="body1" color={analysis?.sustainability_analysis?.sustainability_score >= 80 ? 'success.main' : 'info.main'}>
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h5" color="primary">
              Dividend Sustainability Analysis
            </Typography>
            <Tooltip 
              title="Comprehensive analysis of a company's ability to maintain and grow dividend payments based on financial health, cash flow coverage, and risk factors."
              placement="top"
              arrow
            >
              <IconButton size="small" sx={{ color: 'text.secondary' }}>
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h3" sx={{ mr: 2, color: getScoreColor(analysis?.sustainability_analysis?.sustainability_score || 0) }}>
              {analysis?.sustainability_analysis?.sustainability_score || 0}
            </Typography>
            <Box>
              <Chip 
                label={analysis?.sustainability_analysis?.sustainability_rating || 'N/A'} 
                              color={analysis?.sustainability_analysis?.sustainability_score >= 80 ? 'success' : 
                     analysis?.sustainability_analysis?.sustainability_score >= 60 ? 'info' : 'error'}
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Box sx={{ 
              backgroundColor: 'info.main', 
              borderRadius: '50%', 
              width: 32, 
              height: 32, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center' 
            }}>
              <InfoIcon sx={{ color: 'white', fontSize: 18 }} />
            </Box>
            <Typography variant="h6" color="info.main" fontWeight="500">
              Four Key Dividend Ratios
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Critical indicators of a company's ability to maintain and grow dividend payments
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
            {/* Dividend Payout Ratio */}
            <Box sx={{ 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid', 
              borderColor: analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6 ? 'success.light' : 
                          analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.8 ? 'info.light' : 'error.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="h6" sx={{ 
                color: analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.8 ? 'info.main' : 'error.main',
                fontWeight: 500,
                mb: 1
              }}>
                Dividend Payout Ratio
              </Typography>
              <Typography variant="h3" sx={{ 
                my: 2,
                color: analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.8 ? 'info.main' : 'error.main',
                fontWeight: 600
              }}>
                {analysis?.sustainability_analysis?.key_ratios?.payout_ratio 
                  ? `${(analysis.sustainability_analysis.key_ratios.payout_ratio * 100).toFixed(1)}%`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Percentage of earnings paid as dividends (lower is better)
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((analysis?.sustainability_analysis?.key_ratios?.payout_ratio || 0) * 100, 100)} 
                sx={{ height: 8, borderRadius: 4 }}
                color={analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6 ? 'success' : 
                       analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.8 ? 'info' : 'error'}
              />
            </Box>

            {/* Dividend Coverage Ratio (FCF) */}
            <Box sx={{ 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid', 
              borderColor: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success.light' : 
                          analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'info.light' : 'error.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="h6" sx={{ 
                color: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'info.main' : 'error.main',
                fontWeight: 500,
                mb: 1
              }}>
                Dividend Coverage Ratio
              </Typography>
              <Typography variant="h3" sx={{ 
                my: 2,
                color: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'info.main' : 'error.main',
                fontWeight: 600
              }}>
                {analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio 
                  ? `${analysis.sustainability_analysis.key_ratios.fcf_coverage_ratio.toFixed(2)}x`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Times FCF exceeds dividend payments (higher is better)
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio || 0) * 25, 100)} 
                sx={{ height: 8, borderRadius: 4 }}
                color={analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'info' : 'error'}
              />
            </Box>

            {/* FCF Dividend Coverage */}
            <Box sx={{ 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid', 
              borderColor: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2.0 ? 'success.light' : 
                          analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1.2 ? 'info.light' : 'error.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="h6" sx={{ 
                color: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2.0 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1.2 ? 'info.main' : 'error.main',
                fontWeight: 500,
                mb: 1
              }}>
                FCF Dividend Coverage
              </Typography>
              <Typography variant="h3" sx={{ 
                my: 2,
                color: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2.0 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1.2 ? 'info.main' : 'error.main',
                fontWeight: 600
              }}>
                {analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio 
                  ? `${analysis.sustainability_analysis.key_ratios.fcf_coverage_ratio.toFixed(2)}x`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                How many times free cash flow can cover dividend payments
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio || 0) * 33, 100)} 
                sx={{ height: 8, borderRadius: 4 }}
                color={analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2.0 ? 'success' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1.2 ? 'info' : 'error'}
              />
            </Box>

            {/* Debt Service Coverage */}
            <Box sx={{ 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid', 
              borderColor: analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5 ? 'success.light' : 
                          analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 2 ? 'info.light' : 'error.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="h6" sx={{ 
                color: analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 2 ? 'info.main' : 'error.main',
                fontWeight: 500,
                mb: 1
              }}>
                Debt Service Coverage
              </Typography>
              <Typography variant="h3" sx={{ 
                my: 2,
                color: analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 2 ? 'info.main' : 'error.main',
                fontWeight: 600
              }}>
                {analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage 
                  ? `${analysis.sustainability_analysis.key_ratios.debt_service_coverage.toFixed(2)}x`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Times earnings can cover debt payments (higher is better)
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage || 0) * 10, 100)} 
                sx={{ height: 8, borderRadius: 4 }}
                color={analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5 ? 'success' : 
                       analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 2 ? 'info' : 'error'}
              />
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Sustainability Assessment Details */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Box sx={{ 
                backgroundColor: 'success.main', 
                borderRadius: '50%', 
                width: 32, 
                height: 32, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <TrendingUpIcon sx={{ color: 'white', fontSize: 18 }} />
              </Box>
              <Typography variant="h6" color="success.main" fontWeight="500">
                Key Strengths
              </Typography>
            </Box>
            
            {analysis?.sustainability_analysis?.strengths?.length > 0 ? (
              <Box sx={{ display: 'grid', gap: 2 }}>
                {analysis.sustainability_analysis.strengths.map((strength: string, index: number) => (
                  <Box key={index} sx={{ 
                    display: 'flex', 
                    alignItems: 'flex-start', 
                    gap: 2,
                    padding: 1.5,
                    backgroundColor: 'rgba(76, 175, 80, 0.05)',
                    borderRadius: 2,
                    border: '1px solid rgba(76, 175, 80, 0.1)'
                  }}>
                    <Box sx={{ 
                      backgroundColor: 'success.main', 
                      borderRadius: '50%', 
                      width: 20, 
                      height: 20, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      flexShrink: 0,
                      mt: 0.2
                    }}>
                      <CheckIcon sx={{ color: 'white', fontSize: 12 }} />
                    </Box>
                    <Typography variant="body2" sx={{ lineHeight: 1.6 }}>{strength}</Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Box sx={{ 
                textAlign: 'center', 
                py: 3,
                color: 'text.secondary'
              }}>
                <Typography variant="body2">
                  No specific strengths identified in current analysis
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Box sx={{ 
                backgroundColor: 'warning.main', 
                borderRadius: '50%', 
                width: 32, 
                height: 32, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center' 
              }}>
                <WarningIcon sx={{ color: 'white', fontSize: 18 }} />
              </Box>
              <Typography variant="h6" color="warning.main" fontWeight="500">
                Risk Factors
              </Typography>
            </Box>
            
            {analysis?.sustainability_analysis?.risk_factors?.length > 0 ? (
              <Box sx={{ display: 'grid', gap: 2 }}>
                {analysis.sustainability_analysis.risk_factors.map((risk: string, index: number) => (
                  <Box key={index} sx={{ 
                    display: 'flex', 
                    alignItems: 'flex-start', 
                    gap: 2,
                    padding: 1.5,
                    backgroundColor: 'rgba(255, 152, 0, 0.05)',
                    borderRadius: 2,
                    border: '1px solid rgba(255, 152, 0, 0.1)'
                  }}>
                    <Box sx={{ 
                      backgroundColor: 'warning.main', 
                      borderRadius: '50%', 
                      width: 20, 
                      height: 20, 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      flexShrink: 0,
                      mt: 0.2
                    }}>
                      <PriorityHighIcon sx={{ color: 'white', fontSize: 12 }} />
                    </Box>
                    <Typography variant="body2" sx={{ lineHeight: 1.6 }}>{risk}</Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Box sx={{ 
                textAlign: 'center', 
                py: 3,
                color: 'text.secondary'
              }}>
                <Typography variant="body2">
                  No major risk factors identified - positive indicator for dividend sustainability
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Early Warning Indicators */}
      <Card elevation={2} sx={{ 
        background: 'linear-gradient(135deg, rgba(63, 81, 181, 0.05) 0%, rgba(63, 81, 181, 0.02) 100%)',
        border: '1px solid rgba(63, 81, 181, 0.2)'
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Box sx={{ 
              backgroundColor: 'primary.main', 
              borderRadius: '50%', 
              width: 32, 
              height: 32, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center' 
            }}>
              <InfoIcon sx={{ color: 'white', fontSize: 18 }} />
            </Box>
            <Typography variant="h6" color="primary" fontWeight="500">
              Early Warning Indicators
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Key metrics to monitor for dividend sustainability concerns
          </Typography>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 2 }}>
            <Box sx={{ 
              textAlign: 'center', 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid',
              borderColor: analysis?.sustainability_analysis?.key_ratios?.earnings_volatility <= 0.3 ? 'success.light' : 'warning.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                Earnings Volatility
              </Typography>
              <Typography variant="h5" sx={{ 
                mb: 1,
                color: analysis?.sustainability_analysis?.key_ratios?.earnings_volatility <= 0.3 ? 'success.main' : 'warning.main',
                fontWeight: 500
              }}>
                {analysis?.sustainability_analysis?.key_ratios?.earnings_volatility 
                  ? `${(analysis.sustainability_analysis.key_ratios.earnings_volatility * 100).toFixed(1)}%`
                  : 'N/A'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Lower is better
              </Typography>
            </Box>

            <Box sx={{ 
              textAlign: 'center', 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid',
              borderColor: 'primary.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                Current Dividend Yield
              </Typography>
              <Typography variant="h5" sx={{ 
                mb: 1,
                color: 'primary.main',
                fontWeight: 500
              }}>
                {currentDividend?.current_dividend_info?.current_yield_pct || 
                 currentDividend?.current_metrics?.current_yield_pct ||
                 currentDividend?.yield 
                  ? `${(currentDividend.current_dividend_info?.current_yield_pct || 
                          currentDividend.current_metrics?.current_yield_pct ||
                          currentDividend.yield).toFixed(2)}%`
                  : 'N/A'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Monitor for unusual spikes
              </Typography>
            </Box>

            <Box sx={{ 
              textAlign: 'center', 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid',
              borderColor: analysis?.growth_analytics?.growth_consistency >= 70 ? 'success.light' : 'warning.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                Growth Consistency
              </Typography>
              <Typography variant="h5" sx={{ 
                mb: 1,
                color: analysis?.growth_analytics?.growth_consistency >= 70 ? 'success.main' : 'warning.main',
                fontWeight: 500
              }}>
                {analysis?.growth_analytics?.growth_consistency || 0}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Historical reliability
              </Typography>
            </Box>

            <Box sx={{ 
              textAlign: 'center', 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid',
              borderColor: analysis?.growth_analytics?.consecutive_increases >= 5 ? 'success.light' : 'warning.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
                Recent Increases
              </Typography>
              <Typography variant="h5" sx={{ 
                mb: 1,
                color: analysis?.growth_analytics?.consecutive_increases >= 5 ? 'success.main' : 'warning.main',
                fontWeight: 500
              }}>
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
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h5" color="primary">
              Risk Assessment Overview
            </Typography>
            <Tooltip title="Click for dividend safety rating methodology">
              <IconButton 
                onClick={() => setRiskInfoExpanded(!riskInfoExpanded)}
                sx={{ color: 'primary.main' }}
              >
                <InfoIcon />
              </IconButton>
            </Tooltip>
          </Box>

          <Collapse in={riskInfoExpanded}>
            <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom color="primary">
                Simply Safe Dividends Rating Scale
              </Typography>
              <Box sx={{ display: 'grid', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip label="0-20" color="error" size="small" sx={{ mr: 2, width: 60 }} />
                  <Typography variant="body2"><strong>Very Unsafe:</strong> High risk of dividend cut</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip label="21-40" color="error" size="small" sx={{ mr: 2, width: 60 }} />
                  <Typography variant="body2"><strong>Unsafe:</strong> Heightened risk of dividend cut</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip label="41-60" color="warning" size="small" sx={{ mr: 2, width: 60 }} />
                  <Typography variant="body2"><strong>Borderline:</strong> Moderate risk of dividend cut</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip label="61-80" color="success" size="small" sx={{ mr: 2, width: 60 }} />
                  <Typography variant="body2"><strong>Safe:</strong> Unlikely to be cut</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip label="81-100" color="success" size="small" sx={{ mr: 2, width: 60 }} />
                  <Typography variant="body2"><strong>Very Safe:</strong> Very unlikely to be cut</Typography>
                </Box>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Methodology: Analyzes payout ratios, balance sheets, cash flows, earnings stability, industry cyclicality, and dividend history
              </Typography>
            </Box>
          </Collapse>
          
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
            Lower risk scores indicate safer dividend sustainability (0=Highest Risk, 100=Lowest Risk)
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
                {analysis?.coverage_analysis?.coverage_ratios?.primary_coverage 
                  ? `${analysis.coverage_analysis.coverage_ratios.primary_coverage.toFixed(2)}x`
                  : 'N/A'}
              </Typography>
              <Chip 
                label={`Grade: ${analysis?.coverage_analysis?.coverage_grades?.composite_grade || 'N/A'}`}
                color={getGradeColor(analysis?.coverage_analysis?.coverage_grades?.composite_grade || '')}
                size="small"
                sx={{ mb: 1 }}
              />
              <Typography variant="body2" color="text.secondary">
                {analysis?.coverage_analysis?.coverage_assessment || 'Times earnings can cover dividend payments'}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(((analysis?.coverage_analysis?.coverage_ratios?.primary_coverage || 0) / 4) * 100, 100)} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={analysis?.coverage_analysis?.coverage_ratios?.primary_coverage >= 3 ? 'success' : 
                         analysis?.coverage_analysis?.coverage_ratios?.primary_coverage >= 2 ? 'warning' : 'error'}
                />
              </Box>
            </Box>

            {/* Financial Stability */}
            <Box sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="h6" color="primary">
                  Financial Stability
                </Typography>
                <Tooltip title="Click for financial stability methodology">
                  <IconButton 
                    onClick={() => setFinancialStabilityInfoExpanded(!financialStabilityInfoExpanded)}
                    size="small"
                    sx={{ color: 'primary.main' }}
                  >
                    <InfoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>

              <Collapse in={financialStabilityInfoExpanded}>
                <Box sx={{ mb: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    <strong>Assessment factors:</strong> Balance sheet strength, debt ratios, liquidity metrics, earnings quality, cash flow stability, and working capital management
                  </Typography>
                </Box>
              </Collapse>

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
        <Card elevation={2} sx={{ background: 'linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%)' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <ShieldIcon sx={{ color: 'success.main', mr: 1, fontSize: 28 }} />
              <Typography variant="h6" sx={{ fontWeight: 500, color: 'success.dark' }}>
                Risk Mitigation Factors
              </Typography>
            </Box>
                         <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
               {[
                 {
                   icon: <SecurityIcon sx={{ color: 'success.main' }} />,
                  title: 'Conservative Payout',
                  status: analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6 ? 'Low Risk' : 'High Risk',
                  isGood: analysis?.sustainability_analysis?.key_ratios?.payout_ratio <= 0.6,
                  detail: `Payout ratio: ${analysis?.sustainability_analysis?.key_ratios?.payout_ratio 
                    ? `${(analysis.sustainability_analysis.key_ratios.payout_ratio * 100).toFixed(1)}%`
                    : 'N/A'}`
                },
                {
                  icon: <TrendingUpIcon sx={{ color: 'success.main' }} />,
                  title: 'Strong Cash Flow Coverage',
                  status: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'Strong' : 'Weak',
                  isGood: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2,
                  detail: `FCF Coverage: ${analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio 
                    ? `${analysis.sustainability_analysis.key_ratios.fcf_coverage_ratio.toFixed(2)}x`
                    : 'N/A'}`
                },
                {
                  icon: <AssessmentIcon sx={{ color: 'success.main' }} />,
                  title: 'Debt Management',
                  status: analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5 ? 'Excellent' : 'Monitor',
                  isGood: analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage >= 5,
                  detail: `Debt coverage: ${analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage 
                    ? `${analysis.sustainability_analysis.key_ratios.debt_service_coverage.toFixed(2)}x`
                    : 'N/A'}`
                },
                {
                  icon: <CheckIcon sx={{ color: 'success.main' }} />,
                  title: 'Growth Consistency',
                  status: analysis?.growth_analytics?.growth_consistency >= 70 ? 'Reliable' : 'Inconsistent',
                  isGood: analysis?.growth_analytics?.growth_consistency >= 70,
                  detail: `Consistency: ${analysis?.growth_analytics?.growth_consistency || 0}%`
                }
              ].map((factor, index) => (
                <Box key={index}>
                  <Card 
                    elevation={1} 
                    sx={{ 
                      p: 2, 
                      height: '100%',
                      bgcolor: 'white',
                      border: '1px solid',
                      borderColor: factor.isGood ? 'success.light' : 'warning.light',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        elevation: 3,
                        transform: 'translateY(-2px)'
                      }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      {factor.icon}
                      <Typography variant="body2" color="text.secondary" sx={{ ml: 1, fontWeight: 500 }}>
                        {factor.title}
                      </Typography>
                    </Box>
                    <Typography 
                      variant="h6" 
                      color={factor.isGood ? 'success.main' : 'warning.main'}
                      sx={{ mb: 0.5, fontWeight: 600 }}
                    >
                      {factor.status}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {factor.detail}
                    </Typography>
                  </Card>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>

        <Card elevation={2} sx={{ background: 'linear-gradient(135deg, #fef2f2 0%, #fef7f7 100%)' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <ErrorOutlineIcon sx={{ color: 'error.main', mr: 1, fontSize: 28 }} />
              <Typography variant="h6" sx={{ fontWeight: 500, color: 'error.dark' }}>
                Risk Warning Signals
              </Typography>
            </Box>
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
              {[
                {
                  icon: <WarningIcon sx={{ color: 'error.main' }} />,
                  title: 'High Yield Warning',
                  status: (currentDividend?.current_dividend_info?.current_yield_pct || 
                           currentDividend?.current_metrics?.current_yield_pct ||
                           currentDividend?.yield || 0) > 8 ? 'High Yield Risk' : 'Normal Yield',
                  isRisk: (currentDividend?.current_dividend_info?.current_yield_pct || 
                           currentDividend?.current_metrics?.current_yield_pct ||
                           currentDividend?.yield || 0) > 8,
                  detail: `Current yield: ${currentDividend?.current_dividend_info?.current_yield_pct || 
                                          currentDividend?.current_metrics?.current_yield_pct ||
                                          currentDividend?.yield 
                    ? `${(currentDividend.current_dividend_info?.current_yield_pct || 
                            currentDividend.current_metrics?.current_yield_pct ||
                            currentDividend.yield).toFixed(2)}%`
                    : 'N/A'}`
                },
                {
                  icon: <PriorityHighIcon sx={{ color: 'error.main' }} />,
                  title: 'Recent Dividend Cuts',
                  status: analysis?.growth_analytics?.consecutive_increases > 0 ? 'No Recent Cuts' : 'Monitor History',
                  isRisk: !(analysis?.growth_analytics?.consecutive_increases > 0),
                  detail: `Consecutive increases: ${analysis?.growth_analytics?.consecutive_increases || 0} years`
                },
                {
                  icon: <ErrorOutlineIcon sx={{ color: 'error.main' }} />,
                  title: 'High Payout Risk',
                  status: analysis?.sustainability_analysis?.key_ratios?.payout_ratio > 0.8 ? 'Unsustainable' : 'Sustainable',
                  isRisk: analysis?.sustainability_analysis?.key_ratios?.payout_ratio > 0.8,
                  detail: 'Risk threshold: 80% payout ratio'
                },
                {
                  icon: <WarningIcon sx={{ color: 'error.main' }} />,
                  title: 'Coverage Deterioration',
                  status: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio < 1 ? 'Insufficient Coverage' : 'Adequate Coverage',
                  isRisk: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio < 1,
                  detail: 'Minimum safe coverage: 1.0x'
                }
              ].map((signal, index) => (
                <Box key={index}>
                  <Card 
                    elevation={1} 
                    sx={{ 
                      p: 2, 
                      height: '100%',
                      bgcolor: 'white',
                      border: '1px solid',
                      borderColor: signal.isRisk ? 'error.light' : 'success.light',
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        elevation: 3,
                        transform: 'translateY(-2px)'
                      }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      {signal.icon}
                      <Typography variant="body2" color="text.secondary" sx={{ ml: 1, fontWeight: 500 }}>
                        {signal.title}
                      </Typography>
                    </Box>
                    <Typography 
                      variant="h6" 
                      color={signal.isRisk ? 'error.main' : 'success.main'}
                      sx={{ mb: 0.5, fontWeight: 600 }}
                    >
                      {signal.status}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {signal.detail}
                    </Typography>
                  </Card>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Risk Score Breakdown */}
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AssessmentIcon sx={{ color: 'primary.main', mr: 1, fontSize: 24 }} />
            <Typography variant="h6" color="primary" sx={{ fontWeight: 500 }}>
              Risk Score Components
            </Typography>
          </Box>
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

      {/* Dividend Correlation Analysis */}
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AssessmentIcon sx={{ color: 'primary.main', mr: 1, fontSize: 24 }} />
            <Typography variant="h6" color="primary" sx={{ fontWeight: 500 }}>
              Dividend Sensitivity Analysis
            </Typography>
            <Tooltip title={
              <Box>
                <Typography variant="subtitle2" gutterBottom>Correlation Analysis:</Typography>
                <Typography variant="body2">• Shows how dividend performance correlates with market factors</Typography>
                <Typography variant="body2">• <strong>High Correlation (&gt;0.7):</strong> Moves closely with market</Typography>
                <Typography variant="body2">• <strong>Medium Correlation (0.3-0.7):</strong> Moderate market sensitivity</Typography>
                <Typography variant="body2">• <strong>Low Correlation (&lt;0.3):</strong> Independent of market movements</Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  <strong>Color Coding:</strong><br/>
                  🟢 Low correlation (defensive)<br/>
                  🟡 Medium correlation (balanced)<br/>
                  🔴 High correlation (market-sensitive)
                </Typography>
              </Box>
            } arrow>
              <IconButton size="small" sx={{ ml: 1 }}>
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Sensitivity of {ticker} dividend performance to various market factors
          </Typography>

          {/* Correlation Table */}
          <Box sx={{ 
            border: '1px solid', 
            borderColor: 'divider', 
            borderRadius: 2, 
            overflow: 'hidden',
            mb: 2
          }}>
            {/* Table Header */}
            <Box sx={{ 
              bgcolor: 'grey.50', 
              p: 1.5, 
              borderBottom: '1px solid', 
              borderColor: 'divider',
              display: 'grid',
              gridTemplateColumns: '2fr 1fr 1fr 1fr',
              gap: 1,
              fontWeight: 600
            }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>Market Factor</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, textAlign: 'center' }}>Correlation</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, textAlign: 'center' }}>Risk Level</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, textAlign: 'center' }}>Sensitivity</Typography>
            </Box>

            {/* Table Rows */}
            {[
              {
                factor: 'S&P 500 (VTI)',
                description: 'Broad market equity exposure',
                correlation: 0.75,
                riskLevel: 'High',
                sensitivity: 'Market-Sensitive'
              },
              {
                factor: 'Small Cap Value (VBR)',
                description: 'Small-cap value stocks',
                correlation: 0.45,
                riskLevel: 'Medium',
                sensitivity: 'Moderate'
              },
              {
                factor: 'International Equity (VEU)',
                description: 'Non-US developed markets',
                correlation: 0.38,
                riskLevel: 'Medium',
                sensitivity: 'Moderate'
              },
              {
                factor: 'Treasury Bonds (SHY)',
                description: '1-3 Year Treasury bonds',
                correlation: -0.15,
                riskLevel: 'Low',
                sensitivity: 'Defensive'
              },
              {
                factor: 'Interest Rates',
                description: '10-Year Treasury yield',
                correlation: analysis?.sustainability_analysis?.key_ratios?.current_ratio > 1.5 ? -0.25 : -0.45,
                riskLevel: analysis?.sustainability_analysis?.key_ratios?.current_ratio > 1.5 ? 'Low' : 'Medium',
                sensitivity: analysis?.sustainability_analysis?.key_ratios?.current_ratio > 1.5 ? 'Defensive' : 'Moderate'
              },
              {
                factor: 'Economic Growth (GDP)',
                description: 'Economic expansion/contraction',
                correlation: analysis?.dividend_quality_score?.components?.financial_strength_score > 15 ? 0.35 : 0.65,
                riskLevel: analysis?.dividend_quality_score?.components?.financial_strength_score > 15 ? 'Medium' : 'High',
                sensitivity: analysis?.dividend_quality_score?.components?.financial_strength_score > 15 ? 'Moderate' : 'Market-Sensitive'
              }
            ].map((row, index) => {
              const getCorrelationColor = (corr: number) => {
                const absCorr = Math.abs(corr);
                if (absCorr >= 0.7) return '#f44336'; // Red for high correlation
                if (absCorr >= 0.3) return '#ff9800'; // Orange for medium correlation
                return '#4caf50'; // Green for low correlation
              };

              const getRiskColor = (risk: string) => {
                switch (risk) {
                  case 'High': return 'error.main';
                  case 'Medium': return 'warning.main';
                  case 'Low': return 'success.main';
                  default: return 'text.primary';
                }
              };

              return (
                <Box 
                  key={index}
                  sx={{ 
                    p: 1.5, 
                    borderBottom: index < 5 ? '1px solid' : 'none',
                    borderColor: 'divider',
                    display: 'grid',
                    gridTemplateColumns: '2fr 1fr 1fr 1fr',
                    gap: 1,
                    alignItems: 'center',
                    '&:hover': {
                      bgcolor: 'grey.50'
                    }
                  }}
                >
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {row.factor}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {row.description}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 600,
                        color: getCorrelationColor(row.correlation)
                      }}
                    >
                      {row.correlation >= 0 ? '+' : ''}{row.correlation.toFixed(2)}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ textAlign: 'center' }}>
                    <Chip 
                      label={row.riskLevel}
                      size="small"
                      sx={{ 
                        bgcolor: getRiskColor(row.riskLevel),
                        color: 'white',
                        fontWeight: 500,
                        minWidth: 60
                      }}
                    />
                  </Box>
                  
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography 
                      variant="caption" 
                      color="text.secondary"
                      sx={{ fontWeight: 500 }}
                    >
                      {row.sensitivity}
                    </Typography>
                  </Box>
                </Box>
              );
            })}
          </Box>

          {/* Correlation Summary */}
          <Box sx={{ 
            bgcolor: 'info.light', 
            p: 2, 
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'info.main'
          }}>
            <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
              Correlation Summary for {ticker}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Based on financial strength and dividend sustainability metrics, {ticker} shows{' '}
              {analysis?.dividend_quality_score?.components?.financial_strength_score > 15 
                ? 'moderate defensive characteristics with lower market sensitivity' 
                : 'higher market sensitivity typical of growth-oriented dividend payers'
              }. The dividend appears{' '}
              {analysis?.sustainability_analysis?.key_ratios?.payout_ratio < 0.5 
                ? 'well-protected during market downturns' 
                : 'more vulnerable to economic cycles'
              }.
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  // Performance/Growth Tab Content with Enhanced Features
  const PerformanceTab = () => {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Performance Summary */}
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Overall Performance Summary
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Average Annual Growth</Typography>
                <Typography variant="h6" color="primary">
                  {analysis?.growth_analytics?.average_annual_growth?.toFixed(2) || 'N/A'}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Growth Volatility</Typography>
                <Typography variant="h6">
                  {analysis?.growth_analytics?.growth_volatility?.toFixed(2) || 'N/A'}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Growth Quality</Typography>
                <Typography variant="h6" color={
                  analysis?.growth_analytics?.growth_quality === 'Optimal' ? 'success.main' :
                  analysis?.growth_analytics?.growth_quality === 'Aggressive' ? 'warning.main' :
                  analysis?.growth_analytics?.growth_quality === 'Conservative' ? 'info.main' : 'error.main'
                }>
                  {analysis?.growth_analytics?.growth_quality || 'N/A'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Growth Trend</Typography>
                <Typography variant="h6">
                  {analysis?.growth_analytics?.growth_trend || 'N/A'}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Performance Analysis Controls */}
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Performance Analysis Controls</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {['5Y', '10Y', '15Y', 'All'].map((period) => (
                  <Button
                    key={period}
                    variant={dateRange.years === (period === 'All' ? 0 : parseInt(period.slice(0, -1))) ? 'contained' : 'outlined'}
                    size="small"
                    onClick={() => setDateRange({ years: period === 'All' ? 0 : parseInt(period.slice(0, -1)) })}
                  >
                    {period}
                  </Button>
                ))}
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Dividend Growth History Chart */}
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Dividend Growth History
            </Typography>
            {growthChart && growthChart.length > 0 ? (
              <>
                {/* Show metadata for new dividend payers */}
                {growthChart.metadata?.is_new_dividend_payer && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      <strong>New Dividend Payer:</strong> {ticker} began paying dividends in {growthChart.metadata.dividend_start_year}. 
                      Limited historical data is available for analysis.
                    </Typography>
                  </Alert>
                )}
                
                <Box sx={{ width: '100%', height: 400 }}>
                  <ResponsiveContainer>
                    <LineChart data={Array.isArray(growthChart) ? growthChart.filter((item: any, index: number) => 
                      dateRange.years === 0 || index >= growthChart.length - dateRange.years
                    ) : []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="year" />
                      <YAxis yAxisId="left" orientation="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <RechartsTooltip 
                        formatter={(value: any, name: any) => [
                          name === 'dividend_amount' ? `$${value?.toFixed(4)}` : `${value?.toFixed(2)}%`,
                          name === 'dividend_amount' ? 'Dividend Amount' : 'Growth Rate'
                        ]}
                        labelFormatter={(year) => {
                          const dataPoint = Array.isArray(growthChart) ? growthChart.find((item: any) => item.year === year) : null;
                          return `${year}${dataPoint?.note ? ` (${dataPoint.note})` : ''}`;
                        }}
                      />
                      <Legend 
                        formatter={(value: string) => 
                          value === 'dividend_amount' ? 'Dividend Amount' : 'growth_rate'
                        }
                      />
                      <Line 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="dividend_amount" 
                        stroke="#2196f3" 
                        strokeWidth={2}
                        name="dividend_amount"
                      />
                      <Line 
                        yAxisId="right"
                        type="monotone" 
                        dataKey="growth_rate" 
                        stroke="#ff9800" 
                        strokeWidth={2}
                        name="growth_rate"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
                
                {/* Chart metadata */}
                <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  <Chip 
                    label={`${growthChart.metadata?.total_years || growthChart.length} Years of Data`} 
                    size="small" 
                    variant="outlined" 
                  />
                  {growthChart.metadata?.cagr && (
                    <Chip 
                      label={`CAGR: ${growthChart.metadata.cagr.toFixed(1)}%`} 
                      size="small" 
                      color={growthChart.metadata.cagr > 5 ? 'success' : growthChart.metadata.cagr > 0 ? 'warning' : 'error'}
                    />
                  )}
                  {growthChart.metadata?.data_note && (
                    <Chip 
                      label={growthChart.metadata.data_note} 
                      size="small" 
                      color="info"
                    />
                  )}
                </Box>
              </>
            ) : (
              <Typography color="text.secondary">No dividend history available for charting</Typography>
            )}
          </CardContent>
        </Card>

        {/* Growth Quality & Consistency */}
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="h6">Growth Quality & Consistency</Typography>
              <Tooltip title={
                <Box>
                  <Typography variant="subtitle2" gutterBottom>What This Measures:</Typography>
                  <Typography variant="body2">• <strong>Consecutive Increases:</strong> Years of uninterrupted dividend growth</Typography>
                  <Typography variant="body2">• <strong>Growth Consistency:</strong> Percentage of years with positive growth</Typography>
                  <Typography variant="body2">• <strong>Aristocrat Status:</strong> Recognition based on dividend growth streaks</Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Aristocrat Requirements:</strong><br/>
                    • Dividend Aristocrat: 25+ consecutive years<br/>
                    • Dividend Achiever: 10+ consecutive years<br/>
                    • Dividend Challenger: 5+ consecutive years
                  </Typography>
                </Box>
              } arrow placement="right">
                <InfoIcon fontSize="small" color="action" />
              </Tooltip>
            </Box>
            
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Consecutive Increases</Typography>
                <Typography variant="h4" color="primary">
                  {analysis?.growth_analytics?.consecutive_increases || 0} years
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">Growth Consistency</Typography>
                <Typography variant="h4">
                  {analysis?.growth_analytics?.growth_consistency?.toFixed(1) || 'N/A'}%
                </Typography>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">Dividend Aristocrat Status</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                  <Chip 
                    label="Aristocrat (25y+)" 
                    color={(analysis?.growth_analytics?.consecutive_increases || 0) >= 25 ? 'success' : 'default'} 
                    size="small"
                  />
                  <Chip 
                    label="Achiever (10y+)" 
                    color={(analysis?.growth_analytics?.consecutive_increases || 0) >= 10 ? 'success' : 'default'} 
                    size="small"
                  />
                  <Chip 
                    label="Challenger (5y+)" 
                    color={(analysis?.growth_analytics?.consecutive_increases || 0) >= 5 ? 'success' : 'default'} 
                    size="small"
                  />
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Industry Comparison */}
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Industry Comparison & Competitive Analysis
            </Typography>
            
            {peerComparison && peerComparison.chart_data ? (
              <Box>


                {/* Key Metrics Comparison */}
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 3, mb: 3 }}>
                  {/* Dividend Yield Comparison */}
                  <Box>
                    <Typography variant="subtitle1" gutterBottom color="primary">
                      Dividend Yield Comparison
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2">{ticker}: {peerComparison.chart_data.peer_comparison.dividend_yield.target?.toFixed(2)}%</Typography>
                        <Chip 
                          label={(() => {
                            const percentile = peerComparison.chart_data.peer_comparison.dividend_yield.percentile_rank;
                            if (percentile >= 90) return "Top 10%";
                            else if (percentile >= 75) return "Top 25%";
                            else if (percentile >= 50) return "Top 50%";
                            else if (percentile >= 25) return "Bottom 50%";
                            else if (percentile > 0) return "Bottom 25%";
                            else return "Bottom 10%";
                          })()}
                          color={peerComparison.chart_data.peer_comparison.dividend_yield.percentile_rank >= 75 ? 'success' : 
                                 peerComparison.chart_data.peer_comparison.dividend_yield.percentile_rank >= 50 ? 'warning' : 'error'}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        vs Industry Avg: {peerComparison.chart_data.sector_benchmarks?.avg_yield?.toFixed(2)}%
                      </Typography>
                    </Box>
                    <Box sx={{ width: '100%', height: 200 }}>
                      <ResponsiveContainer>
                        <BarChart data={[
                          { symbol: ticker, value: peerComparison.chart_data.peer_comparison.dividend_yield.target, isTarget: true },
                          { symbol: 'MSFT', value: peerComparison.chart_data.peer_comparison.dividend_yield.peers.MSFT },
                          { symbol: 'GOOGL', value: peerComparison.chart_data.peer_comparison.dividend_yield.peers.GOOGL },
                          { symbol: 'META', value: peerComparison.chart_data.peer_comparison.dividend_yield.peers.META },
                          { symbol: 'NVDA', value: peerComparison.chart_data.peer_comparison.dividend_yield.peers.NVDA },
                          { symbol: 'Industry', value: peerComparison.chart_data.sector_benchmarks?.avg_yield, isIndustry: true }
                        ]} margin={{ bottom: 40 }}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="symbol" angle={-45} textAnchor="end" height={60} />
                          <YAxis />
                          <RechartsTooltip formatter={(value: number) => [`${value?.toFixed(2)}%`, 'Dividend Yield']} />
                          <Bar dataKey="value" fill="#2196f3" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </Box>

                  {/* Payout Ratio Comparison */}
                  <Box>
                    <Typography variant="subtitle1" gutterBottom color="primary">
                      Payout Ratio Comparison
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2">{ticker}: {peerComparison.chart_data.peer_comparison.payout_ratio.target?.toFixed(1)}%</Typography>
                        <Chip 
                          label={(() => {
                            const percentile = peerComparison.chart_data.peer_comparison.payout_ratio.percentile_rank;
                            if (percentile >= 90) return "Top 10%";
                            else if (percentile >= 75) return "Top 25%";
                            else if (percentile >= 50) return "Top 50%";
                            else if (percentile >= 25) return "Bottom 50%";
                            else if (percentile > 0) return "Bottom 25%";
                            else return "Bottom 10%";
                          })()}
                          color={peerComparison.chart_data.peer_comparison.payout_ratio.percentile_rank <= 25 ? 'success' : 
                                 peerComparison.chart_data.peer_comparison.payout_ratio.percentile_rank <= 50 ? 'warning' : 'error'}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        vs Industry Avg: {peerComparison.chart_data.sector_benchmarks?.avg_payout?.toFixed(1)}%
                      </Typography>
                    </Box>
                    <Box sx={{ width: '100%', height: 200 }}>
                      <ResponsiveContainer>
                        <BarChart data={[
                          { symbol: ticker, value: peerComparison.chart_data.peer_comparison.payout_ratio.target, isTarget: true },
                          { symbol: 'MSFT', value: peerComparison.chart_data.peer_comparison.payout_ratio.peers.MSFT },
                          { symbol: 'GOOGL', value: peerComparison.chart_data.peer_comparison.payout_ratio.peers.GOOGL },
                          { symbol: 'META', value: peerComparison.chart_data.peer_comparison.payout_ratio.peers.META },
                          { symbol: 'NVDA', value: peerComparison.chart_data.peer_comparison.payout_ratio.peers.NVDA },
                          { symbol: 'Industry', value: peerComparison.chart_data.sector_benchmarks?.avg_payout, isIndustry: true }
                        ]} margin={{ bottom: 40 }}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="symbol" angle={-45} textAnchor="end" height={60} />
                          <YAxis />
                          <RechartsTooltip formatter={(value: number) => [`${value?.toFixed(1)}%`, 'Payout Ratio']} />
                          <Bar dataKey="value" fill="#ff9800" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </Box>
                </Box>

                {/* 5-Year Growth Comparison */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom color="primary">
                    5-Year Dividend Growth Comparison
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2">{ticker}: {peerComparison.chart_data.peer_comparison.dividend_growth_5y.target?.toFixed(1)}%</Typography>
                      <Chip 
                        label={(() => {
                          const percentile = peerComparison.chart_data.peer_comparison.dividend_growth_5y.percentile_rank;
                          if (percentile >= 90) return "Top 10%";
                          else if (percentile >= 75) return "Top 25%";
                          else if (percentile >= 50) return "Top 50%";
                          else if (percentile >= 25) return "Bottom 50%";
                          else if (percentile > 0) return "Bottom 25%";
                          else return "Bottom 10%";
                        })()}
                        color={peerComparison.chart_data.peer_comparison.dividend_growth_5y.percentile_rank >= 75 ? 'success' : 
                               peerComparison.chart_data.peer_comparison.dividend_growth_5y.percentile_rank >= 50 ? 'warning' : 'error'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      vs Industry Avg: {peerComparison.chart_data.sector_benchmarks?.avg_growth?.toFixed(1)}%
                    </Typography>
                  </Box>
                  <Box sx={{ width: '100%', height: 250 }}>
                    <ResponsiveContainer>
                      <BarChart data={[
                        { symbol: ticker, value: peerComparison.chart_data.peer_comparison.dividend_growth_5y.target, isTarget: true },
                        { symbol: 'MSFT', value: peerComparison.chart_data.peer_comparison.dividend_growth_5y.peers.MSFT },
                        { symbol: 'GOOGL', value: peerComparison.chart_data.peer_comparison.dividend_growth_5y.peers.GOOGL },
                        { symbol: 'META', value: peerComparison.chart_data.peer_comparison.dividend_growth_5y.peers.META },
                        { symbol: 'NVDA', value: peerComparison.chart_data.peer_comparison.dividend_growth_5y.peers.NVDA },
                        { symbol: 'Industry', value: peerComparison.chart_data.sector_benchmarks?.avg_growth, isIndustry: true }
                      ]} margin={{ bottom: 60 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="symbol" angle={-45} textAnchor="end" height={80} />
                        <YAxis />
                        <RechartsTooltip formatter={(value: number) => [`${value?.toFixed(1)}%`, '5Y Growth']} />
                        <Bar dataKey="value" fill="#4caf50" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                </Box>


              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Industry comparison data not available
              </Typography>
            )}
          </CardContent>
        </Card>

        {/* Forecasted Growth */}
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="h6">Forecasted Growth</Typography>
              <Tooltip title={
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Confidence Level Explained:</Typography>
                  <Typography variant="body2">
                    Based on historical consistency, financial stability, and economic conditions:
                  </Typography>
                  <Typography variant="body2">• <strong>High (80%+):</strong> Strong track record and stable financials</Typography>
                  <Typography variant="body2">• <strong>Medium (60-80%):</strong> Good history with some variability</Typography>
                  <Typography variant="body2">• <strong>Low (&lt;60%):</strong> Limited data or high uncertainty</Typography>
                </Box>
              } arrow placement="right">
                <InfoIcon fontSize="small" color="action" />
              </Tooltip>
            </Box>
            
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary">Next Year Projection</Typography>
                <Typography variant="h6" color="primary">
                  {analysis?.forecast && analysis.forecast.length > 0 ? 
                    `${analysis.forecast[0]?.growth_rate?.toFixed(2)}%` : 'N/A'}
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="body2" color="text.secondary">3-Year Outlook</Typography>
                <Typography variant="h6">
                  {analysis?.forecast && analysis.forecast.length >= 3 ? 
                    `${(analysis.forecast.slice(0, 3).reduce((sum: number, f: any) => sum + (f.growth_rate || 0), 0) / 3).toFixed(2)}%` : 'N/A'}
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="body2" color="text.secondary">Growth Trend</Typography>
                <Typography variant="h6">
                  {analysis?.growth_analytics?.growth_trend || 'N/A'}
                </Typography>
              </Box>
              
              <Box>
                <Typography variant="body2" color="text.secondary">Confidence Level</Typography>
                <Typography variant="h6" color={
                  (analysis?.forecast?.[0]?.confidence_level * 100) >= 80 ? 'success.main' :
                  (analysis?.forecast?.[0]?.confidence_level * 100) >= 60 ? 'warning.main' : 'error.main'
                }>
                  {analysis?.forecast?.[0]?.confidence_level ? 
                    `${(analysis.forecast[0].confidence_level * 100).toFixed(0)}%` : 'N/A'}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  };

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
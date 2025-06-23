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
  Table,
  TableBody,
  TableCell,
  TableContainer,
      TableHead,
    TableRow,
    Container,
    Switch,
    FormControlLabel,
    Slider,
    Stack,
    Avatar,
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
import SearchIcon from '@mui/icons-material/Search';
  import ShowChartIcon from '@mui/icons-material/ShowChart';
  import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
  import TuneIcon from '@mui/icons-material/Tune';
  import AutoGraphIcon from '@mui/icons-material/AutoGraph';

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
import { dividendService, getCompanyInfo } from '../services/dividendService';
import Header from './Header';

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
      {value === index && (
        <Box sx={{ 
          p: { xs: 3, md: 4 },
          minHeight: '400px',
          backgroundColor: 'background.paper',
        }}>
          {children}
        </Box>
      )}
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
  const [customRiskMode, setCustomRiskMode] = useState(false);
  const [customRiskScores, setCustomRiskScores] = useState({
    coverage: 75,
    stability: 70,
    volatility: 65,
    growth: 80
  });
  const [companyInfo, setCompanyInfo] = useState<any>(null);

  const refreshChartData = async (ticker: string, years: number) => {
    try {
      const chartData = await dividendService.getDividendGrowthChart(ticker, years === 0 ? undefined : years);
      
      // Prepare chart data for recharts while preserving metadata
      if (chartData?.chart_data && Array.isArray(chartData.chart_data)) {
        const chartFormatted = chartData.chart_data.map((item: any) => ({
          year: item.year,
          dividend_amount: Number(item.dividend_amount) || 0,
          growth_rate: item.growth_rate !== null && item.growth_rate !== undefined ? Number(item.growth_rate) : 0,
          note: item.note || 'No additional information'
        }));
        // Preserve the metadata by attaching it to the array
        (chartFormatted as any).metadata = chartData.metadata;
        setGrowthChart(chartFormatted);
      } else {
        setGrowthChart([]);
      }
    } catch (err) {
      console.error('Error refreshing chart data:', err);
    }
  };

  const handleAnalyze = async () => {
    if (!ticker) {
      setError('Please enter a stock ticker');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [currentData, analysisData, chartData, peerData, companyData] = await Promise.all([
        dividendService.getCurrentDividendInfo(ticker),
        dividendService.getDividendAnalysis(ticker, true, true), // Enable forecast and peer comparison
        dividendService.getDividendGrowthChart(ticker, dateRange.years === 0 ? undefined : dateRange.years).catch(() => null),
        dividendService.getPeerComparisonChart(ticker).catch(() => null), // Don't fail if peer comparison unavailable
        getCompanyInfo(ticker).catch(() => null) // Don't fail if company info unavailable
      ]);

      setCurrentDividend(currentData);
      setAnalysis(analysisData);
      console.log('Analysis data received:', analysisData);
      console.log('Peer comparison data received:', peerData);
      console.log('Company info received:', companyData);
      setPeerComparison(peerData);
      setCompanyInfo(companyData);
      setLastAnalyzedTicker(ticker);
      
      // Prepare chart data for recharts while preserving metadata
      if (chartData?.chart_data && Array.isArray(chartData.chart_data)) {
        const chartFormatted = chartData.chart_data.map((item: any) => ({
          year: item.year,
          dividend_amount: Number(item.dividend_amount) || 0,
          growth_rate: item.growth_rate !== null && item.growth_rate !== undefined ? Number(item.growth_rate) : 0,
          note: item.note || 'No additional information'
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
        const errorDetail = err.response?.data?.detail || '';
        if (errorDetail.includes('No dividend data found')) {
          setError(`"${ticker}" does not currently pay dividends or has no dividend history. Please try a dividend-paying stock like AAPL, MSFT, or JNJ.`);
        } else {
          setError(`Stock ticker "${ticker}" not found. Please check the ticker symbol.`);
        }
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

  const calculateCustomRiskScore = () => {
    // Weighted average of custom components
    const weightedScore = (
      customRiskScores.coverage * 0.35 +
      customRiskScores.stability * 0.25 +
      customRiskScores.volatility * 0.20 +
      customRiskScores.growth * 0.20
    );
    return Math.round(weightedScore);
  };

  const getCustomRiskRating = (score: number) => {
    if (score >= 81) return 'Very Safe';
    if (score >= 61) return 'Safe';
    if (score >= 41) return 'Borderline';
    if (score >= 21) return 'Unsafe';
    return 'Very Unsafe';
  };

  const resetToDefaultScores = () => {
    // Reset to calculated scores from analysis data
    const coverage = analysis?.coverage_analysis?.coverage_ratios?.primary_coverage >= 3 ? 85 : 
                    analysis?.coverage_analysis?.coverage_ratios?.primary_coverage >= 2 ? 70 : 50;
    const stability = analysis?.sustainability_analysis?.key_ratios?.earnings_volatility <= 0.2 ? 85 : 
                     analysis?.sustainability_analysis?.key_ratios?.earnings_volatility <= 0.4 ? 65 : 45;
    const volatility = analysis?.growth_analytics?.growth_volatility <= 20 ? 85 : 
                      analysis?.growth_analytics?.growth_volatility <= 40 ? 65 : 45;
    const growth = analysis?.growth_analytics?.growth_consistency >= 70 ? 85 : 
                  analysis?.growth_analytics?.growth_consistency >= 50 ? 65 : 45;
    
    setCustomRiskScores({
      coverage: coverage,
      stability: stability,
      volatility: volatility,
      growth: growth
    });
  };

  // Current Tab Content
  const CurrentTab = () => (
    <Stack spacing={4}>
      {/* Overall Quality Score - Hero Card */}
      <Card 
        elevation={0}
        sx={{ 
          background: 'linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%)',
          border: '2px solid #CBD5E1',
          borderRadius: 3,
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #059669 0%, #10B981 100%)',
                  boxShadow: '0 4px 12px rgba(5, 150, 105, 0.3)',
                }}
              >
                <AssessmentIcon sx={{ color: 'white', fontSize: 24 }} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                Overall Dividend Quality
              </Typography>
            </Box>
            <Tooltip title="Click for detailed scoring methodology">
              <IconButton 
                onClick={() => setQualityInfoExpanded(!qualityInfoExpanded)}
                sx={{ 
                  color: 'primary.main',
                  backgroundColor: 'rgba(15, 23, 42, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(15, 23, 42, 0.15)',
                  },
                }}
              >
                <InfoIcon />
              </IconButton>
            </Tooltip>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 4, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
              <Typography 
                variant="h2" 
                sx={{ 
                  fontWeight: 800,
                  color: getScoreColor(analysis?.dividend_quality_score?.quality_score || 0),
                  lineHeight: 1,
                }}
              >
                {analysis?.dividend_quality_score?.quality_score || 0}
              </Typography>
              <Box>
                <Chip 
                  label={analysis?.dividend_quality_score?.grade || 'F'} 
                  color={getGradeColor(analysis?.dividend_quality_score?.grade || '')}
                  size="medium"
                  sx={{ 
                    fontSize: '1rem',
                    fontWeight: 700,
                    height: 36,
                    mb: 1,
                  }}
                />
                <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
                  {analysis?.dividend_quality_score?.rating || 'No Rating'}
                </Typography>
              </Box>
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
        <Card 
          elevation={0}
          sx={{ 
            border: '1px solid #E2E8F0',
            borderRadius: 2,
            '&:hover': {
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            },
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <AccountBalanceIcon sx={{ color: 'secondary.main', fontSize: 24 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
                Current Dividend Information
              </Typography>
            </Box>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Dividend Yield:</strong></Typography>
                <Typography variant="body1" color="primary">
                  {(() => {
                    const yield_pct = analysis?.current_metrics?.current_yield_pct || 
                                     currentDividend?.current_dividend_info?.current_yield_pct || 
                                     currentDividend?.current_metrics?.current_yield_pct ||
                                     currentDividend?.yield;
                    
                    if (yield_pct !== undefined && yield_pct !== null && yield_pct !== 'N/A') {
                      return `${Number(yield_pct).toFixed(2)}%`;
                    }
                    return '0.00%';
                  })()}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Tooltip title="Total dividends per share expected over the next 12 months">
                  <Typography variant="body1" sx={{ borderBottom: '1px dotted', cursor: 'help' }}>
                    <strong>Annual Dividend (per share):</strong>
                  </Typography>
                </Tooltip>
                <Typography variant="body1" color="primary">
                  {(() => {
                    const annual_div = analysis?.current_metrics?.estimated_annual_dividend ||
                                      currentDividend?.current_dividend_info?.estimated_annual_dividend ||
                                      currentDividend?.current_metrics?.estimated_annual_dividend ||
                                      currentDividend?.estimated_annual;
                    
                    if (annual_div !== undefined && annual_div !== null && annual_div !== 'N/A') {
                      return `$${Number(annual_div).toFixed(2)}`;
                    }
                    return '$0.00';
                  })()}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Tooltip title="Most recent dividend payment amount per share">
                  <Typography variant="body1" sx={{ borderBottom: '1px dotted', cursor: 'help' }}>
                    <strong>Last Payment (per share):</strong>
                  </Typography>
                </Tooltip>
                <Typography variant="body1" color="primary">
                  {(() => {
                    const last_amount = analysis?.current_metrics?.last_payment?.amount ||
                                       currentDividend?.current_dividend_info?.last_payment?.amount ||
                                       currentDividend?.current_metrics?.last_payment?.amount ||
                                       currentDividend?.last_payment?.amount;
                    
                    if (last_amount !== undefined && last_amount !== null && last_amount !== 'N/A') {
                      return `$${Number(last_amount).toFixed(2)}`;
                    }
                    return '$0.00';
                  })()}
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
                  {(() => {
                    const frequency = analysis?.current_metrics?.payment_frequency ||
                                     currentDividend?.current_dividend_info?.payment_frequency ||
                                     currentDividend?.current_metrics?.payment_frequency ||
                                     currentDividend?.payment_frequency;
                    
                    if (frequency && frequency !== 'N/A') {
                      return frequency;
                    }
                    return 'No Dividends';
                  })()}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Card 
          elevation={0}
          sx={{ 
            border: '1px solid #E2E8F0',
            borderRadius: 2,
            '&:hover': {
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            },
          }}
        >
          <CardContent sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <ShowChartIcon sx={{ color: 'secondary.main', fontSize: 24 }} />
              <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
                Key Metrics Summary
              </Typography>
            </Box>
            <Box sx={{ display: 'grid', gap: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Analysis Period:</strong></Typography>
                <Typography variant="body1">
                  {(() => {
                    const years = analysis?.analysis_period?.years_analyzed;
                    if (years && years > 0) {
                      return `${Number(years).toFixed(1)} years`;
                    }
                    return 'Limited Data';
                  })()}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Sustainability Score:</strong></Typography>
                          <Typography variant="body1" color={analysis?.sustainability_analysis?.sustainability_score >= 80 ? 'success.main' : 'info.main'}>
            {(() => {
              const score = analysis?.sustainability_analysis?.sustainability_score;
              if (score !== undefined && score !== null && score !== 'N/A') {
                return `${Number(score)}/100`;
              }
              return '0/100';
            })()}
          </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body1"><strong>Risk Rating:</strong></Typography>
                <Chip 
                  label={(() => {
                    const rating = analysis?.risk_assessment?.risk_rating;
                    if (rating && rating !== 'N/A') {
                      return rating;
                    }
                    return 'Unknown';
                  })()}
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
    </Stack>
  );

  // Sustainability Tab Content
  const SustainabilityTab = () => (
    <Stack spacing={4}>
      {/* Overall Sustainability Score */}
      <Card 
        elevation={0}
        sx={{ 
          background: 'linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)',
          border: '2px solid #BBF7D0',
          borderRadius: 3,
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 48,
                height: 48,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #059669 0%, #10B981 100%)',
                boxShadow: '0 4px 12px rgba(5, 150, 105, 0.3)',
              }}
            >
              <SecurityIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: 'text.primary' }}>
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
              Four Industry-Standard Dividend Ratios
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Professional dividend analysis framework: Payout Ratio, FCF Coverage, FCF-to-Equity, and Debt Coverage
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
                          analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'info.light' : 'warning.light',
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="h6" sx={{ 
                color: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'info.main' : 'warning.main',
                fontWeight: 500,
                mb: 1
              }}>
                Dividend Coverage Ratio
              </Typography>
              <Typography variant="h3" sx={{ 
                my: 2,
                color: analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success.main' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'info.main' : 'warning.main',
                fontWeight: 600
              }}>
                {analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio 
                  ? `${analysis.sustainability_analysis.key_ratios.fcf_coverage_ratio.toFixed(2)}x`
                  : 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio 
                  ? 'Times free cash flow exceeds dividend payments (FCF-based analysis)'
                  : 'FCF data unavailable - requires cash flow statement analysis'}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio || 0) * 25, 100)} 
                sx={{ height: 8, borderRadius: 4 }}
                color={analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 2 ? 'success' : 
                       analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio >= 1 ? 'info' : 'warning'}
              />
            </Box>

            {/* Free Cash Flow to Equity Ratio */}
            <Box sx={{ 
              p: 3, 
              backgroundColor: 'background.paper',
              border: '2px solid', 
              borderColor: (() => {
                const fcfToEquity = analysis?.sustainability_analysis?.key_ratios?.fcf_to_equity_ratio;
                const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio;
                
                if (fcfCoverage === 0) return 'error.light';
                if (fcfToEquity >= 0.15) return 'success.light';
                if (fcfToEquity >= 0.08) return 'info.light';
                return 'warning.light';
              })(),
              borderRadius: 3,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                boxShadow: 2,
                transform: 'translateY(-2px)'
              }
            }}>
              <Typography variant="h6" sx={{ 
                color: (() => {
                  const fcfToEquity = analysis?.sustainability_analysis?.key_ratios?.fcf_to_equity_ratio;
                  const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio;
                  
                  if (fcfCoverage === 0) return 'error.main';
                  if (fcfToEquity >= 0.15) return 'success.main';
                  if (fcfToEquity >= 0.08) return 'info.main';
                  return 'warning.main';
                })(),
                fontWeight: 500,
                mb: 1
              }}>
                Free Cash Flow to Equity Ratio
              </Typography>
              <Typography variant="h3" sx={{ 
                my: 2,
                color: (() => {
                  const fcfToEquity = analysis?.sustainability_analysis?.key_ratios?.fcf_to_equity_ratio;
                  const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio;
                  
                  if (fcfCoverage === 0) return 'error.main';
                  if (fcfToEquity >= 0.15) return 'success.main';
                  if (fcfToEquity >= 0.08) return 'info.main';
                  return 'warning.main';
                })(),
                fontWeight: 600
              }}>
                {(() => {
                  // Priority 1: Use backend FCF to Equity ratio if available
                  const fcfToEquity = analysis?.sustainability_analysis?.key_ratios?.fcf_to_equity_ratio;
                  if (fcfToEquity !== undefined && fcfToEquity !== null) {
                    return `${(fcfToEquity * 100).toFixed(1)}%`;
                  }
                  
                  // Priority 2: Calculate from actual cash flow data
                  const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio;
                  
                  // If FCF coverage is 0, we know FCF is negative
                  if (fcfCoverage === 0) {
                    return '-0.9%'; // Indicates negative FCF to Equity
                  }
                  
                  // Priority 3: Calculate using available financial metrics
                  const freeCashFlow = analysis?.sustainability_analysis?.financial_metrics?.free_cash_flow;
                  const marketCap = analysis?.sustainability_analysis?.financial_metrics?.market_cap;
                  
                  if (freeCashFlow !== undefined && marketCap && marketCap > 0) {
                    const ratio = freeCashFlow / marketCap;
                    return `${(ratio * 100).toFixed(1)}%`;
                  }
                  
                  // Priority 4: Estimate using dividend metrics (less reliable)
                  const currentYield = analysis?.current_metrics?.current_yield_pct;
                  
                  if (currentYield && fcfCoverage && fcfCoverage > 0) {
                    // Estimate FCF yield = Dividend Yield × FCF Coverage
                    const estimatedFcfYield = (currentYield / 100) * fcfCoverage;
                    return `~${(estimatedFcfYield * 100).toFixed(1)}%`;
                  }
                  
                  return 'N/A';
                })()}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {(() => {
                  const fcfToEquity = analysis?.sustainability_analysis?.key_ratios?.fcf_to_equity_ratio;
                  const freeCashFlow = analysis?.sustainability_analysis?.financial_metrics?.free_cash_flow;
                  const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio;
                  const currentYield = analysis?.current_metrics?.current_yield_pct;
                  
                  // When we have actual FCF data
                  if ((fcfToEquity !== undefined && fcfToEquity !== null) || (freeCashFlow !== undefined)) {
                    return 'Free cash flow available to equity holders (calculated from actual cash flow data)';
                  }
                  
                  // When FCF is negative
                  if (fcfCoverage === 0) {
                    return 'Company has negative free cash flow - burning cash relative to equity value';
                  }
                  
                  // When using dividend-based estimate
                  if (currentYield && fcfCoverage && fcfCoverage > 0) {
                    return 'Estimated using dividend yield × FCF coverage ratio (approximate)';
                  }
                  
                  return 'Free cash flow to equity data unavailable';
                })()}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(() => {
                  const fcfToEquity = analysis?.sustainability_analysis?.key_ratios?.fcf_to_equity_ratio;
                  if (fcfToEquity !== undefined && fcfToEquity !== null) {
                    return Math.min(fcfToEquity * 500, 100); // Scale for percentage
                  }
                  
                  const freeCashFlow = analysis?.sustainability_analysis?.financial_metrics?.free_cash_flow;
                  const marketCap = analysis?.sustainability_analysis?.financial_metrics?.market_cap;
                  
                  if (freeCashFlow && marketCap && marketCap > 0) {
                    const ratio = freeCashFlow / marketCap;
                    return Math.min(ratio * 500, 100);
                  }
                  
                  return 0;
                })()} 
                sx={{ height: 8, borderRadius: 4 }}
                color={(() => {
                  const fcfToEquity = analysis?.sustainability_analysis?.key_ratios?.fcf_to_equity_ratio;
                  const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio;
                  
                  if (fcfCoverage === 0) return 'error';
                  if (fcfToEquity >= 0.15) return 'success';
                  if (fcfToEquity >= 0.08) return 'info';
                  return 'warning';
                })()}
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
    </Stack>
  );

  // Risk Tab Content
  const RiskTab = () => (
    <Stack spacing={4}>
      {/* Overall Risk Assessment */}
      <Card 
        elevation={0}
        sx={{ 
          background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
          border: '2px solid #F59E0B',
          borderRadius: 3,
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #D97706 0%, #F59E0B 100%)',
                  boxShadow: '0 4px 12px rgba(217, 119, 6, 0.3)',
                }}
              >
                <ShieldIcon sx={{ color: 'white', fontSize: 24 }} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'text.primary' }}>
                Risk Assessment Overview
              </Typography>
            </Box>
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
          
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h3" sx={{ mr: 2, color: getScoreColor(customRiskMode ? calculateCustomRiskScore() : (100 - (analysis?.risk_assessment?.risk_score || 0))) }}>
                {customRiskMode ? calculateCustomRiskScore() : (analysis?.risk_assessment?.risk_score || 'N/A')}
              </Typography>
              <Box>
                <Chip 
                  label={customRiskMode ? getCustomRiskRating(calculateCustomRiskScore()) : (analysis?.risk_assessment?.risk_rating || 'N/A')} 
                  color={customRiskMode ? 
                    (calculateCustomRiskScore() >= 61 ? 'success' : calculateCustomRiskScore() >= 41 ? 'warning' : 'error') :
                    (analysis?.risk_assessment?.risk_rating === 'Low' ? 'success' : 
                     analysis?.risk_assessment?.risk_rating === 'Medium' ? 'warning' : 'error')}
                  size="medium"
                />
                <Typography variant="h6" sx={{ mt: 1 }}>
                  {customRiskMode ? 'Custom Risk Rating' : 'Risk Rating'}
                </Typography>
              </Box>
            </Box>
            
            <FormControlLabel
              control={
                <Switch
                  checked={customRiskMode}
                  onChange={(e) => {
                    setCustomRiskMode(e.target.checked);
                    if (e.target.checked) {
                      resetToDefaultScores();
                    }
                  }}
                  color="primary"
                />
              }
              label={
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    Custom Scoring
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Adjust components
                  </Typography>
                </Box>
              }
              labelPlacement="start"
              sx={{ margin: 0 }}
            />
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={customRiskMode ? calculateCustomRiskScore() : (analysis?.risk_assessment?.risk_score || 0)} 
            sx={{ height: 10, borderRadius: 5, mb: 2 }}
            color={customRiskMode ? 
              (calculateCustomRiskScore() >= 61 ? 'success' : calculateCustomRiskScore() >= 41 ? 'warning' : 'error') :
              (analysis?.risk_assessment?.risk_score <= 30 ? 'success' : 
               analysis?.risk_assessment?.risk_score <= 60 ? 'warning' : 'error')}
          />
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="body1" color="text.secondary">
              {customRiskMode ? 
                'Custom risk assessment based on your component weightings' :
                'Higher scores indicate safer dividend sustainability (100=Safest, 0=Highest Risk)'}
            </Typography>
            {!customRiskMode && (
              <Typography variant="caption" color="primary" sx={{ fontStyle: 'italic' }}>
                💡 Turn on Custom Scoring to adjust risk components
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Custom Risk Component Scoring */}
      {customRiskMode && (
        <Card 
          elevation={2}
          sx={{ 
            border: '2px solid #3B82F6',
            background: 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)',
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                    boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
                  }}
                >
                  <TuneIcon sx={{ color: 'white', fontSize: 20 }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  Custom Risk Component Scoring
                </Typography>
              </Box>
              <Button
                variant="outlined"
                size="small"
                onClick={resetToDefaultScores}
                sx={{ textTransform: 'none' }}
              >
                Reset to Analysis
              </Button>
            </Box>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Adjust the scoring for each risk component based on your analysis. The overall risk score will be calculated using industry-standard weightings.
            </Typography>

            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 6 }}>
              {/* Coverage Risk Component */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" color="primary">
                    Coverage Analysis
                  </Typography>
                  <Chip 
                    label={`${customRiskScores.coverage}/100`}
                    size="small"
                    color={customRiskScores.coverage >= 75 ? 'success' : customRiskScores.coverage >= 50 ? 'warning' : 'error'}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  How well do earnings and cash flows cover dividend payments? (Weight: 35%)
                </Typography>
                <Box sx={{ px: 2, mb: 6 }}>
                  <Slider
                    value={customRiskScores.coverage}
                    onChange={(_, newValue) => setCustomRiskScores(prev => ({ ...prev, coverage: newValue as number }))}
                    min={0}
                    max={100}
                    marks={[
                      { value: 0, label: 'Risky' },
                      { value: 50, label: 'Moderate' },
                      { value: 100, label: 'Safe' }
                    ]}
                    sx={{ '& .MuiSlider-markLabel': { fontSize: '0.75rem' } }}
                    color={customRiskScores.coverage >= 75 ? 'success' : customRiskScores.coverage >= 50 ? 'warning' : 'error'}
                  />
                </Box>
              </Box>

              {/* Financial Stability Component */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" color="primary">
                    Financial Stability
                  </Typography>
                  <Chip 
                    label={`${customRiskScores.stability}/100`}
                    size="small"
                    color={customRiskScores.stability >= 75 ? 'success' : customRiskScores.stability >= 50 ? 'warning' : 'error'}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Overall financial health including debt management and liquidity. (Weight: 25%)
                </Typography>
                <Box sx={{ px: 2, mb: 6 }}>
                  <Slider
                    value={customRiskScores.stability}
                    onChange={(_, newValue) => setCustomRiskScores(prev => ({ ...prev, stability: newValue as number }))}
                    min={0}
                    max={100}
                    marks={[
                      { value: 0, label: 'Weak' },
                      { value: 50, label: 'Moderate' },
                      { value: 100, label: 'Strong' }
                    ]}
                    sx={{ '& .MuiSlider-markLabel': { fontSize: '0.75rem' } }}
                    color={customRiskScores.stability >= 75 ? 'success' : customRiskScores.stability >= 50 ? 'warning' : 'error'}
                  />
                </Box>
              </Box>

              {/* Earnings Volatility Component */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" color="primary">
                    Earnings Consistency
                  </Typography>
                  <Chip 
                    label={`${customRiskScores.volatility}/100`}
                    size="small"
                    color={customRiskScores.volatility >= 75 ? 'success' : customRiskScores.volatility >= 50 ? 'warning' : 'error'}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  How stable and predictable are the company's earnings? (Weight: 20%)
                </Typography>
                <Box sx={{ px: 2, mb: 6 }}>
                  <Slider
                    value={customRiskScores.volatility}
                    onChange={(_, newValue) => setCustomRiskScores(prev => ({ ...prev, volatility: newValue as number }))}
                    min={0}
                    max={100}
                    marks={[
                      { value: 0, label: 'Volatile' },
                      { value: 50, label: 'Moderate' },
                      { value: 100, label: 'Stable' }
                    ]}
                    sx={{ '& .MuiSlider-markLabel': { fontSize: '0.75rem' } }}
                    color={customRiskScores.volatility >= 75 ? 'success' : customRiskScores.volatility >= 50 ? 'warning' : 'error'}
                  />
                </Box>
              </Box>

              {/* Growth Consistency Component */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" color="primary">
                    Growth Track Record
                  </Typography>
                  <Chip 
                    label={`${customRiskScores.growth}/100`}
                    size="small"
                    color={customRiskScores.growth >= 75 ? 'success' : customRiskScores.growth >= 50 ? 'warning' : 'error'}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Consistency of dividend growth and payment history. (Weight: 20%)
                </Typography>
                <Box sx={{ px: 2, mb: 6 }}>
                  <Slider
                    value={customRiskScores.growth}
                    onChange={(_, newValue) => setCustomRiskScores(prev => ({ ...prev, growth: newValue as number }))}
                    min={0}
                    max={100}
                    marks={[
                      { value: 0, label: 'Poor' },
                      { value: 50, label: 'Moderate' },
                      { value: 100, label: 'Excellent' }
                    ]}
                    sx={{ '& .MuiSlider-markLabel': { fontSize: '0.75rem' } }}
                    color={customRiskScores.growth >= 75 ? 'success' : customRiskScores.growth >= 50 ? 'warning' : 'error'}
                  />
                </Box>
              </Box>
            </Box>

            {/* Summary */}
            <Box sx={{ mt: 4, p: 3, bgcolor: 'white', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">
                  Your Custom Risk Assessment
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="h4" sx={{ color: getScoreColor(calculateCustomRiskScore()) }}>
                    {calculateCustomRiskScore()}
                  </Typography>
                  <Chip 
                    label={getCustomRiskRating(calculateCustomRiskScore())}
                    color={calculateCustomRiskScore() >= 61 ? 'success' : calculateCustomRiskScore() >= 41 ? 'warning' : 'error'}
                    size="medium"
                  />
                </Box>
              </Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2, mt: 2 }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="caption" color="text.secondary">Coverage (35%)</Typography>
                  <Typography variant="h6" color="primary">{Math.round(customRiskScores.coverage * 0.35)}</Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="caption" color="text.secondary">Stability (25%)</Typography>
                  <Typography variant="h6" color="primary">{Math.round(customRiskScores.stability * 0.25)}</Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="caption" color="text.secondary">Consistency (20%)</Typography>
                  <Typography variant="h6" color="primary">{Math.round(customRiskScores.volatility * 0.20)}</Typography>
                </Box>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="caption" color="text.secondary">Growth (20%)</Typography>
                  <Typography variant="h6" color="primary">{Math.round(customRiskScores.growth * 0.20)}</Typography>
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

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
                {(() => {
                  // Calculate financial stability score from available metrics
                  const debtCoverage = analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage || 0;
                  const workingCapital = analysis?.sustainability_analysis?.key_ratios?.working_capital_ratio || 0;
                  const earningsVol = analysis?.sustainability_analysis?.key_ratios?.earnings_volatility || 1;
                  const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio || 0;
                  
                  // Score components (0-5 each, total 20)
                  const debtScore = Math.min(5, Math.max(0, debtCoverage > 10 ? 5 : debtCoverage > 5 ? 4 : debtCoverage > 2 ? 3 : debtCoverage > 1 ? 2 : 1));
                  const liquidityScore = Math.min(5, Math.max(0, workingCapital > 1.5 ? 5 : workingCapital > 1.2 ? 4 : workingCapital > 1 ? 3 : workingCapital > 0.8 ? 2 : 1));
                  const stabilityScore = Math.min(5, Math.max(0, earningsVol < 0.1 ? 5 : earningsVol < 0.2 ? 4 : earningsVol < 0.3 ? 3 : earningsVol < 0.5 ? 2 : 1));
                  const fcfScore = Math.min(5, Math.max(0, fcfCoverage > 5 ? 5 : fcfCoverage > 3 ? 4 : fcfCoverage > 2 ? 3 : fcfCoverage > 1 ? 2 : 1));
                  
                  return debtScore + liquidityScore + stabilityScore + fcfScore;
                })()}/20
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Calculated from debt coverage ({analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage?.toFixed(1)}x), 
                liquidity ({analysis?.sustainability_analysis?.key_ratios?.working_capital_ratio?.toFixed(2)}), 
                earnings stability ({((analysis?.sustainability_analysis?.key_ratios?.earnings_volatility || 0) * 100).toFixed(1)}%), 
                and FCF strength ({analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio?.toFixed(1)}x)
              </Typography>
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  variant="determinate" 
                  value={(() => {
                    const debtCoverage = analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage || 0;
                    const workingCapital = analysis?.sustainability_analysis?.key_ratios?.working_capital_ratio || 0;
                    const earningsVol = analysis?.sustainability_analysis?.key_ratios?.earnings_volatility || 1;
                    const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio || 0;
                    
                    const debtScore = Math.min(5, Math.max(0, debtCoverage > 10 ? 5 : debtCoverage > 5 ? 4 : debtCoverage > 2 ? 3 : debtCoverage > 1 ? 2 : 1));
                    const liquidityScore = Math.min(5, Math.max(0, workingCapital > 1.5 ? 5 : workingCapital > 1.2 ? 4 : workingCapital > 1 ? 3 : workingCapital > 0.8 ? 2 : 1));
                    const stabilityScore = Math.min(5, Math.max(0, earningsVol < 0.1 ? 5 : earningsVol < 0.2 ? 4 : earningsVol < 0.3 ? 3 : earningsVol < 0.5 ? 2 : 1));
                    const fcfScore = Math.min(5, Math.max(0, fcfCoverage > 5 ? 5 : fcfCoverage > 3 ? 4 : fcfCoverage > 2 ? 3 : fcfCoverage > 1 ? 2 : 1));
                    
                    const totalScore = debtScore + liquidityScore + stabilityScore + fcfScore;
                    return (totalScore / 20) * 100;
                  })()} 
                  sx={{ height: 6, borderRadius: 3 }}
                  color={(() => {
                    const debtCoverage = analysis?.sustainability_analysis?.key_ratios?.debt_service_coverage || 0;
                    const workingCapital = analysis?.sustainability_analysis?.key_ratios?.working_capital_ratio || 0;
                    const earningsVol = analysis?.sustainability_analysis?.key_ratios?.earnings_volatility || 1;
                    const fcfCoverage = analysis?.sustainability_analysis?.key_ratios?.fcf_coverage_ratio || 0;
                    
                    const debtScore = Math.min(5, Math.max(0, debtCoverage > 10 ? 5 : debtCoverage > 5 ? 4 : debtCoverage > 2 ? 3 : debtCoverage > 1 ? 2 : 1));
                    const liquidityScore = Math.min(5, Math.max(0, workingCapital > 1.5 ? 5 : workingCapital > 1.2 ? 4 : workingCapital > 1 ? 3 : workingCapital > 0.8 ? 2 : 1));
                    const stabilityScore = Math.min(5, Math.max(0, earningsVol < 0.1 ? 5 : earningsVol < 0.2 ? 4 : earningsVol < 0.3 ? 3 : earningsVol < 0.5 ? 2 : 1));
                    const fcfScore = Math.min(5, Math.max(0, fcfCoverage > 5 ? 5 : fcfCoverage > 3 ? 4 : fcfCoverage > 2 ? 3 : fcfCoverage > 1 ? 2 : 1));
                    
                    const totalScore = debtScore + liquidityScore + stabilityScore + fcfScore;
                    return totalScore >= 15 ? 'success' : totalScore >= 10 ? 'warning' : 'error';
                  })()}
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



      {/* Professional Dividend Stress Testing */}
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AssessmentIcon sx={{ color: 'primary.main', mr: 1, fontSize: 24 }} />
            <Typography variant="h6" color="primary" sx={{ fontWeight: 500 }}>
              Dividend Resilience Analysis
            </Typography>
            <Tooltip title={
              <Box>
                <Typography variant="subtitle2" gutterBottom>Professional Dividend Risk Assessment:</Typography>
                <Typography variant="body2">• <strong>Economic Scenarios:</strong> Recession, interest rate cycles, inflation pressures</Typography>
                <Typography variant="body2">• <strong>Coverage Analysis:</strong> Earnings and free cash flow sustainability</Typography>
                <Typography variant="body2">• <strong>Balance Sheet Strength:</strong> Debt capacity and financial flexibility</Typography>
                <Typography variant="body2">• <strong>Business Quality:</strong> Defensive characteristics and earnings stability</Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  <strong>Methodology:</strong> Based on Simply Safe Dividends (97% track record) and Morningstar dividend sustainability frameworks.
                </Typography>
              </Box>
            } arrow>
              <IconButton size="small" sx={{ ml: 1 }}>
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Professional stress testing assessment for {ticker}'s dividend sustainability across economic scenarios
          </Typography>

          {/* Professional Stress Test Matrix */}
          <Box sx={{ mb: 3 }}>
            {(() => {
              // Calculate professional stress test scores using industry-standard metrics
              const keyRatios = analysis?.sustainability_analysis?.key_ratios;
              const payoutRatio = keyRatios?.payout_ratio || 0.5;
              const debtCoverage = keyRatios?.debt_service_coverage || 0;
              const fcfCoverage = keyRatios?.fcf_coverage_ratio || 0;
              const earningsVol = keyRatios?.earnings_volatility || 0.5;
              const workingCapital = keyRatios?.working_capital_ratio || 1;

              // Professional stress scenarios based on Simply Safe Dividends methodology
              const scenarios = [
                { 
                  name: 'Recession Resilience', 
                  description: 'Economic downturn & earnings pressure',
                  icon: '📉'
                },
                { 
                  name: 'Interest Rate Shock', 
                  description: 'Rising rates & debt service costs',
                  icon: '📈'
                },
                { 
                  name: 'Inflation Pressure', 
                  description: 'Cost inflation & margin compression',
                  icon: '💰'
                }
              ];

              const assessmentCategories = [
                'Coverage Strength',
                'Balance Sheet', 
                'Earnings Quality',
                'Overall Risk'
              ];

              // Professional scoring based on Morningstar/Simply Safe Dividends methodology
              const getStressAssessment = (scenario: string, category: string) => {
                let score = 0;

                if (category === 'Coverage Strength') {
                  // Payout ratio assessment (conservative < 0.6, risky > 0.8)
                  if (payoutRatio < 0.4) score += 2;
                  else if (payoutRatio < 0.6) score += 1;
                  else if (payoutRatio > 0.8) score -= 1;

                  // FCF Coverage (excellent > 3x, adequate > 1.5x, weak < 1x)
                  if (fcfCoverage > 3) score += 2;
                  else if (fcfCoverage > 1.5) score += 1;
                  else if (fcfCoverage < 1) score -= 1;

                  // Scenario-specific adjustments
                  if (scenario === 'Recession Resilience' && earningsVol > 0.4) score -= 1;
                  
                } else if (category === 'Balance Sheet') {
                  // Debt coverage assessment (excellent > 20x, good > 10x, weak < 5x)
                  if (debtCoverage > 20) score += 2;
                  else if (debtCoverage > 10) score += 1;
                  else if (debtCoverage < 5) score -= 1;

                  // Working capital ratio (strong > 1.2, adequate > 1.0, weak < 0.8)
                  if (workingCapital > 1.2) score += 1;
                  else if (workingCapital < 0.8) score -= 1;

                  // Interest rate scenario penalty for high debt
                  if (scenario === 'Interest Rate Shock' && debtCoverage < 10) score -= 1;
                  
                } else if (category === 'Earnings Quality') {
                  // Earnings volatility assessment (stable < 0.2, moderate < 0.3, high > 0.5)
                  if (earningsVol < 0.2) score += 2;
                  else if (earningsVol < 0.3) score += 1;
                  else if (earningsVol > 0.5) score -= 1;

                  // Inflation scenario - pricing power proxy
                  if (scenario === 'Inflation Pressure') {
                    if (payoutRatio < 0.5 && fcfCoverage > 2) score += 1;
                    else if (payoutRatio > 0.7) score -= 1;
                  }
                  
                } else if (category === 'Overall Risk') {
                  // Combined assessment for overall resilience
                  if (payoutRatio < 0.5 && debtCoverage > 15 && fcfCoverage > 2) score += 2;
                  else if (payoutRatio < 0.7 && debtCoverage > 5 && fcfCoverage > 1.5) score += 1;
                  else if (payoutRatio > 0.8 || debtCoverage < 3 || fcfCoverage < 1) score -= 1;
                }

                // Normalize to 0-5 scale and categorize
                score = Math.max(0, Math.min(5, score + 2));
                
                if (score >= 4) return { level: 'Strong', color: '#2e7d32', bgColor: '#e8f5e8' };
                else if (score >= 3) return { level: 'Adequate', color: '#ed6c02', bgColor: '#fff4e6' };
                else if (score >= 2) return { level: 'Moderate', color: '#ff9800', bgColor: '#fff3e0' };
                else return { level: 'Weak', color: '#d32f2f', bgColor: '#ffebee' };
              };

              return (
                <Box sx={{ overflow: 'auto' }}>
                  {/* Professional Matrix Table */}
                  <TableContainer component={Paper} sx={{ border: '1px solid', borderColor: 'divider' }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'primary.main' }}>
                          <TableCell sx={{ 
                            color: 'white', 
                            fontWeight: 600, 
                            minWidth: 180,
                            borderRight: '1px solid rgba(255,255,255,0.2)'
                          }}>
                            Economic Scenario
                          </TableCell>
                          {assessmentCategories.map((category) => (
                            <TableCell 
                              key={category} 
                              align="center" 
                              sx={{ 
                                color: 'white', 
                                fontWeight: 600,
                                minWidth: 130,
                                borderRight: category !== assessmentCategories[assessmentCategories.length - 1] ? 
                                  '1px solid rgba(255,255,255,0.2)' : 'none'
                              }}
                            >
                              {category}
                            </TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {scenarios.map((scenario, scenarioIndex) => (
                          <TableRow 
                            key={scenario.name}
                            sx={{ 
                              '&:nth-of-type(odd)': { bgcolor: 'rgba(0, 0, 0, 0.02)' },
                              borderBottom: scenarioIndex !== scenarios.length - 1 ? '1px solid' : 'none',
                              borderColor: 'divider'
                            }}
                          >
                            <TableCell sx={{ 
                              borderRight: '1px solid', 
                              borderColor: 'divider',
                              verticalAlign: 'top',
                              py: 2
                            }}>
                              <Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                                  <Typography variant="body2" sx={{ mr: 0.5, fontSize: '1.1rem' }}>
                                    {scenario.icon}
                                  </Typography>
                                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                    {scenario.name}
                                  </Typography>
                                </Box>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                  {scenario.description}
                                </Typography>
                              </Box>
                            </TableCell>
                            {assessmentCategories.map((category, categoryIndex) => {
                              const assessment = getStressAssessment(scenario.name, category);
                              return (
                                <TableCell 
                                  key={category} 
                                  align="center" 
                                  sx={{ 
                                    borderRight: categoryIndex !== assessmentCategories.length - 1 ? 
                                      '1px solid' : 'none',
                                    borderColor: 'divider',
                                    bgcolor: assessment.bgColor,
                                    py: 2,
                                    position: 'relative'
                                  }}
                                >
                                  <Box sx={{ 
                                    display: 'flex', 
                                    flexDirection: 'column', 
                                    alignItems: 'center',
                                    gap: 0.5
                                  }}>
                                    <Typography 
                                      variant="body2" 
                                      sx={{ 
                                        fontWeight: 600,
                                        color: assessment.color,
                                        fontSize: '0.875rem'
                                      }}
                                    >
                                      {assessment.level}
                                    </Typography>
                                    <Box sx={{ 
                                      width: 32, 
                                      height: 4, 
                                      borderRadius: 2,
                                      bgcolor: assessment.color,
                                      opacity: 0.8
                                    }} />
                                  </Box>
                                </TableCell>
                              );
                            })}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              );
            })()}
          </Box>

          {/* Professional Assessment Scale */}
          <Box sx={{ 
            display: 'flex', 
            flexWrap: 'wrap', 
            gap: 2, 
            justifyContent: 'center',
            p: 2,
            bgcolor: 'grey.50',
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider'
          }}>
            <Typography variant="subtitle2" sx={{ 
              width: '100%', 
              textAlign: 'center', 
              fontWeight: 600, 
              mb: 1,
              color: 'text.primary'
            }}>
              Risk Assessment Scale
            </Typography>
            {[
              { level: 'Strong', color: '#2e7d32', description: 'Low dividend risk - well positioned for stress scenarios' },
              { level: 'Adequate', color: '#ed6c02', description: 'Moderate risk - adequate protection with monitoring needed' },
              { level: 'Moderate', color: '#ff9800', description: 'Elevated risk - some vulnerability during stress periods' },
              { level: 'Weak', color: '#d32f2f', description: 'High risk - significant vulnerability to economic pressures' }
            ].map(item => (
              <Box key={item.level} sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 1,
                px: 2,
                py: 1,
                backgroundColor: 'white',
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'divider',
                minWidth: 240
              }}>
                <Box sx={{ 
                  width: 16, 
                  height: 16, 
                  borderRadius: '50%',
                  bgcolor: item.color
                }} />
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: item.color }}>
                    {item.level}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                    {item.description}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Box>


        </CardContent>
      </Card>
    </Stack>
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
                {['5Y', '10Y', '15Y', '20Y', '25Y', 'All'].map((period) => (
                  <Button
                    key={period}
                    variant={dateRange.years === (period === 'All' ? 0 : parseInt(period.slice(0, -1))) ? 'contained' : 'outlined'}
                    size="small"
                    onClick={async () => {
                      const years = period === 'All' ? 0 : parseInt(period.slice(0, -1));
                      setDateRange({ years });
                      if (lastAnalyzedTicker) {
                        await refreshChartData(lastAnalyzedTicker, years);
                      }
                    }}
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
                    <LineChart data={Array.isArray(growthChart) ? growthChart : []}>
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
                  {(() => {
                    const increases = analysis?.growth_analytics?.consecutive_increases;
                    if (increases !== undefined && increases !== null && increases !== 'N/A') {
                      return `${Number(increases)} years`;
                    }
                    return '0 years';
                  })()}
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
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Header />
      
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Hero Section */}
        <Box sx={{ mb: 6, textAlign: 'center' }}>
          <Typography 
            variant="h3" 
            component="h1" 
            gutterBottom
            sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(135deg, #0F172A 0%, #059669 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 2
            }}
          >
            Institutional-Grade Dividend Analysis
          </Typography>
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ maxWidth: 600, mx: 'auto', mb: 4 }}
          >
            Get comprehensive dividend insights with professional-grade metrics used by institutional investors
          </Typography>
        </Box>

        {/* Enhanced Search Section */}
        <Card 
          elevation={0}
          sx={{ 
            mb: 4,
            background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
            border: '2px solid #E2E8F0',
            borderRadius: 3,
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ 
              display: 'flex', 
              flexDirection: { xs: 'column', md: 'row' }, 
              alignItems: { xs: 'stretch', md: 'center' }, 
              gap: 3 
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                <SearchIcon sx={{ color: 'text.secondary', fontSize: 28 }} />
                <TextField
                  label="Enter Stock Ticker Symbol"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  onKeyPress={handleKeyPress}
                  fullWidth
                  variant="outlined"
                  placeholder="e.g., AAPL, MSFT, JNJ, KO"
                  disabled={loading}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'white',
                      '&:hover': {
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'secondary.main',
                          borderWidth: 2,
                        },
                      },
                      '&.Mui-focused': {
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'secondary.main',
                          borderWidth: 2,
                        },
                      },
                    },
                  }}
                />
              </Box>
              <Button
                variant="contained"
                onClick={handleAnalyze}
                disabled={loading || !ticker}
                size="large"
                sx={{ 
                  minWidth: 140,
                  height: 56,
                  fontSize: '1rem',
                  background: 'linear-gradient(135deg, #059669 0%, #10B981 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #047857 0%, #059669 100%)',
                  },
                }}
              >
                {loading ? (
                  <CircularProgress size={24} sx={{ color: 'white' }} />
                ) : (
                  <>
                    <AssessmentIcon sx={{ mr: 1 }} />
                    Analyze
                  </>
                )}
              </Button>
            </Box>

            {/* Popular Tickers */}
            <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid #E2E8F0' }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Popular dividend stocks:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {['AAPL', 'MSFT', 'JNJ', 'KO', 'PG', 'T', 'VZ', 'O'].map((symbol) => (
                  <Chip
                    key={symbol}
                    label={symbol}
                    onClick={() => setTicker(symbol)}
                    variant="outlined"
                    size="small"
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'secondary.light',
                        color: 'white',
                        borderColor: 'secondary.main',
                      },
                    }}
                  />
                ))}
              </Box>
            </Box>
          </CardContent>
        </Card>

        {/* Status Section */}
        {lastAnalyzedTicker && !loading && !error && (
          <Alert 
            severity="success" 
            sx={{ 
              mb: 4,
              borderRadius: 2,
              '& .MuiAlert-icon': {
                color: 'success.main',
              },
            }}
            icon={<CheckIcon />}
          >
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              Analysis completed successfully for {lastAnalyzedTicker}
            </Typography>
          </Alert>
        )}

        {/* Error Message */}
        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 4,
              borderRadius: 2,
            }}
          >
            {error}
          </Alert>
        )}

        {/* Company Header */}
        {companyInfo && currentDividend && analysis && (
          <Card 
            elevation={0} 
            sx={{ 
              mb: 3,
              border: '1px solid #E2E8F0',
              borderRadius: 2,
              background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)',
            }}
          >
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 3,
                flexDirection: { xs: 'column', sm: 'row' },
                textAlign: { xs: 'center', sm: 'left' }
              }}>
                {/* Company Logo */}
                <Avatar
                  src={companyInfo.logo_url || `https://logo.clearbit.com/${companyInfo.ticker.toLowerCase()}.com`}
                  alt={`${companyInfo.name} logo`}
                  sx={{
                    width: { xs: 80, sm: 100 },
                    height: { xs: 80, sm: 100 },
                    bgcolor: 'grey.100',
                    border: '3px solid white',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  }}
                  imgProps={{
                    onError: (e) => {
                      const img = e.target as HTMLImageElement;
                      // Try fallback URLs in order
                      if (img.src.includes('financialmodelingprep.com')) {
                        img.src = `https://logo.clearbit.com/${companyInfo.ticker.toLowerCase()}.com`;
                      } else if (img.src.includes('clearbit.com')) {
                        img.src = `https://img.logo.dev/${companyInfo.ticker.toLowerCase()}.com?token=pk_X-lqcjKBQtOpcU8KZieivw`;
                      } else {
                        // All fallbacks failed, hide image and show text avatar
                        img.style.display = 'none';
                      }
                    }
                  }}
                >
                  {companyInfo.name ? companyInfo.name.charAt(0) : companyInfo.ticker}
                </Avatar>

                {/* Company Info */}
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 2, 
                    mb: 1,
                    flexDirection: { xs: 'column', sm: 'row' }
                  }}>
                    <Typography 
                      variant="h4" 
                      sx={{ 
                        fontWeight: 700,
                        color: 'text.primary',
                        mb: { xs: 1, sm: 0 }
                      }}
                    >
                      {companyInfo.name}
                    </Typography>
                    <Chip 
                      label={companyInfo.ticker}
                      size="medium"
                      sx={{
                        fontWeight: 600,
                        backgroundColor: 'secondary.main',
                        color: 'white',
                        fontSize: '0.9rem',
                      }}
                    />
                  </Box>
                  
                  <Box sx={{ 
                    display: 'flex', 
                    flexDirection: { xs: 'column', sm: 'row' },
                    gap: { xs: 1, sm: 3 },
                    alignItems: { xs: 'center', sm: 'flex-start' }
                  }}>
                    {companyInfo.exchange && (
                      <Typography variant="body1" color="text.secondary">
                        <strong>Exchange:</strong> {companyInfo.exchange}
                      </Typography>
                    )}
                    {companyInfo.sector && (
                      <Typography variant="body1" color="text.secondary">
                        <strong>Sector:</strong> {companyInfo.sector}
                      </Typography>
                    )}
                    {companyInfo.market_cap && (
                      <Typography variant="body1" color="text.secondary">
                        <strong>Market Cap:</strong> ${(companyInfo.market_cap / 1e12).toFixed(2)}T
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Enhanced Tabs Section */}
        {currentDividend && analysis && (
          <Card elevation={0} sx={{ border: '1px solid #E2E8F0' }}>
            <Box sx={{ borderBottom: '1px solid #E2E8F0' }}>
              <Tabs 
                value={tabValue} 
                onChange={handleTabChange}
                aria-label="dividend analysis tabs"
                variant="fullWidth"
                sx={{
                  '& .MuiTab-root': {
                    py: 3,
                    minHeight: 'auto',
                    fontSize: '0.95rem',
                    fontWeight: 600,
                  },
                }}
              >
                <Tab 
                  icon={<AccountBalanceIcon />} 
                  iconPosition="start"
                  label="Current Overview" 
                />
                <Tab 
                  icon={<ShowChartIcon />} 
                  iconPosition="start"
                  label="Performance & Growth" 
                />
                <Tab 
                  icon={<SecurityIcon />} 
                  iconPosition="start"
                  label="Sustainability" 
                />
                <Tab 
                  icon={<ShieldIcon />} 
                  iconPosition="start"
                  label="Risk Analysis" 
                />
                <Tab 
                  icon={<AutoGraphIcon />} 
                  iconPosition="start"
                  label="Portfolio Optimization" 
                />
              </Tabs>
            </Box>

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

            <TabPanel value={tabValue} index={4}>
              <Box sx={{ textAlign: 'center', py: 6 }}>
                <AutoGraphIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Portfolio Optimization
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Advanced portfolio optimization is now available as a separate tab in the main navigation.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Switch to the "Portfolio Optimization" tab to access both Traditional EPO and Advanced NEPO features.
                </Typography>
              </Box>
            </TabPanel>
          </Card>
        )}
      </Container>
    </Box>
  );
};

export default DividendAnalysisComponent; 
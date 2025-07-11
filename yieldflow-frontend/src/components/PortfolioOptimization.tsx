import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Stack,
  Divider,
  InputAdornment,
  Fade,
  Collapse,
  CircularProgress,
  Avatar,
  Grow,
  Tabs,
  Tab,
} from '@mui/material';

import {
  AutoGraph as AutoGraphIcon,
  Tune as TuneIcon,
  Timeline as TimelineIcon,
  Newspaper as NewspaperIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  ShowChart as ShowChartIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Psychology as PsychologyIcon,
  Equalizer as EqualizerIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import { Pie, Scatter, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';
import { portfolioService } from '../services/portfolioService';
import { TAB_LABELS } from './PortfolioOptimization.constants';
import type { CorrelationMatrix } from '../services/portfolioService';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  BarElement
);

enum OptimizationObjectiveLocal {
  SHARPE_RATIO = 'sharpe_ratio',
  DIVIDEND_YIELD = 'dividend_yield',
  BALANCED = 'balanced'
}

interface OptimizationResults {
  optimized_weights: Record<string, number>;
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  expected_dividend_yield: number;
}

interface NEPOResults {
  success: boolean;
  methodology: string;
  optimization_results: {
    optimized_weights: Record<string, number>;
    position_sizes: Record<string, any>;
    expected_return: number;
    annual_expected_return_pct: number;
    volatility: number;
    annual_volatility_pct: number;
    sharpe_ratio: number;
    investment_amount: number;
    time_horizon: string;
  };
  traditional_epo_baseline: OptimizationResults;
  news_intelligence: {
    enabled: boolean;
    gemini_powered: boolean;
    news_analyses: Record<string, any>;
    investment_thesis: string;
    geopolitical_risk_level: number;
  };
  performance_metrics: {
    expected_dividend_yield: number;
    improvement_over_epo: Record<string, number>;
    combination_weight: number;
  };
  metadata: {
    optimization_timestamp: string;
    analysis_features: string[];
    data_sources: string[];
    risk_considerations: string[];
  };
}

interface EfficientFrontier {
  frontier_points: {
    volatility: number;
    expected_return: number;
  }[];
}

const PortfolioOptimization: React.FC = () => {
  const [tickers, setTickers] = useState(['AAPL', 'GOOGL', 'KO', 'PG']);
  const [newTicker, setNewTicker] = useState('');
  const [objective, setObjective] = useState(OptimizationObjectiveLocal.SHARPE_RATIO);
  const [maxWeight, setMaxWeight] = useState(0.5);
  const [investmentAmount, setInvestmentAmount] = useState(100000);
  const [timeHorizon, setTimeHorizon] = useState('medium');
  const [useNewsEnhancement, setUseNewsEnhancement] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<OptimizationResults | null>(null);
  const [traditionalResults, setTraditionalResults] = useState<OptimizationResults | null>(null);
  const [nepoResults, setNepoResults] = useState<NEPOResults | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [efficientFrontier, setEfficientFrontier] = useState<EfficientFrontier | null>(null);
  const [correlationMatrix, setCorrelationMatrix] = useState<CorrelationMatrix | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => setActiveTab(newValue);

  const tabLabels = TAB_LABELS;

  const addTicker = () => {
    if (newTicker.trim() && !tickers.includes(newTicker.trim().toUpperCase())) {
      setTickers([...tickers, newTicker.trim().toUpperCase()]);
      setNewTicker('');
    }
  };

  const removeTicker = (index: number) => {
    setTickers(tickers.filter((_, i) => i !== index));
  };

  const handleOptimize = async () => {
    const validTickers = tickers.filter(t => t.trim());
    if (validTickers.length < 2) {
      alert('Please add at least 2 tickers for optimization');
      return;
    }

    setLoading(true);
    setShowResults(false);
    
    try {
      if (useNewsEnhancement) {
        // Run Advanced Optimization (NEPO)
        const nepoData = await portfolioService.optimizeNewsEnhancedPortfolio({
          tickers: validTickers,
          objective: objective as any,
          max_weight: maxWeight
        }, {
          investment_amount: investmentAmount,
          time_horizon: timeHorizon as 'short' | 'medium' | 'long',
          include_news_analysis: true
        });
        
        setNepoResults(nepoData as any);
        
        // Map the NEPO results to the display format
        setResults({
          optimized_weights: (nepoData as any).optimization_results?.optimized_weights || {},
          expected_return: (nepoData as any).optimization_results?.expected_return || 0,
          volatility: (nepoData as any).optimization_results?.volatility || 0,
          sharpe_ratio: (nepoData as any).optimization_results?.sharpe_ratio || 0,
          expected_dividend_yield: (nepoData as any).performance_metrics?.expected_dividend_yield || 0
        });
        
        // Set traditional results for comparison if available
        if ((nepoData as any).traditional_epo_baseline && Object.keys((nepoData as any).traditional_epo_baseline).length > 0) {
          setTraditionalResults((nepoData as any).traditional_epo_baseline);
        } else {
          // Run traditional optimization for comparison
          const traditionalData = await portfolioService.optimizePortfolio({
            tickers: validTickers,
            objective: objective as any,
            max_weight: maxWeight
          });
          setTraditionalResults({
            optimized_weights: traditionalData.weights,
            expected_return: traditionalData.expected_return,
            volatility: traditionalData.volatility,
            sharpe_ratio: traditionalData.sharpe_ratio,
            expected_dividend_yield: traditionalData.expected_dividend_yield
          });
        }
      } else {
        // Run Traditional Optimization (EPO only)
        const traditionalData = await portfolioService.optimizePortfolio({
          tickers: validTickers,
          objective: objective as any,
          max_weight: maxWeight
        });
        
        setTraditionalResults({
          optimized_weights: traditionalData.weights,
          expected_return: traditionalData.expected_return,
          volatility: traditionalData.volatility,
          sharpe_ratio: traditionalData.sharpe_ratio,
          expected_dividend_yield: traditionalData.expected_dividend_yield
        });
        setResults({
          optimized_weights: traditionalData.weights,
          expected_return: traditionalData.expected_return,
          volatility: traditionalData.volatility,
          sharpe_ratio: traditionalData.sharpe_ratio,
          expected_dividend_yield: traditionalData.expected_dividend_yield
        });
        setNepoResults(null);
      }
      
      setShowResults(true);

      // fetch efficient frontier
      const frontier = await portfolioService.getEfficientFrontier(validTickers, objective as any, 30);
      setEfficientFrontier(frontier);

      // fetch correlation matrix
      try {
        const corr = await portfolioService.getCorrelationMatrix(validTickers);
        setCorrelationMatrix(corr);
      } catch (err) {
        console.error('Failed to load correlation matrix', err);
      }
    } catch (error) {
      console.error('Optimization failed:', error);
      alert('Optimization failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatCurrency = (value: number) => `$${value.toLocaleString()}`;

  // Create professional pie chart data for portfolio allocation
  const createPieData = (weights: Record<string, number>) => {
    const labels = Object.keys(weights);
    const data = Object.values(weights).map(w => w * 100);
    const colors = [
      '#0F172A', '#3B82F6', '#10B981', '#F59E0B', '#DC2626',
      '#8B5CF6', '#EC4899', '#14B8A6', '#84CC16', '#64748B'
    ];

    return {
      labels,
      datasets: [{
        data,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 1,
        borderColor: '#FFFFFF',
        hoverBorderWidth: 2,
        hoverBorderColor: '#E2E8F0'
      }]
    };
  };

  // Create performance comparison chart
  const createComparisonData = () => {
    if (!results || !traditionalResults || !useNewsEnhancement) return null;

    return {
      labels: ['Expected Return', 'Volatility', 'Sharpe Ratio'],
      datasets: [
        {
          label: 'Traditional EPO',
          data: [
            traditionalResults.expected_return * 100,
            traditionalResults.volatility * 100,
            traditionalResults.sharpe_ratio
          ],
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: '#3b82f6',
          borderWidth: 2
        },
        {
          label: 'NEPO Enhanced',
          data: [
            results.expected_return * 100,
            results.volatility * 100,
            results.sharpe_ratio
          ],
          backgroundColor: 'rgba(245, 158, 11, 0.5)',
          borderColor: '#f59e0b',
          borderWidth: 2
        }
      ]
    };
  };

  const renderCorrelationMatrix = () => {
    if (!correlationMatrix) {
      return <Typography>Loading correlation matrix...</Typography>;
    }

    const { tickers: corrTickers, matrix } = correlationMatrix;

    const getCellColor = (value: number) => {
      if (value >= 0) {
        const alpha = 0.2 + 0.6 * value; // 0.2 to 0.8
        return `rgba(220,38,38,${alpha})`; // red family
      }
      const alpha = 0.2 + 0.6 * (-value);
      return `rgba(37,99,235,${alpha})`; // blue family
    };

    return (
      <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell></TableCell>
              {corrTickers.map((t) => (
                <TableCell key={t} align="center"><strong>{t}</strong></TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {corrTickers.map((rowTicker, i) => (
              <TableRow key={rowTicker}>
                <TableCell><strong>{rowTicker}</strong></TableCell>
                {corrTickers.map((_, j) => (
                  <TableCell key={`${rowTicker}-${j}`} align="center" sx={{ backgroundColor: getCellColor(matrix[i][j]), color: 'white', fontSize: '0.75rem' }}>
                    {(matrix[i][j] * 100).toFixed(0)}%
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box sx={{ 
      p: 3,
      backgroundColor: '#F8FAFC',
      minHeight: '100vh'
    }}>
      {/* Professional Header */}
      <Box sx={{ mb: 4 }}>
        <Paper 
          elevation={0} 
          sx={{ 
            p: 3,
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: 2,
            borderLeft: `4px solid ${useNewsEnhancement ? '#F59E0B' : '#0F172A'}`
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AutoGraphIcon 
                sx={{ 
                  mr: 2, 
                  fontSize: 32, 
                  color: useNewsEnhancement ? '#F59E0B' : '#0F172A' 
                }} 
              />
              <Box>
                <Typography 
                  variant="h4" 
                  sx={{ 
                    fontWeight: 700,
                    color: '#0F172A',
                    fontSize: '1.75rem',
                    mb: 0.5
                  }}
                >
                  Portfolio Optimization
                </Typography>
                <Typography 
                  variant="body1" 
                  sx={{ 
                    color: '#64748B',
                    fontSize: '0.875rem',
                    fontWeight: 500
                  }}
                >
                  Enhanced quantitative optimization with real-time market intelligence
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ textAlign: 'right' }}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#64748B',
                  fontSize: '0.75rem',
                  fontFamily: 'monospace'
                }}
              >
                {useNewsEnhancement ? 'NEPO Mode' : 'EPO Mode'}
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: useNewsEnhancement ? '#F59E0B' : '#0F172A',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  fontFamily: 'monospace'
                }}
              >
                {useNewsEnhancement ? 'AI Enhanced' : 'Quantitative'}
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '400px 1fr' }, gap: 3 }}>
        {/* Configuration Panel */}
        <Paper 
          elevation={0} 
          sx={{ 
            height: 'fit-content',
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: 2
          }}
        >
          <Box sx={{ 
            p: 2, 
            borderBottom: '1px solid #F1F5F9',
            backgroundColor: '#F8FAFC'
          }}>
            <Typography 
              variant="h6" 
              sx={{ 
                display: 'flex', 
                alignItems: 'center',
                fontSize: '1rem',
                fontWeight: 600,
                color: '#0F172A'
              }}
            >
              <TuneIcon sx={{ mr: 1, fontSize: 20 }} />
              Configuration
            </Typography>
          </Box>
          
          <Box sx={{ p: 3 }}>
            <Stack spacing={3}>
              {/* Optimization Mode Toggle */}
              <Box>
                <Typography 
                  variant="subtitle2" 
                  sx={{ 
                    mb: 2,
                    fontWeight: 600,
                    color: '#334155',
                    fontSize: '0.875rem'
                  }}
                >
                  Optimization Method
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={useNewsEnhancement}
                      onChange={(e) => setUseNewsEnhancement(e.target.checked)}
                      color="primary"
                      size="medium"
                    />
                  }
                  label={
                    <Box>
                      <Typography 
                        variant="body1" 
                        sx={{ 
                          fontWeight: 600, 
                          display: 'flex', 
                          alignItems: 'center',
                          fontSize: '0.875rem',
                          color: '#0F172A'
                        }}
                      >
                        {useNewsEnhancement ? (
                          <>
                            <PsychologyIcon sx={{ mr: 1, color: '#F59E0B', fontSize: 18 }} />
                            Advanced NEPO
                          </>
                        ) : (
                          <>
                            <EqualizerIcon sx={{ mr: 1, color: '#0F172A', fontSize: 18 }} />
                            Traditional EPO
                          </>
                        )}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: '#64748B',
                          fontSize: '0.75rem',
                          mt: 0.5
                        }}
                      >
                        {useNewsEnhancement 
                          ? 'AI-enhanced optimization with market sentiment'
                          : 'Quantitative optimization with correlation analysis'
                        }
                      </Typography>
                    </Box>
                  }
                />
              </Box>

                <Divider sx={{ borderColor: '#F1F5F9' }} />

                {/* Tickers */}
                <Box>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      mb: 2,
                      fontWeight: 600,
                      color: '#334155',
                      fontSize: '0.875rem'
                    }}
                  >
                    Portfolio Instruments
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <TextField
                      size="small"
                      placeholder="Ticker symbol (e.g., AAPL)"
                      value={newTicker}
                      onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                      onKeyPress={(e) => e.key === 'Enter' && addTicker()}
                      sx={{ 
                        flexGrow: 1,
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: '#F8FAFC',
                          fontSize: '0.875rem',
                          fontFamily: 'monospace',
                          '& fieldset': {
                            borderColor: '#E2E8F0'
                          },
                          '&:hover fieldset': {
                            borderColor: '#CBD5E1'
                          }
                        }
                      }}
                    />
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={addTicker}
                      disabled={!newTicker.trim()}
                      sx={{
                        borderColor: '#E2E8F0',
                        color: '#475569',
                        fontSize: '0.75rem',
                        px: 2,
                        '&:hover': {
                          borderColor: '#CBD5E1',
                          backgroundColor: '#F8FAFC'
                        }
                      }}
                    >
                      Add
                    </Button>
                  </Box>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {tickers.filter(t => t).map((ticker, index) => (
                      <Chip
                        key={index}
                        label={ticker}
                        onDelete={() => removeTicker(index)}
                        deleteIcon={<RemoveIcon />}
                        variant="outlined"
                        size="small"
                        sx={{
                          backgroundColor: '#F8FAFC',
                          borderColor: '#E2E8F0',
                          color: '#0F172A',
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          '& .MuiChip-deleteIcon': {
                            color: '#64748B',
                            fontSize: '14px',
                            '&:hover': {
                              color: '#DC2626'
                            }
                          }
                        }}
                      />
                    ))}
                  </Box>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      mt: 1,
                      color: '#64748B',
                      fontSize: '0.6875rem'
                    }}
                  >
                    {tickers.filter(t => t).length} instruments selected • Min: 2 required
                  </Typography>
                </Box>

                {/* Investment Amount */}
                <Box>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      mb: 1,
                      fontWeight: 600,
                      color: '#334155',
                      fontSize: '0.875rem'
                    }}
                  >
                    Investment Capital
                  </Typography>
                  <TextField
                    type="number"
                    value={investmentAmount}
                    onChange={(e) => setInvestmentAmount(Number(e.target.value))}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                    }}
                    size="small"
                    fullWidth
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#F8FAFC',
                        fontFamily: 'monospace',
                        fontSize: '0.875rem',
                        '& fieldset': {
                          borderColor: '#E2E8F0'
                        },
                        '&:hover fieldset': {
                          borderColor: '#CBD5E1'
                        }
                      }
                    }}
                  />
                </Box>

                {/* Optimization Objective */}
                <Box>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      mb: 1,
                      fontWeight: 600,
                      color: '#334155',
                      fontSize: '0.875rem'
                    }}
                  >
                    Optimization Target
                  </Typography>
                  <FormControl size="small" fullWidth>
                    <Select
                      value={objective}
                      onChange={(e) => setObjective(e.target.value as OptimizationObjectiveLocal)}
                      sx={{
                        backgroundColor: '#F8FAFC',
                        fontSize: '0.875rem',
                        '& .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#E2E8F0'
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: '#CBD5E1'
                        }
                      }}
                    >
                      <MenuItem value="sharpe_ratio">
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <SpeedIcon sx={{ mr: 2, fontSize: 16, color: '#6366F1' }} />
                          <Box>
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 600 }}>Sharpe Ratio</Typography>
                            <Typography sx={{ fontSize: '0.75rem', color: '#64748B' }}>Risk-adjusted returns</Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                      <MenuItem value="dividend_yield">
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <ShowChartIcon sx={{ mr: 2, fontSize: 16, color: '#10B981' }} />
                          <Box>
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 600 }}>Dividend Yield</Typography>
                            <Typography sx={{ fontSize: '0.75rem', color: '#64748B' }}>Income optimization</Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                      <MenuItem value="balanced">
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <SecurityIcon sx={{ mr: 2, fontSize: 16, color: '#F59E0B' }} />
                          <Box>
                            <Typography sx={{ fontSize: '0.875rem', fontWeight: 600 }}>Balanced</Typography>
                            <Typography sx={{ fontSize: '0.75rem', color: '#64748B' }}>Growth & income</Typography>
                          </Box>
                        </Box>
                      </MenuItem>
                    </Select>
                  </FormControl>
                </Box>

                {/* Time Horizon (NEPO only) */}
                <Collapse in={useNewsEnhancement}>
                  <Box>
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        mb: 1,
                        fontWeight: 600,
                        color: '#334155',
                        fontSize: '0.875rem'
                      }}
                    >
                      Investment Horizon
                    </Typography>
                    <FormControl size="small" fullWidth>
                      <Select
                        value={timeHorizon}
                        onChange={(e) => setTimeHorizon(e.target.value)}
                        sx={{
                          backgroundColor: '#F8FAFC',
                          fontSize: '0.875rem',
                          '& .MuiOutlinedInput-notchedOutline': {
                            borderColor: '#CBD5E1'
                          }
                        }}
                      >
                        <MenuItem value="short">Short Term (3-6 months)</MenuItem>
                        <MenuItem value="medium">Medium Term (6-18 months)</MenuItem>
                        <MenuItem value="long">Long Term (18+ months)</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                </Collapse>

                {/* Max Weight */}
                <Box>
                  <Typography 
                    variant="subtitle2" 
                    sx={{ 
                      mb: 1,
                      fontWeight: 600,
                      color: '#334155',
                      fontSize: '0.875rem'
                    }}
                  >
                    Position Limit
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <TextField
                      type="number"
                      value={maxWeight}
                      onChange={(e) => {
                        const raw = e.target.value.replace(',', '.');
                        const parsed = Number(raw);
                        if (!isNaN(parsed)) {
                          setMaxWeight(parsed);
                        }
                      }}
                      inputProps={{ min: 0.1, max: 1, step: 0.1 }}
                      size="small"
                      sx={{ 
                        width: 120,
                        '& .MuiOutlinedInput-root': {
                          backgroundColor: '#F8FAFC',
                          fontFamily: 'monospace',
                          fontSize: '0.875rem',
                          '& fieldset': {
                            borderColor: '#E2E8F0'
                          }
                        }
                      }}
                    />
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#64748B',
                        fontSize: '0.75rem',
                        fontFamily: 'monospace'
                      }}
                    >
                      = {(maxWeight * 100).toFixed(0)}% maximum allocation
                    </Typography>
                  </Box>
                </Box>

                {/* Optimize Button */}
                <Button
                  variant="contained"
                  onClick={handleOptimize}
                  disabled={loading || tickers.filter(t => t).length < 2}
                  size="large"
                  startIcon={loading ? <CircularProgress size={16} color="inherit" /> : <AnalyticsIcon />}
                  sx={{
                    mt: 2,
                    py: 1.5,
                    backgroundColor: useNewsEnhancement ? '#F59E0B' : '#0F172A',
                    color: '#FFFFFF',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    borderRadius: 1,
                    textTransform: 'none',
                    '&:hover': {
                      backgroundColor: useNewsEnhancement ? '#D97706' : '#1E293B',
                    },
                    '&:disabled': {
                      backgroundColor: '#E2E8F0',
                      color: '#94A3B8'
                    }
                  }}
                >
                  {loading 
                    ? 'Analyzing Portfolio...' 
                    : useNewsEnhancement 
                      ? 'Run NEPO Analysis'
                      : 'Run EPO Analysis'
                  }
                </Button>

                {useNewsEnhancement && (
                  <Alert 
                    severity="info" 
                    sx={{ 
                      fontSize: '0.75rem',
                      backgroundColor: '#E0F2FE',
                      color: '#0369A1',
                      border: '1px solid #7DD3FC',
                      '& .MuiAlert-icon': {
                        color: '#0284C7'
                      }
                    }}
                  >
                    <strong>NEPO:</strong> AI-enhanced optimization with real-time market sentiment
                  </Alert>
                )}
              </Stack>
            </Box>
          </Paper>

        {/* Results Panel with Tabs */}
        <Collapse in={showResults && !!results}>
          <Paper elevation={0} sx={{ backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: 2 }}>
            {/* Tab Navigation */}
            <Box sx={{ borderBottom: '1px solid #E2E8F0' }}>
              <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
                {tabLabels.map((label, idx) => (
                  <Tab key={idx} label={label} />
                ))}
              </Tabs>
            </Box>
            <Box sx={{ p: 3 }}>
              {/* Overview Tab */}
              {activeTab === 0 && (
                <Stack spacing={3}>
                  {/* Key Metrics Cards */}
                  <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(4, 1fr)' }, gap: 2 }}>
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center', 
                        backgroundColor: '#EFF6FF',
                        border: '1px solid #DBEAFE',
                        borderRadius: 1,
                        borderLeft: '4px solid #3B82F6'
                      }}
                    >
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontSize: '0.6875rem',
                          fontWeight: 500,
                          color: '#64748B',
                          textTransform: 'uppercase',
                          letterSpacing: '0.025em',
                          mb: 1
                        }}
                      >
                        Expected Return
                      </Typography>
                      <Typography 
                        variant="h4" 
                        sx={{ 
                          fontWeight: 700, 
                          color: '#1E40AF',
                          fontFamily: 'monospace',
                          fontSize: '1.5rem'
                        }}
                      >
                        {results ? formatPercent(results.expected_return) : '--'}
                      </Typography>
                    </Paper>
                    
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center', 
                        backgroundColor: '#FEF2F2',
                        border: '1px solid #FECACA',
                        borderRadius: 1,
                        borderLeft: '4px solid #DC2626'
                      }}
                    >
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontSize: '0.6875rem',
                          fontWeight: 500,
                          color: '#64748B',
                          textTransform: 'uppercase',
                          letterSpacing: '0.025em',
                          mb: 1
                        }}
                      >
                        Volatility Risk
                      </Typography>
                      <Typography 
                        variant="h4" 
                        sx={{ 
                          fontWeight: 700, 
                          color: '#DC2626',
                          fontFamily: 'monospace',
                          fontSize: '1.5rem'
                        }}
                      >
                        {results ? formatPercent(results.volatility) : '--'}
                      </Typography>
                    </Paper>
                    
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center', 
                        backgroundColor: '#F0FDF4',
                        border: '1px solid #BBF7D0',
                        borderRadius: 1,
                        borderLeft: '4px solid #10B981'
                      }}
                    >
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontSize: '0.6875rem',
                          fontWeight: 500,
                          color: '#64748B',
                          textTransform: 'uppercase',
                          letterSpacing: '0.025em',
                          mb: 1
                        }}
                      >
                        Sharpe Ratio
                      </Typography>
                      <Typography 
                        variant="h4" 
                        sx={{ 
                          fontWeight: 700, 
                          color: '#059669',
                          fontFamily: 'monospace',
                          fontSize: '1.5rem'
                        }}
                      >
                        {results ? results.sharpe_ratio.toFixed(2) : '--'}
                      </Typography>
                    </Paper>
                    
                    <Paper 
                      sx={{ 
                        p: 3, 
                        textAlign: 'center', 
                        backgroundColor: '#FFFBEB',
                        border: '1px solid #FED7AA',
                        borderRadius: 1,
                        borderLeft: '4px solid #F59E0B'
                      }}
                    >
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontSize: '0.6875rem',
                          fontWeight: 500,
                          color: '#64748B',
                          textTransform: 'uppercase',
                          letterSpacing: '0.025em',
                          mb: 1
                        }}
                      >
                        Div. Yield
                      </Typography>
                      <Typography 
                        variant="h4" 
                        sx={{ 
                          fontWeight: 700, 
                          color: '#D97706',
                          fontFamily: 'monospace',
                          fontSize: '1.5rem'
                        }}
                      >
                        {results ? formatPercent(results.expected_dividend_yield) : '--'}
                      </Typography>
                    </Paper>
                  </Box>

                  {/* Performance Comparison for NEPO */}
                  {useNewsEnhancement && nepoResults && traditionalResults && results && (
                    <Grow in={showResults} timeout={1100}>
                      <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #e2e8f0 0%, #f8fafc 100%)', borderRadius: 2, boxShadow: '0px 4px 24px rgba(0,0,0,0.05)' }}>
                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', color: 'text.primary' }}>
                          <TimelineIcon sx={{ mr: 1 }} />
                          NEPO vs Traditional EPO Performance
                        </Typography>
                        
                                             <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                           <Box>
                             <Box sx={{ mb: 3 }}>
                               <Typography variant="subtitle2" color="text.primary" gutterBottom>Performance Metrics</Typography>
                               <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                                 <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(255, 255, 255, 0.7)', borderRadius: 1 }}>
                                   <Typography variant="body2" color="text.secondary">Traditional EPO</Typography>
                                   <Typography variant="h6" color="primary">
                                     {formatPercent(traditionalResults.expected_return)}
                                   </Typography>
                                 </Box>
                                 <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(59, 130, 246, 0.1)', borderRadius: 1 }}>
                                   <Typography variant="body2" color="text.secondary">NEPO Enhanced</Typography>
                                   <Typography variant="h6" color="primary.main">
                                     {formatPercent(results.expected_return)}
                                   </Typography>
                                 </Box>
                               </Box>
                             </Box>
                             
                             <Box sx={{ textAlign: 'center', p: 2, backgroundColor: '#FFFFFF', borderRadius: 1, boxShadow: '0px 2px 8px rgba(0,0,0,0.05)' }}>
                               <Typography variant="body2" color="text.secondary">Alpha Generated</Typography>
                               <Typography 
                                 variant="h5" 
                                 color={results.expected_return > traditionalResults.expected_return ? 'success.main' : 'error.main'}
                                 sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}
                               >
                                 {results.expected_return > traditionalResults.expected_return ? 
                                   <TrendingUpIcon sx={{ mr: 0.5 }} /> : 
                                   <TrendingDownIcon sx={{ mr: 0.5 }} />
                                 }
                                 {formatPercent(results.expected_return - traditionalResults.expected_return)}
                               </Typography>
                             </Box>
                           </Box>
                           
                           <Box>
                             {createComparisonData() && (
                               <Box sx={{ height: 200 }}>
                                 <Bar 
                                   data={createComparisonData()!} 
                                   options={{
                                     responsive: true,
                                     maintainAspectRatio: false,
                                     plugins: {
                                       legend: { position: 'top' as const },
                                       title: { display: true, text: 'Performance Comparison' }
                                     },
                                     scales: {
                                       y: { beginAtZero: true }
                                     }
                                   }}
                                 />
                               </Box>
                             )}
                           </Box>
                         </Box>
                      </Paper>
                    </Grow>
                  )}

                  {/* Portfolio Allocation */}
                  <Grow in={showResults} timeout={1300}>
                    <Box>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                        <ShowChartIcon sx={{ mr: 1 }} />
                        Portfolio Allocation
                      </Typography>
                      
                                         <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                         <Box>
                           {results && (
                             <Box sx={{ height: 300 }}>
                               <Pie 
                                 data={createPieData(results.optimized_weights)} 
                                 options={{
                                   responsive: true,
                                   maintainAspectRatio: false,
                                   plugins: {
                                     legend: { position: 'right' as const },
                                     title: { display: true, text: 'Portfolio Weights' }
                                   }
                                 }}
                               />
                             </Box>
                           )}
                         </Box>
                         
                         <Box>
                          <TableContainer component={Paper} sx={{ maxHeight: 300 }}>
                            <Table size="small" stickyHeader>
                              <TableHead>
                                <TableRow sx={{ backgroundColor: 'grey.100' }}>
                                  <TableCell><strong>Stock</strong></TableCell>
                                  <TableCell align="right"><strong>Weight</strong></TableCell>
                                  <TableCell align="right"><strong>Amount</strong></TableCell>
                                  <TableCell align="right"><strong>Est. Shares</strong></TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {results && Object.entries(results.optimized_weights).map(([ticker, weight], index) => {
                                  const dollarAmount = weight * investmentAmount;
                                  const estimatedPrice = ticker === 'SPY' ? 500 : ticker === 'GOOGL' ? 150 : 200;
                                  const shares = Math.floor(dollarAmount / estimatedPrice);
                                  
                                  return (
                                    <Fade key={ticker} in={showResults} timeout={1500 + index * 200}>
                                      <TableRow hover>
                                        <TableCell>
                                          <Chip 
                                            label={ticker} 
                                            size="small" 
                                            variant="outlined"
                                            avatar={<Avatar sx={{ fontSize: '0.65rem' }}>{ticker[0]}</Avatar>}
                                          />
                                        </TableCell>
                                        <TableCell align="right">
                                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                                            <LinearProgress 
                                              variant="determinate" 
                                              value={weight * 100} 
                                              sx={{ 
                                                width: 60, 
                                                mr: 1, 
                                                height: 8, 
                                                borderRadius: 4,
                                                backgroundColor: 'grey.200',
                                                '& .MuiLinearProgress-bar': {
                                                  borderRadius: 4,
                                                  background: `linear-gradient(90deg, #3b82f6, #1d4ed8)`
                                                }
                                              }}
                                            />
                                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                              {(weight * 100).toFixed(1)}%
                                            </Typography>
                                          </Box>
                                        </TableCell>
                                        <TableCell align="right">
                                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                            {formatCurrency(dollarAmount)}
                                          </Typography>
                                        </TableCell>
                                        <TableCell align="right">
                                          <Typography variant="body2">
                                            {shares.toLocaleString()}
                                          </Typography>
                                        </TableCell>
                                      </TableRow>
                                    </Fade>
                                  );
                                })}
                              </TableBody>
                            </Table>
                                                 </TableContainer>
                         </Box>
                       </Box>
                    </Box>
                  </Grow>

                  {/* News Intelligence (NEPO only) */}
                  {useNewsEnhancement && nepoResults?.news_intelligence && (
                    <Grow in={showResults} timeout={1500}>
                      <Paper sx={{ 
                        p: 3, 
                        backgroundColor: '#F1F5F9', 
                        color: 'text.primary',
                        borderRadius: 2,
                        boxShadow: '0px 4px 24px rgba(0,0,0,0.05)'
                      }}>
                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                          <NewspaperIcon sx={{ mr: 1 }} />
                          Market Intelligence & Stock Selection
                          {nepoResults.news_intelligence.gemini_powered && (
                            <Chip 
                              label="AI Powered" 
                              size="small" 
                              sx={{ ml: 1, backgroundColor: 'rgba(0,0,0,0.04)', color: 'primary.main' }}
                              icon={<PsychologyIcon sx={{ fontSize: '16px !important' }} />}
                            />
                          )}
                        </Typography>
                        
                        {/* News Analyses */}
                        {nepoResults.news_intelligence.news_analyses && Object.keys(nepoResults.news_intelligence.news_analyses).length > 0 && (
                          <Box>
                            <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                              Stock Selection Rationale:
                            </Typography>
                                                     <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 2 }}>
                               {Object.entries(nepoResults.news_intelligence.news_analyses).map(([ticker, analysis]: [string, any], index) => (
                                 <Box key={ticker}>
                                  <Fade in={showResults} timeout={2000 + index * 300}>
                                    <Paper sx={{ 
                                      p: 2, 
                                      backgroundColor: 'white', 
                                      color: 'text.primary',
                                      borderRadius: 1,
                                      border: '1px solid #E2E8F0',
                                      boxShadow: '0px 2px 12px rgba(0,0,0,0.04)'
                                    }}>
                                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                        <Avatar sx={{ mr: 1, fontSize: '0.75rem', backgroundColor: 'warning.main' }}>
                                          {ticker[0]}
                                        </Avatar>
                                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                                          {ticker}
                                        </Typography>
                                        <Chip 
                                          label={`Sentiment: ${analysis.sentiment_score?.toFixed(2) || 'N/A'}`}
                                          size="small"
                                          color="primary"
                                          sx={{ ml: 'auto' }}
                                        />
                                      </Box>
                                      <Typography variant="body2" sx={{ mb: 1 }}>
                                        <strong>Confidence:</strong> {((analysis.confidence || 0) * 100).toFixed(0)}%
                                      </Typography>
                                      <Typography variant="body2" sx={{ fontSize: '0.875rem', lineHeight: 1.4 }}>
                                        {analysis.selection_reasoning || analysis.summary || `Selected for portfolio diversification and risk-adjusted returns.`}
                                      </Typography>
                                                                     </Paper>
                                   </Fade>
                                 </Box>
                               ))}
                             </Box>
                          </Box>
                        )}
                      </Paper>
                    </Grow>
                  )}

                  {/* Methodology */}
                  <Grow in={showResults} timeout={1700}>
                    <Paper sx={{ p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
                      <Typography variant="body2">
                        <strong>Methodology:</strong> {useNewsEnhancement 
                          ? 'News-Enhanced Portfolio Optimization (NEPO) combining quantitative analysis with real-time market intelligence'
                          : 'Enhanced Portfolio Optimization (EPO) using advanced quantitative methods and correlation shrinkage'
                        }
                      </Typography>
                      {nepoResults?.metadata?.analysis_features && (
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            <strong>Features:</strong> {nepoResults.metadata.analysis_features.filter(f => f).join(' • ')}
                          </Typography>
                        </Box>
                      )}
                    </Paper>
                  </Grow>

                  {/* ===== Additional visualisations on same page ===== */}
                  {showResults && (
                    <Box sx={{ mt: 4 }}>
                      {/* Efficient Frontier */}
                      {efficientFrontier && (
                        <Box sx={{ mb: 4 }}>
                          <Typography variant="h6" gutterBottom>
                            Efficient Frontier
                          </Typography>
                          {(() => {
                            const vols = efficientFrontier.frontier_points.map(p => p.volatility * 100);
                            const rets = efficientFrontier.frontier_points.map(p => p.expected_return * 100);
                            const xMin = Math.min(...vols) * 0.9;
                            const xMax = Math.max(...vols) * 1.1;
                            const yMin = Math.min(...rets) * 0.9;
                            const yMax = Math.max(...rets) * 1.1;
                            return (
                              <Scatter
                                data={{
                                  datasets: [
                                    {
                                      label: 'Efficient Frontier',
                                      data: efficientFrontier.frontier_points.map(p => ({ x: p.volatility * 100, y: p.expected_return * 100 })),
                                      borderColor: '#3B82F6',
                                      backgroundColor: 'rgba(59,130,246,0.4)',
                                      showLine: true,
                                      fill: false,
                                    },
                                  ],
                                }}
                                options={{
                                  scales: {
                                    x: { title: { display: true, text: 'Volatility (%)' }, suggestedMin: xMin, suggestedMax: xMax },
                                    y: { title: { display: true, text: 'Expected Return (%)' }, suggestedMin: yMin, suggestedMax: yMax },
                                  },
                                  plugins: { legend: { position: 'top' } },
                                }}
                              />
                            );
                          })()}
                        </Box>
                      )}

                      {/* Correlation Matrix */}
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          Correlation Matrix
                        </Typography>
                        {renderCorrelationMatrix()}
                      </Box>
                    </Box>
                  )}
                </Stack>
              )}
            </Box>
          </Paper>
        </Collapse>
      </Box>
    </Box>
  );
};

export default PortfolioOptimization; 
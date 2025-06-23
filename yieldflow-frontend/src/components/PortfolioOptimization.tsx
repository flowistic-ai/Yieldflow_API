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
  InputLabel,
  Switch,
  FormControlLabel,
  Alert,
  Card,
  CardContent,
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
  useTheme,
  Fade,
  Slide,
  Grow,
  Collapse,
  CircularProgress,
  Avatar,
  AvatarGroup,
  Tooltip,
} from '@mui/material';

import {
  AutoGraph as AutoGraphIcon,
  Tune as TuneIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Newspaper as NewspaperIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  ShowChart as ShowChartIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Psychology as PsychologyIcon,
  Equalizer as EqualizerIcon,
  Analytics as AnalyticsIcon,
  Stars as StarsIcon,
} from '@mui/icons-material';
import { Pie, Line, Bar } from 'react-chartjs-2';
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
import { portfolioService, OptimizationObjective } from '../services/portfolioService';

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

const PortfolioOptimization: React.FC = () => {
  const theme = useTheme();
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
    } catch (error) {
      console.error('Optimization failed:', error);
      alert('Optimization failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatCurrency = (value: number) => `$${value.toLocaleString()}`;

  // Create pie chart data for portfolio allocation
  const createPieData = (weights: Record<string, number>) => {
    const labels = Object.keys(weights);
    const data = Object.values(weights).map(w => w * 100);
    const colors = [
      '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
      '#ec4899', '#14b8a6', '#f97316', '#84cc16', '#6366f1'
    ];

    return {
      labels,
      datasets: [{
        data,
        backgroundColor: colors.slice(0, labels.length),
        borderWidth: 2,
        borderColor: '#ffffff'
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

  return (
    <Box sx={{ p: 4 }}>
      {/* Animated Header */}
      <Slide direction="down" in mountOnEnter unmountOnExit>
        <Paper 
          elevation={0} 
          sx={{ 
            mb: 4, 
            p: 4, 
            background: useNewsEnhancement 
              ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
              : 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)', 
            color: 'white',
            borderRadius: 3,
            position: 'relative',
            overflow: 'hidden'
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AutoGraphIcon sx={{ mr: 2, fontSize: 40 }} />
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                Portfolio Optimization
              </Typography>
              <Typography variant="h6" sx={{ opacity: 0.9 }}>
                Traditional EPO & Advanced News-Enhanced Optimization
              </Typography>
            </Box>
          </Box>
          
          <Typography variant="body1" sx={{ opacity: 0.9 }}>
            Choose between traditional Enhanced Portfolio Optimization (EPO) or advanced 
            News-Enhanced Portfolio Optimization (NEPO) with real-time market intelligence.
          </Typography>

          {/* Animated background effects */}
          <Box
            sx={{
              position: 'absolute',
              top: -50,
              right: -50,
              width: 200,
              height: 200,
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '50%',
              animation: 'pulse 4s ease-in-out infinite',
              '@keyframes pulse': {
                '0%, 100%': { transform: 'scale(1)', opacity: 0.5 },
                '50%': { transform: 'scale(1.1)', opacity: 0.3 }
              }
            }}
          />
        </Paper>
      </Slide>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 4 }}>
        {/* Configuration Panel */}
        <Fade in>
          <Card elevation={2} sx={{ height: 'fit-content' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <TuneIcon sx={{ mr: 1 }} />
                Optimization Settings
              </Typography>

              <Stack spacing={3}>
                {/* Optimization Mode Toggle */}
                <Box>
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
                        <Typography variant="body1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                          {useNewsEnhancement ? (
                            <>
                              <PsychologyIcon sx={{ mr: 1, color: 'warning.main' }} />
                              Advanced NEPO Mode
                            </>
                          ) : (
                            <>
                              <EqualizerIcon sx={{ mr: 1, color: 'primary.main' }} />
                              Traditional EPO Mode
                            </>
                          )}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {useNewsEnhancement 
                            ? 'News-Enhanced Portfolio Optimization with real-time market intelligence'
                            : 'Enhanced Portfolio Optimization using quantitative methods only'
                          }
                        </Typography>
                      </Box>
                    }
                  />
                </Box>

                <Divider />

                {/* Tickers */}
                <Box>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                    Stock Tickers
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <TextField
                      size="small"
                      placeholder="Enter ticker (e.g., AAPL)"
                      value={newTicker}
                      onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                      onKeyPress={(e) => e.key === 'Enter' && addTicker()}
                      sx={{ flexGrow: 1 }}
                    />
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={addTicker}
                      disabled={!newTicker.trim()}
                    >
                      Add
                    </Button>
                  </Box>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {tickers.filter(t => t).map((ticker, index) => (
                      <Grow key={index} in>
                        <Chip
                          label={ticker}
                          onDelete={() => removeTicker(index)}
                          deleteIcon={<RemoveIcon />}
                          color="primary"
                          variant="outlined"
                          avatar={<Avatar sx={{ fontSize: '0.75rem' }}>{ticker[0]}</Avatar>}
                        />
                      </Grow>
                    ))}
                  </Box>
                </Box>

                {/* Investment Amount */}
                <TextField
                  label="Investment Amount"
                  type="number"
                  value={investmentAmount}
                  onChange={(e) => setInvestmentAmount(Number(e.target.value))}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                  size="small"
                />

                {/* Optimization Objective */}
                <FormControl size="small">
                  <InputLabel>Optimization Objective</InputLabel>
                  <Select
                    value={objective}
                    label="Optimization Objective"
                    onChange={(e) => setObjective(e.target.value as OptimizationObjectiveLocal)}
                  >
                    <MenuItem value="sharpe_ratio">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <SpeedIcon sx={{ mr: 1, fontSize: 18 }} />
                        Sharpe Ratio
                      </Box>
                    </MenuItem>
                    <MenuItem value="dividend_yield">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <ShowChartIcon sx={{ mr: 1, fontSize: 18 }} />
                        Dividend Yield
                      </Box>
                    </MenuItem>
                    <MenuItem value="balanced">
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <SecurityIcon sx={{ mr: 1, fontSize: 18 }} />
                        Balanced
                      </Box>
                    </MenuItem>
                  </Select>
                </FormControl>

                {/* Time Horizon (NEPO only) */}
                <Collapse in={useNewsEnhancement}>
                  <FormControl size="small" fullWidth>
                    <InputLabel>Time Horizon</InputLabel>
                    <Select
                      value={timeHorizon}
                      label="Time Horizon"
                      onChange={(e) => setTimeHorizon(e.target.value)}
                    >
                      <MenuItem value="short">Short (3-6 months)</MenuItem>
                      <MenuItem value="medium">Medium (6-18 months)</MenuItem>
                      <MenuItem value="long">Long (18+ months)</MenuItem>
                    </Select>
                  </FormControl>
                </Collapse>

                {/* Max Weight */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Maximum Weight per Stock
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <TextField
                      type="number"
                      value={maxWeight}
                      onChange={(e) => setMaxWeight(Number(e.target.value))}
                      inputProps={{ min: 0.1, max: 1, step: 0.1 }}
                      size="small"
                      sx={{ width: 100 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {maxWeight} = {(maxWeight * 100).toFixed(0)}% maximum allocation
                    </Typography>
                  </Box>
                </Box>

                {/* Optimize Button */}
                <Button
                  variant="contained"
                  onClick={handleOptimize}
                  disabled={loading || tickers.filter(t => t).length < 2}
                  size="large"
                  startIcon={loading ? <CircularProgress size={20} /> : <AnalyticsIcon />}
                  sx={{
                    mt: 2,
                    py: 1.5,
                    background: useNewsEnhancement 
                      ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                      : 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                    '&:hover': {
                      background: useNewsEnhancement
                        ? 'linear-gradient(135deg, #d97706 0%, #b45309 100%)'
                        : 'linear-gradient(135deg, #047857 0%, #065f46 100%)',
                    }
                  }}
                >
                  {loading 
                    ? 'Optimizing Portfolio...' 
                    : useNewsEnhancement 
                      ? 'Run Advanced NEPO Analysis'
                      : 'Run Traditional EPO'
                  }
                </Button>

                {useNewsEnhancement && (
                  <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
                    <strong>NEPO Mode:</strong> Combines quantitative optimization with real-time news sentiment analysis for enhanced returns
                  </Alert>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Fade>

        {/* Results Panel */}
        <Collapse in={showResults && !!results}>
          <Card elevation={2}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <AssessmentIcon sx={{ mr: 1 }} />
                Optimization Results
                {useNewsEnhancement && nepoResults && (
                  <Chip 
                    label="NEPO Enhanced" 
                    color="warning" 
                    size="small" 
                    sx={{ ml: 1 }}
                    icon={<StarsIcon />}
                  />
                )}
              </Typography>

              <Stack spacing={3}>
                {/* Key Metrics Cards */}
                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' }, gap: 2 }}>
                  <Grow in={showResults} timeout={500}>
                    <Paper 
                      sx={{ 
                        p: 2, 
                        textAlign: 'center', 
                        background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)', 
                        color: 'white',
                        borderRadius: 2
                      }}
                    >
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>Expected Return</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, mt: 1 }}>
                        {results ? formatPercent(results.expected_return) : '0.00%'}
                      </Typography>
                    </Paper>
                  </Grow>
                  <Grow in={showResults} timeout={700}>
                    <Paper 
                      sx={{ 
                        p: 2, 
                        textAlign: 'center', 
                        background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', 
                        color: 'white',
                        borderRadius: 2
                      }}
                    >
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>Risk (Volatility)</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, mt: 1 }}>
                        {results ? formatPercent(results.volatility) : '0.00%'}
                      </Typography>
                    </Paper>
                  </Grow>
                  <Grow in={showResults} timeout={900}>
                    <Paper 
                      sx={{ 
                        p: 2, 
                        textAlign: 'center', 
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', 
                        color: 'white',
                        borderRadius: 2
                      }}
                    >
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>Sharpe Ratio</Typography>
                      <Typography variant="h5" sx={{ fontWeight: 700, mt: 1 }}>
                        {results ? results.sharpe_ratio.toFixed(3) : '0.000'}
                      </Typography>
                    </Paper>
                  </Grow>
                </Box>

                {/* Performance Comparison for NEPO */}
                {useNewsEnhancement && nepoResults && traditionalResults && results && (
                  <Grow in={showResults} timeout={1100}>
                    <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #fef3c7 0%, #fbbf24 100%)', borderRadius: 2 }}>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', color: '#92400e' }}>
                        <TimelineIcon sx={{ mr: 1 }} />
                        NEPO vs Traditional EPO Performance
                      </Typography>
                      
                                             <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                         <Box>
                           <Box sx={{ mb: 3 }}>
                             <Typography variant="subtitle2" color="#92400e" gutterBottom>Performance Metrics</Typography>
                             <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                               <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(255, 255, 255, 0.7)', borderRadius: 1 }}>
                                 <Typography variant="body2" color="text.secondary">Traditional EPO</Typography>
                                 <Typography variant="h6" color="primary">
                                   {formatPercent(traditionalResults.expected_return)}
                                 </Typography>
                               </Box>
                               <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(245, 158, 11, 0.2)', borderRadius: 1 }}>
                                 <Typography variant="body2" color="text.secondary">NEPO Enhanced</Typography>
                                 <Typography variant="h6" color="warning.dark">
                                   {formatPercent(results.expected_return)}
                                 </Typography>
                               </Box>
                             </Box>
                           </Box>
                           
                           <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(255, 255, 255, 0.9)', borderRadius: 1 }}>
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
                      background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)', 
                      color: 'white',
                      borderRadius: 2
                    }}>
                      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                        <NewspaperIcon sx={{ mr: 1 }} />
                        Market Intelligence & Stock Selection
                        {nepoResults.news_intelligence.gemini_powered && (
                          <Chip 
                            label="AI Powered" 
                            size="small" 
                            sx={{ ml: 1, backgroundColor: 'rgba(255, 255, 255, 0.9)', color: 'warning.dark' }}
                            icon={<PsychologyIcon sx={{ fontSize: '16px !important' }} />}
                          />
                        )}
                      </Typography>
                      
                      {/* Investment Thesis */}
                      <Box sx={{ mb: 3, p: 2, backgroundColor: 'rgba(255, 255, 255, 0.15)', borderRadius: 1 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                          Investment Thesis:
                        </Typography>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.6 }}>
                          {nepoResults.news_intelligence.investment_thesis || 'News-enhanced analysis completed with market intelligence integration.'}
                        </Typography>
                      </Box>

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
                                    backgroundColor: 'rgba(255, 255, 255, 0.95)', 
                                    color: 'text.primary',
                                    borderRadius: 1,
                                    border: '1px solid rgba(245, 158, 11, 0.3)'
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
              </Stack>
            </CardContent>
          </Card>
        </Collapse>
      </Box>
    </Box>
  );
};

export default PortfolioOptimization; 
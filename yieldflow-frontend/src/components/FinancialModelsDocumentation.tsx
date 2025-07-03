import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Stack,
  Divider,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Description as DescriptionIcon,
  TrendingUp as TrendingUpIcon,
  Calculate as CalculateIcon,
  Psychology as PsychologyIcon,
  Security as SecurityIcon,
  Architecture as ArchitectureIcon,
} from '@mui/icons-material';

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
      id={`docs-tabpanel-${index}`}
      aria-labelledby={`docs-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const FinancialModelsDocumentation: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleDownloadPDF = () => {
    // Create a link to download the PDF
    const link = document.createElement('a');
    link.href = '/YieldFlow_Financial_Models_Documentation.pdf';
    link.download = 'YieldFlow_Financial_Models_Documentation.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header Section */}
      <Paper elevation={2} sx={{ p: 4, mb: 4, background: 'linear-gradient(135deg, #1E293B 0%, #475569 100%)', color: 'white' }}>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700, color: 'white' }}>
              📊 YieldFlow Financial Models
            </Typography>
            <Typography variant="h6" sx={{ color: 'rgba(255,255,255,0.9)', mb: 2 }}>
              Comprehensive Technical Documentation for Advanced Investment Analytics
            </Typography>
            <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
              <Chip label="June 2025" color="secondary" />
              <Chip label="Technical Documentation" sx={{ bgcolor: 'white', color: 'primary.main', fontWeight: 600 }} />
            </Stack>
          </Box>
          <Box>
            <Tooltip title="Download Full PDF Documentation">
              <Button
                variant="contained"
                color="secondary"
                startIcon={<DownloadIcon />}
                onClick={handleDownloadPDF}
                sx={{ 
                  mb: 2,
                  fontSize: '1.1rem',
                  fontWeight: 700,
                  px: 4,
                  py: 1.5,
                  background: 'linear-gradient(45deg, #059669 30%, #10B981 90%)',
                  boxShadow: '0 3px 5px 2px rgba(5, 150, 105, .3)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #047857 30%, #059669 90%)',
                    boxShadow: '0 4px 8px 3px rgba(5, 150, 105, .4)',
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                Download PDF
              </Button>
            </Tooltip>
          </Box>
        </Box>
      </Paper>

      {/* Executive Summary */}
      <Card sx={{ mb: 4 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" gutterBottom color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DescriptionIcon /> Executive Summary
          </Typography>
          <Typography variant="body1" paragraph>
            This document provides a comprehensive overview of the advanced mathematical models and financial formulas 
            implemented in the YieldFlow API. Our platform utilizes cutting-edge quantitative finance methodologies 
            including Enhanced Portfolio Optimization (EPO), News-Enhanced Portfolio Optimization (NEPO), and 
            FinBERT-LSTM-VAR Enhanced Dividend Forecasting.
          </Typography>
          
          <Typography variant="h6" gutterBottom sx={{ mt: 3, color: 'secondary.main' }}>
            Key Innovations:
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip icon={<TrendingUpIcon />} label="EPO: Correlation Shrinkage Methodology" color="primary" variant="outlined" />
            <Chip icon={<PsychologyIcon />} label="NEPO: News Sentiment Integration" color="secondary" variant="outlined" />
            <Chip icon={<CalculateIcon />} label="Enhanced Dividend Forecasting" color="info" variant="outlined" />
            <Chip icon={<SecurityIcon />} label="Monte Carlo Simulation" color="warning" variant="outlined" />
          </Stack>
        </CardContent>
      </Card>

      {/* Navigation Tabs */}
      <Paper elevation={1} sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              fontSize: '0.95rem',
              fontWeight: 600,
              minHeight: 64,
              textTransform: 'none',
            },
          }}
        >
          <Tab icon={<TrendingUpIcon />} label="Portfolio Optimization" />
          <Tab icon={<CalculateIcon />} label="Dividend Forecasting" />
          <Tab icon={<SecurityIcon />} label="Risk Management" />
          <Tab icon={<PsychologyIcon />} label="AI & ML Models" />
          <Tab icon={<ArchitectureIcon />} label="Implementation" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <TabPanel value={tabValue} index={0}>
        <PortfolioOptimizationSection />
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        <DividendForecastingSection />
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        <RiskManagementSection />
      </TabPanel>
      
      <TabPanel value={tabValue} index={3}>
        <AIModelsSection />
      </TabPanel>
      
      <TabPanel value={tabValue} index={4}>
        <ImplementationSection />
      </TabPanel>
    </Container>
  );
};

// Portfolio Optimization Section Component
const PortfolioOptimizationSection: React.FC = () => (
  <Box>
    <Typography variant="h4" gutterBottom color="primary">
      1. Portfolio Optimization Models
    </Typography>
    
    <Accordion defaultExpanded>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography variant="h6">1.1 Enhanced Portfolio Optimization (EPO)</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body1" paragraph>
          EPO represents our core portfolio optimization methodology, implementing advanced correlation 
          shrinkage techniques to address estimation errors in traditional Mean-Variance Optimization.
        </Typography>
        
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="subtitle2">Core EPO Mathematical Framework</Typography>
        </Alert>
        
        <Paper elevation={1} sx={{ p: 3, bgcolor: '#f8f9fa', mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Objective Function:</Typography>
          <Typography variant="body1" sx={{ 
            fontFamily: '"Computer Modern", "Latin Modern Math", "Times New Roman", serif',
            fontSize: '1.2rem',
            bgcolor: 'white', 
            p: 3, 
            borderRadius: 1,
            textAlign: 'center',
            fontStyle: 'italic',
            border: '2px solid #e3f2fd'
          }}>
            maximize: SR = (μᵀw - rf) / √(wᵀΣw)
          </Typography>
          
          <Typography variant="body2" sx={{ mt: 2 }}>
            Where:
          </Typography>
          <List dense>
            <ListItem><ListItemText primary="SR = Sharpe Ratio" /></ListItem>
            <ListItem><ListItemText primary="μ = Expected returns vector" /></ListItem>
            <ListItem><ListItemText primary="w = Portfolio weights vector" /></ListItem>
            <ListItem><ListItemText primary="rf = Risk-free rate (4.5% - 10Y Treasury)" /></ListItem>
            <ListItem><ListItemText primary="Σ = Shrunk covariance matrix" /></ListItem>
          </List>
        </Paper>
        
        <Paper elevation={1} sx={{ p: 3, bgcolor: '#f8f9fa' }}>
          <Typography variant="subtitle2" gutterBottom>Constraint Set:</Typography>
          <Typography variant="body1" sx={{ 
            fontFamily: '"Computer Modern", "Latin Modern Math", "Times New Roman", serif',
            fontSize: '1.1rem',
            bgcolor: 'white', 
            p: 3, 
            borderRadius: 1,
            fontStyle: 'italic',
            border: '2px solid #e3f2fd',
            lineHeight: 2
          }}>
            ∑wᵢ = 1                    (Budget constraint)<br/>
            0.01 ≤ wᵢ ≤ 0.80          (Position limits)<br/>
            μᵀw ≥ μₘᵢₙ                (Minimum return threshold)
          </Typography>
        </Paper>
      </AccordionDetails>
    </Accordion>
    
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography variant="h6">1.2 News-Enhanced Portfolio Optimization (NEPO)</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body1" paragraph>
          NEPO combines traditional EPO with real-time news sentiment analysis powered by Google Gemini LLM 
          and FinBERT neural networks.
        </Typography>
        
        <Paper elevation={1} sx={{ p: 3, bgcolor: '#f8f9fa' }}>
          <Typography variant="subtitle2" gutterBottom>Combined Optimization:</Typography>
          <Typography variant="body1" sx={{ 
            fontFamily: '"Computer Modern", "Latin Modern Math", "Times New Roman", serif',
            fontSize: '1.2rem',
            bgcolor: 'white', 
            p: 3, 
            borderRadius: 1,
            textAlign: 'center',
            fontStyle: 'italic',
            border: '2px solid #e3f2fd'
          }}>
            w_NEPO = α×w_EPO + (1-α)×w_NEWS
          </Typography>
          
          <Typography variant="body2" sx={{ mt: 2 }}>
            Where α = 0.7 (70% EPO, 30% news adjustment)
          </Typography>
        </Paper>
      </AccordionDetails>
    </Accordion>
  </Box>
);

// Dividend Forecasting Section Component
const DividendForecastingSection: React.FC = () => (
  <Box>
    <Typography variant="h4" gutterBottom color="primary">
      2. Enhanced Dividend Forecasting
    </Typography>
    
    <Accordion defaultExpanded>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography variant="h6">2.1 FinBERT-LSTM-VAR Integration</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Typography variant="body1" paragraph>
          Our enhanced dividend forecasting combines three advanced methodologies:
        </Typography>
        
        <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
          <Chip label="FinBERT: Financial sentiment analysis" color="primary" />
          <Chip label="LSTM: Temporal pattern recognition" color="secondary" />
          <Chip label="VAR: Vector Autoregressive modeling" color="info" />
        </Stack>
        
        <Paper elevation={1} sx={{ p: 3, bgcolor: '#f8f9fa' }}>
          <Typography variant="subtitle2" gutterBottom>Enhanced Gordon Growth Model:</Typography>
          <Typography variant="body1" sx={{ 
            fontFamily: '"Computer Modern", "Latin Modern Math", "Times New Roman", serif',
            fontSize: '1.2rem',
            bgcolor: 'white', 
            p: 3, 
            borderRadius: 1,
            textAlign: 'center',
            fontStyle: 'italic',
            border: '2px solid #e3f2fd',
            mb: 2
          }}>
            DividendProjection = D₀ × (1 + g_enhanced)ᵗ
          </Typography>
          
          <Typography variant="subtitle2" gutterBottom>Enhanced Growth Rate:</Typography>
          <Typography variant="body1" sx={{ 
            fontFamily: '"Computer Modern", "Latin Modern Math", "Times New Roman", serif',
            fontSize: '1.2rem',
            bgcolor: 'white', 
            p: 3, 
            borderRadius: 1,
            textAlign: 'center',
            fontStyle: 'italic',
            border: '2px solid #e3f2fd'
          }}>
            g_enhanced = g_base + g_sentiment + g_financial + g_risk
          </Typography>
        </Paper>
      </AccordionDetails>
    </Accordion>
  </Box>
);

// Risk Management Section Component
const RiskManagementSection: React.FC = () => (
  <Box>
    <Typography variant="h4" gutterBottom color="primary">
      3. Risk Management & Confidence Intervals
    </Typography>
    
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Monte Carlo Simulation Framework</Typography>
        <Typography variant="body1" paragraph>
          Our risk management system employs Monte Carlo simulation to generate dynamic confidence intervals 
          for all predictions, providing investors with probabilistic risk assessments.
        </Typography>
        
        <Alert severity="warning">
          <Typography variant="body2">
            All forecasts include 95% confidence intervals generated through 10,000 Monte Carlo simulations
          </Typography>
        </Alert>
      </CardContent>
    </Card>
  </Box>
);

// AI Models Section Component
const AIModelsSection: React.FC = () => (
  <Box>
    <Typography variant="h4" gutterBottom color="primary">
      4. AI & Machine Learning Models
    </Typography>
    
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>FinBERT Neural Network</Typography>
        <Typography variant="body1" paragraph>
          Financial sentiment analysis using domain-specific BERT models trained on financial news data.
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="h6" gutterBottom>LSTM Temporal Networks</Typography>
        <Typography variant="body1" paragraph>
          Long Short-Term Memory networks for capturing temporal dependencies in financial time series.
        </Typography>
      </CardContent>
    </Card>
  </Box>
);

// Implementation Section Component
const ImplementationSection: React.FC = () => (
  <Box>
    <Typography variant="h4" gutterBottom color="primary">
      5. Implementation Architecture
    </Typography>
    
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>Technology Stack</Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Chip label="Python FastAPI" />
          <Chip label="NumPy/SciPy" />
          <Chip label="TensorFlow" />
          <Chip label="FinBERT" />
          <Chip label="PostgreSQL" />
          <Chip label="Redis Cache" />
        </Stack>
        
        <Typography variant="body1" sx={{ mt: 2 }}>
          The YieldFlow API is built on a robust microservices architecture, ensuring scalability, 
          reliability, and real-time performance for all financial calculations.
        </Typography>
      </CardContent>
    </Card>
  </Box>
);

export default FinancialModelsDocumentation; 
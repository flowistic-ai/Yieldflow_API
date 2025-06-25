import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Container,
  Stack,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import StatusIndicator from './StatusIndicator';
import MetricsCard from './MetricsCard';
import FinancialDataTable, { ColumnConfig, RowData } from './FinancialDataTable';

const ProfessionalDemo: React.FC = () => {
  // Sample metrics data
  const portfolioMetrics = [
    {
      label: 'Total Assets',
      value: 2847392.50,
      type: 'currency' as const,
      status: 'positive' as const,
      change: 0.0847,
      changeType: 'percentage' as const,
      tooltip: 'Total portfolio value including all holdings',
    },
    {
      label: 'Daily P&L',
      value: 23847.20,
      type: 'currency' as const,
      status: 'positive' as const,
      showTrend: true,
      subtitle: '+2.1% from yesterday',
    },
    {
      label: 'Dividend Yield',
      value: 0.0425,
      type: 'percentage' as const,
      status: 'positive' as const,
      precision: 3,
      tooltip: 'Weighted average dividend yield across portfolio',
    },
  ];

  const riskMetrics = [
    {
      label: 'VaR (1D, 95%)',
      value: -45692.30,
      type: 'currency' as const,
      status: 'warning' as const,
      precision: 0,
      tooltip: 'Value at Risk for 1 day at 95% confidence',
    },
    {
      label: 'Beta',
      value: 1.23,
      type: 'number' as const,
      status: 'neutral' as const,
      precision: 2,
      subtitle: 'vs S&P 500',
    },
    {
      label: 'Sharpe Ratio',
      value: 1.45,
      type: 'number' as const,
      status: 'positive' as const,
      precision: 2,
      tooltip: 'Risk-adjusted return metric',
    },
  ];

  // Sample table data
  const tableColumns: ColumnConfig[] = [
    { key: 'symbol', label: 'Symbol', type: 'text', sortable: true, width: 80 },
    { key: 'name', label: 'Company', type: 'text', sortable: true, width: 200 },
    { key: 'price', label: 'Price', type: 'currency', align: 'right', sortable: true, precision: 2 },
    { key: 'change', label: 'Change', type: 'currency', align: 'right', showTrend: true, precision: 2 },
    { key: 'changePercent', label: 'Change %', type: 'percentage', align: 'right', showTrend: true, precision: 2 },
    { key: 'volume', label: 'Volume', type: 'number', align: 'right', precision: 0 },
    { key: 'dividendYield', label: 'Div Yield', type: 'percentage', align: 'right', precision: 2 },
    { key: 'peRatio', label: 'P/E', type: 'number', align: 'right', precision: 1 },
  ];

  const tableData: RowData[] = [
    {
      id: 1,
      symbol: 'AAPL',
      name: 'Apple Inc.',
      price: 175.84,
      change: 2.47,
      changePercent: 0.0142,
      volume: 54792340,
      dividendYield: 0.0051,
      peRatio: 28.7,
    },
    {
      id: 2,
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      price: 347.62,
      change: -4.23,
      changePercent: -0.0120,
      volume: 23847293,
      dividendYield: 0.0073,
      peRatio: 32.1,
    },
    {
      id: 3,
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      price: 138.45,
      change: 1.89,
      changePercent: 0.0138,
      volume: 18293847,
      dividendYield: 0.0000,
      peRatio: 25.3,
    },
    {
      id: 4,
      symbol: 'AMZN',
      name: 'Amazon.com Inc.',
      price: 143.76,
      change: -0.84,
      changePercent: -0.0058,
      volume: 28374650,
      dividendYield: 0.0000,
      peRatio: 47.2,
    },
    {
      id: 5,
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      price: 218.34,
      change: 8.92,
      changePercent: 0.0426,
      volume: 89374629,
      dividendYield: 0.0000,
      peRatio: 65.8,
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, color: '#0F172A' }}>
          Professional Financial Dashboard Demo
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Showcasing enterprise-grade components with institutional styling standards
        </Typography>
      </Box>

      {/* Status Indicators Demo */}
      <Paper sx={{ p: 3, mb: 3, borderRadius: 1.5 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
          Status Indicators
        </Typography>
        <Stack direction="row" spacing={2} flexWrap="wrap">
          <StatusIndicator type="positive" value={47382.50} format="currency" label="Profit" variant="full" />
          <StatusIndicator type="negative" value={-2847.30} format="currency" label="Loss" variant="full" />
          <StatusIndicator type="warning" value={0.85} format="percentage" label="Risk Level" variant="full" />
          <StatusIndicator type="neutral" value="Processing" label="Status" variant="full" />
          <StatusIndicator type="positive" value={0.0342} format="percentage" showTrend label="Yield" variant="chip" />
          <StatusIndicator type="info" value="Connected" label="Data Feed" variant="chip" />
        </Stack>
      </Paper>

             {/* Metrics Cards Demo */}
       <Box sx={{ 
         display: 'grid', 
         gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, 
         gap: 3, 
         mb: 3 
       }}>
         <MetricsCard
           title="Portfolio Overview"
           metrics={portfolioMetrics}
           variant="standard"
           showActions
           lastUpdated={new Date()}
         />
         <MetricsCard
           title="Risk Metrics"
           metrics={riskMetrics}
           variant="standard"
           showActions
           lastUpdated={new Date()}
         />
       </Box>

             {/* Compact Metrics Row */}
       <Box sx={{ 
         display: 'grid', 
         gridTemplateColumns: { xs: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, 
         gap: 2, 
         mb: 3 
       }}>
         {[
           { label: 'Market Cap', value: 2.84e12, type: 'currency' as const, precision: 0 },
           { label: 'P/E Ratio', value: 24.7, type: 'number' as const },
           { label: 'ROE', value: 0.187, type: 'percentage' as const },
           { label: 'Debt/Equity', value: 0.42, type: 'number' as const },
         ].map((metric, index) => (
           <MetricsCard
             key={index}
             title=""
             metrics={[metric]}
             variant="compact"
           />
         ))}
       </Box>

      {/* Financial Data Table Demo */}
      <Paper sx={{ p: 0, borderRadius: 1.5, overflow: 'hidden' }}>
        <Box sx={{ p: 3, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Holdings Overview
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Real-time market data with professional density
          </Typography>
        </Box>
        <FinancialDataTable
          columns={tableColumns}
          data={tableData}
          variant="dense"
          showActions
          stickyHeader
          maxHeight={400}
        />
      </Paper>

      {/* Professional Styling Examples */}
      <Box sx={{ mt: 4 }}>
                 <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
           Typography & Styling Examples
         </Typography>
         <Box sx={{ 
           display: 'grid', 
           gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, 
           gap: 3 
         }}>
           <Card className="card-financial">
             <CardContent>
               <Typography variant="h6" className="text-professional" gutterBottom>
                 Financial Data Typography
               </Typography>
               <Box className="metric-container">
                 <div className="metric-label">Current Price</div>
                 <div className="metric-value positive">$1,847.32</div>
                 <div className="metric-subtitle">+2.4% from previous close</div>
               </Box>
               <Divider sx={{ my: 2 }} />
               <Box>
                 <Typography className="text-data-label" gutterBottom>
                   Monospace Financial Data
                 </Typography>
                 <Typography className="text-financial-data">
                   AAPL: 175.84 (+2.47) | MSFT: 347.62 (-4.23)
                 </Typography>
               </Box>
             </CardContent>
           </Card>

           <Card className="card-status positive">
             <CardContent className="layout-compact">
               <Typography variant="h6" gutterBottom>
                 Status Card Example
               </Typography>
               <Stack spacing={1}>
                 <Box className="status-positive layout-dense" sx={{ borderRadius: 1, p: 1 }}>
                   <Typography variant="caption">Positive Status</Typography>
                 </Box>
                 <Box className="status-negative layout-dense" sx={{ borderRadius: 1, p: 1 }}>
                   <Typography variant="caption">Negative Status</Typography>
                 </Box>
                 <Box className="status-warning layout-dense" sx={{ borderRadius: 1, p: 1 }}>
                   <Typography variant="caption">Warning Status</Typography>
                 </Box>
               </Stack>
             </CardContent>
           </Card>

           <Card>
             <CardContent>
               <Typography variant="h6" gutterBottom>
                 Dense Layout Examples
               </Typography>
               <Box className="layout-financial-grid" sx={{ background: '#F8FAFC', borderRadius: 1 }}>
                 <Box className="card-data">
                   <Typography className="text-data-label">Revenue</Typography>
                   <Typography className="text-financial-large">$847M</Typography>
                 </Box>
                 <Box className="card-data">
                   <Typography className="text-data-label">Growth</Typography>
                   <Typography className="text-financial-large">+12.3%</Typography>
                 </Box>
               </Box>
             </CardContent>
           </Card>
         </Box>
      </Box>
    </Container>
  );
};

export default ProfessionalDemo; 
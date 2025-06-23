import React, { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline, GlobalStyles, Box, Tabs, Tab, Container } from '@mui/material';
import DividendAnalysisComponent from './components/DividendAnalysis';
import PortfolioOptimization from './components/PortfolioOptimization';
import SmartQueryInterface from './components/SmartQueryInterface';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0F172A', // Professional dark navy
      light: '#334155',
      dark: '#020617',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#059669', // Financial green
      light: '#10B981',
      dark: '#047857',
      contrastText: '#ffffff',
    },
    success: {
      main: '#10B981', // Emerald green
      light: '#34D399',
      dark: '#047857',
    },
    warning: {
      main: '#F59E0B', // Amber
      light: '#FCD34D',
      dark: '#D97706',
    },
    error: {
      main: '#DC2626', // Professional red
      light: '#EF4444',
      dark: '#B91C1C',
    },
    info: {
      main: '#3B82F6', // Professional blue
      light: '#60A5FA',
      dark: '#1D4ED8',
    },
    background: {
      default: '#F8FAFC', // Light gray background
      paper: '#FFFFFF',
    },
    text: {
      primary: '#0F172A',
      secondary: '#64748B',
    },
    divider: '#E2E8F0',
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  spacing: 8,
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
          fontSize: '0.875rem',
          fontWeight: 600,
          textTransform: 'none',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #0F172A 0%, #334155 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #334155 0%, #475569 100%)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          border: '1px solid #F1F5F9',
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          },
          transition: 'box-shadow 0.2s ease-in-out',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#059669',
            },
          },
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontSize: '0.875rem',
          fontWeight: 600,
          minHeight: 48,
          '&.Mui-selected': {
            color: '#059669',
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          backgroundColor: '#059669',
          height: 3,
          borderRadius: 2,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          borderRadius: 6,
        },
      },
    },
  },
});

const globalStyles = (
  <GlobalStyles
    styles={{
      '*': {
        boxSizing: 'border-box',
      },
      html: {
        WebkitFontSmoothing: 'antialiased',
        MozOsxFontSmoothing: 'grayscale',
      },
      body: {
        margin: 0,
        padding: 0,
        fontFamily: theme.typography.fontFamily,
        backgroundColor: theme.palette.background.default,
      },
      '#root': {
        minHeight: '100vh',
      },
      '.App': {
        minHeight: '100vh',
        backgroundColor: theme.palette.background.default,
      },
    }}
  />
);

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
      id={`app-tabpanel-${index}`}
      aria-labelledby={`app-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [mainTabValue, setMainTabValue] = useState(0);

  const handleMainTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setMainTabValue(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {globalStyles}
      <div className="App">
        <Box sx={{ bgcolor: 'background.paper', minHeight: '100vh' }}>
          <Container maxWidth="xl" sx={{ p: 0 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'white' }}>
              <Tabs 
                value={mainTabValue} 
                onChange={handleMainTabChange}
                aria-label="YieldFlow main navigation"
                sx={{
                  px: 4,
                  '& .MuiTab-root': {
                    fontSize: '1rem',
                    fontWeight: 600,
                    minHeight: 64,
                    textTransform: 'none',
                  },
                }}
              >
                <Tab label="🤖 AI Assistant" />
                <Tab label="Dividend Analysis" />
                <Tab label="Portfolio Optimization" />
              </Tabs>
            </Box>
            
            <TabPanel value={mainTabValue} index={0}>
              <SmartQueryInterface />
            </TabPanel>
            
            <TabPanel value={mainTabValue} index={1}>
              <DividendAnalysisComponent />
            </TabPanel>
            
            <TabPanel value={mainTabValue} index={2}>
              <PortfolioOptimization />
            </TabPanel>
          </Container>
        </Box>
      </div>
    </ThemeProvider>
  );
}

export default App;

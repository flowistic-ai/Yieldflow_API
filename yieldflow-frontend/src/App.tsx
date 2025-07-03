import React, { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline, GlobalStyles, Box, Tabs, Tab, Container } from '@mui/material';
import DividendAnalysisComponent from './components/DividendAnalysis';
import PortfolioOptimization from './components/PortfolioOptimization';
import SmartQueryInterface from './components/SmartQueryInterface';
import FinancialModelsDocumentation from './components/FinancialModelsDocumentation';

// Extend the Material-UI theme interface for custom properties
declare module '@mui/material/styles' {
  interface Palette {
    financial: {
      positive: string;
      negative: string;
      neutral: string;
      warning: string;
      positiveBackground: string;
      negativeBackground: string;
      neutralBackground: string;
      warningBackground: string;
    };
  }

  interface PaletteOptions {
    financial?: {
      positive?: string;
      negative?: string;
      neutral?: string;
      warning?: string;
      positiveBackground?: string;
      negativeBackground?: string;
      neutralBackground?: string;
      warningBackground?: string;
    };
  }

  interface TypographyVariants {
    financialData: React.CSSProperties;
    financialLarge: React.CSSProperties;
    dataLabel: React.CSSProperties;
    fontFamilyMonospace: string;
  }

  interface TypographyVariantsOptions {
    financialData?: React.CSSProperties;
    financialLarge?: React.CSSProperties;
    dataLabel?: React.CSSProperties;
    fontFamilyMonospace?: string;
  }
}

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
    // Enhanced financial status colors
    financial: {
      positive: '#059669',
      negative: '#DC2626',
      neutral: '#6B7280',
      warning: '#D97706',
      positiveBackground: '#F0FDF4',
      negativeBackground: '#FEF2F2',
      neutralBackground: '#F9FAFB',
      warningBackground: '#FFFBEB',
    },
  },
  typography: {
    // Professional typography system for financial applications
    fontFamily: '"Inter", "SF Pro Display", "Segoe UI", "Roboto", "Helvetica Neue", sans-serif',
    
    // Financial data monospace font
    fontFamilyMonospace: '"JetBrains Mono", "SF Mono", "Monaco", "Menlo", "Consolas", monospace',
    
    h1: {
      fontSize: '2.25rem', // 36px
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.025em',
      color: '#0F172A',
    },
    h2: {
      fontSize: '1.875rem', // 30px
      fontWeight: 700,
      lineHeight: 1.25,
      letterSpacing: '-0.02em',
      color: '#0F172A',
    },
    h3: {
      fontSize: '1.5rem', // 24px
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.015em',
      color: '#0F172A',
    },
    h4: {
      fontSize: '1.25rem', // 20px
      fontWeight: 600,
      lineHeight: 1.35,
      letterSpacing: '-0.01em',
      color: '#1E293B',
    },
    h5: {
      fontSize: '1.125rem', // 18px
      fontWeight: 600,
      lineHeight: 1.4,
      color: '#1E293B',
    },
    h6: {
      fontSize: '1rem', // 16px
      fontWeight: 600,
      lineHeight: 1.4,
      color: '#334155',
    },
    
    // Body text for general content
    body1: {
      fontSize: '0.875rem', // 14px - More compact for financial data
      lineHeight: 1.5,
      color: '#334155',
    },
    body2: {
      fontSize: '0.75rem', // 12px - Dense information display
      lineHeight: 1.4,
      color: '#475569',
    },
    
    // Financial data typography
    financialData: {
      fontSize: '0.75rem', // 12px
      fontFamily: '"JetBrains Mono", "SF Mono", "Monaco", "Menlo", "Consolas", monospace',
      fontWeight: 500,
      lineHeight: 1.2,
      letterSpacing: '0.01em',
    },
    
    // Large financial numbers
    financialLarge: {
      fontSize: '1.125rem', // 18px
      fontFamily: '"JetBrains Mono", "SF Mono", "Monaco", "Menlo", "Consolas", monospace',
      fontWeight: 600,
      lineHeight: 1.2,
      letterSpacing: '-0.01em',
    },
    
    // Compact data labels
    dataLabel: {
      fontSize: '0.6875rem', // 11px
      fontWeight: 500,
      lineHeight: 1.2,
      letterSpacing: '0.025em',
      textTransform: 'uppercase',
      color: '#64748B',
    },
    
    button: {
      fontSize: '0.875rem',
      fontWeight: 600,
      lineHeight: 1.4,
      letterSpacing: '0.01em',
      textTransform: 'none',
    },
    
    caption: {
      fontSize: '0.6875rem', // 11px
      lineHeight: 1.3,
      color: '#64748B',
    },
  },
  spacing: 4, // 4px base unit for tighter professional spacing
  shape: {
    borderRadius: 6, // More conservative radius for professional look
  },
  components: {
    // Enhanced Button Components
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          padding: '8px 20px',
          fontSize: '0.875rem',
          fontWeight: 600,
          lineHeight: 1.4,
          letterSpacing: '0.01em',
          textTransform: 'none',
          boxShadow: 'none',
          transition: 'all 0.15s ease-in-out',
          '&:hover': {
            boxShadow: '0 2px 8px rgba(15, 23, 42, 0.15)',
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)',
          border: '1px solid transparent',
          '&:hover': {
            background: 'linear-gradient(135deg, #1E293B 0%, #334155 100%)',
            boxShadow: '0 4px 12px rgba(15, 23, 42, 0.25)',
          },
        },
        outlined: {
          borderColor: '#E2E8F0',
          color: '#334155',
          backgroundColor: '#FFFFFF',
          '&:hover': {
            borderColor: '#059669',
            backgroundColor: '#F8FAFC',
            color: '#059669',
          },
        },
        text: {
          color: '#334155',
          '&:hover': {
            backgroundColor: '#F1F5F9',
            color: '#059669',
          },
        },
      },
    },

    // Professional Card Design System
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          boxShadow: '0 1px 3px rgba(15, 23, 42, 0.08)',
          transition: 'all 0.15s ease-in-out',
          '&:hover': {
            borderColor: '#CBD5E1',
            boxShadow: '0 4px 12px rgba(15, 23, 42, 0.12)',
            transform: 'translateY(-1px)',
          },
          // Professional card variants
          '&.financial-card': {
            background: 'linear-gradient(145deg, #FFFFFF 0%, #F8FAFC 100%)',
            borderColor: '#E1E5E9',
          },
          '&.data-card': {
            padding: '12px',
            '& .MuiCardContent-root': {
              padding: '8px !important',
              '&:last-child': {
                paddingBottom: '8px !important',
              },
            },
          },
          '&.status-card': {
            borderLeft: '4px solid #059669',
            paddingLeft: '12px',
          },
        },
      },
    },

    // Enhanced Paper Component
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          backgroundColor: '#FFFFFF',
          border: '1px solid #F1F5F9',
          boxShadow: '0 1px 3px rgba(15, 23, 42, 0.08)',
          '&.dense-paper': {
            padding: '8px 12px',
          },
          '&.financial-paper': {
            background: 'linear-gradient(145deg, #FFFFFF 0%, #F8FAFC 100%)',
          },
        },
        elevation1: {
          boxShadow: '0 1px 3px rgba(15, 23, 42, 0.08)',
        },
        elevation2: {
          boxShadow: '0 2px 6px rgba(15, 23, 42, 0.12)',
        },
        elevation3: {
          boxShadow: '0 4px 12px rgba(15, 23, 42, 0.15)',
        },
      },
    },

    // Professional Input Fields
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 6,
            fontSize: '0.875rem',
            backgroundColor: '#FFFFFF',
            transition: 'all 0.15s ease-in-out',
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#059669',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#059669',
              borderWidth: '2px',
            },
          },
          '& .MuiInputLabel-root': {
            fontSize: '0.875rem',
            color: '#64748B',
            '&.Mui-focused': {
              color: '#059669',
            },
          },
        },
      },
    },

    // Enhanced Navigation Tabs
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontSize: '0.875rem',
          fontWeight: 600,
          minHeight: 48,
          padding: '12px 20px',
          color: '#64748B',
          transition: 'all 0.15s ease-in-out',
          '&.Mui-selected': {
            color: '#059669',
            fontWeight: 700,
          },
          '&:hover': {
            color: '#334155',
            backgroundColor: '#F8FAFC',
          },
        },
      },
    },

    MuiTabs: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #E2E8F0',
        },
        indicator: {
          backgroundColor: '#059669',
          height: 3,
          borderRadius: '2px 2px 0 0',
        },
      },
    },

    // Professional Chip Component
    MuiChip: {
      styleOverrides: {
        root: {
          fontSize: '0.75rem',
          fontWeight: 500,
          borderRadius: 4,
          height: 24,
          '&.status-positive': {
            backgroundColor: '#F0FDF4',
            color: '#059669',
            border: '1px solid #BBF7D0',
          },
          '&.status-negative': {
            backgroundColor: '#FEF2F2',
            color: '#DC2626',
            border: '1px solid #FECACA',
          },
          '&.status-neutral': {
            backgroundColor: '#F9FAFB',
            color: '#6B7280',
            border: '1px solid #E5E7EB',
          },
          '&.status-warning': {
            backgroundColor: '#FFFBEB',
            color: '#D97706',
            border: '1px solid #FED7AA',
          },
        },
        label: {
          padding: '0 8px',
        },
      },
    },

    // Enhanced Table Components
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: '#F8FAFC',
          '& .MuiTableCell-head': {
            fontSize: '0.6875rem',
            fontWeight: 600,
            letterSpacing: '0.025em',
            textTransform: 'uppercase',
            color: '#64748B',
            padding: '8px 12px',
            borderBottom: '1px solid #E2E8F0',
          },
        },
      },
    },

    MuiTableBody: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-body': {
            fontSize: '0.75rem',
            padding: '6px 12px',
            borderBottom: '1px solid #F1F5F9',
            fontFamily: '"JetBrains Mono", "SF Mono", monospace',
          },
          '& .MuiTableRow-root:hover': {
            backgroundColor: '#F8FAFC',
          },
        },
      },
    },

    // Loading Progress Components
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 2,
          backgroundColor: '#E2E8F0',
        },
        bar: {
          borderRadius: 2,
          backgroundColor: '#059669',
        },
      },
    },

    MuiCircularProgress: {
      styleOverrides: {
        root: {
          color: '#059669',
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
                <Tab label="Documentation" />
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
            
            <TabPanel value={mainTabValue} index={3}>
              <FinancialModelsDocumentation />
            </TabPanel>
          </Container>
        </Box>
      </div>
    </ThemeProvider>
  );
}

export default App;

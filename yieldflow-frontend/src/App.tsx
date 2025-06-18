import React from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import DividendAnalysisComponent from './components/DividendAnalysis';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <DividendAnalysisComponent />
      </div>
    </ThemeProvider>
  );
}

export default App;

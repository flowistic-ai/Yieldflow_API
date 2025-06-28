# Yieldflow Frontend

**Modern React Dashboard** for comprehensive dividend analysis and financial insights.

## Overview

Professional dividend analysis dashboard built with React 19 and Material-UI. Provides interactive charts, risk assessment, and real-time dividend analytics through a clean, modern interface.

**Features:**
- 📊 **Interactive Dashboard** - Real-time dividend metrics and analytics
- 📈 **Advanced Charts** - Growth tracking, peer comparison, total return analysis
- 🎯 **Risk Assessment** - Dividend quality scoring and sustainability metrics
- 🔍 **Search Interface** - Quick ticker lookup with autocomplete
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## Quick Start

### Prerequisites
- Node.js 16+
- Backend API running on `http://localhost:8000`

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm start
```

**Frontend runs on:** `http://localhost:3000`

### Environment Configuration

The frontend is pre-configured to connect to the backend at `http://localhost:8000`. 

To change the API endpoint, edit `src/services/dividendService.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

## Project Structure

```
src/
├── components/           # React components
│   ├── DividendAnalysis.tsx  # Main analysis dashboard
│   └── Header.tsx           # Navigation header
├── services/            # API services
│   └── dividendService.ts   # Backend API integration
├── App.tsx              # Main application component
└── index.tsx            # Application entry point
```

## Usage

1. **Start the backend** (see main README for backend setup)
2. **Start the frontend** with `npm start`
3. **Enter a ticker** (e.g., AAPL, MSFT, JNJ) in the search field
4. **View analysis** across multiple tabs:
   - **Overview:** Current metrics and key information
   - **Charts:** Growth trends and visualizations
   - **Sustainability:** Coverage ratios and quality metrics
   - **Risk:** Risk assessment and stress testing

## Components

### DividendAnalysis
Main dashboard component with tabbed interface:
- Real-time dividend data fetching
- Interactive charts with Recharts
- Material-UI components for professional styling
- Error handling and loading states

### Header
Navigation component with:
- Ticker search functionality
- Real-time data refresh
- Responsive design

## Available Scripts

### Development
```bash
npm start          # Start development server
npm test           # Run test suite
npm run build      # Build for production
```

### Production Build
```bash
npm run build      # Creates optimized build in /build folder
```

The build folder can be served with any static file server.

## Dependencies

**Core:**
- **React 19** - Frontend framework
- **Material-UI** - Component library and styling
- **Recharts** - Chart library for visualizations
- **Axios** - HTTP client for API calls

**Development:**
- **TypeScript** - Type safety and better development experience
- **React Scripts** - Build tools and development server

## API Integration

The frontend consumes the Yieldflow API through the `dividendService`:

```typescript
// Get current dividend info
const currentInfo = await dividendService.getCurrentDividendInfo('AAPL');

// Get comprehensive analysis
const analysis = await dividendService.getDividendAnalysis('AAPL', true, true);

// Get growth chart data
const chartData = await dividendService.getDividendGrowthChart('AAPL');
```

## Customization

### Styling
- Uses Material-UI theme system
- Responsive design with breakpoints
- Professional color scheme with branded accents

### Charts
- Built with Recharts for interactive visualizations
- Configurable chart types and styling
- Real-time data updates

### Components
- Modular component architecture
- TypeScript interfaces for type safety
- Reusable service layer for API calls

## Troubleshooting

### Common Issues

1. **API Connection Errors:**
   - Ensure backend is running on port 8000
   - Check CORS configuration in backend

2. **Missing Data:**
   - Verify API keys are configured in backend
   - Check browser console for API errors

3. **Build Errors:**
   - Delete `node_modules` and run `npm install`
   - Clear npm cache: `npm cache clean --force`

### Development Tips

- Use browser dev tools to inspect API calls
- Check backend logs for API errors
- Material-UI provides excellent documentation for component customization

## License

MIT License - see main project LICENSE file for details.

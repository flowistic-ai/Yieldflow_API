# Yieldflow API

**Comprehensive Financial Analytics API** - From Data to Insights in One API Call

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-6+-red.svg)](https://redis.io/)

## Overview

Yieldflow is a comprehensive financial analytics API that goes beyond raw data to provide intelligent financial analysis, ratios, visualizations, and AI-powered insights. Built with FastAPI, it offers:

- **Raw Financial Data**: Complete income statements, balance sheets, and cash flow statements
- **Advanced Analytics**: Pre-calculated financial ratios and categorized analysis
- **Visual Charts**: Built-in chart generation and data visualization
- **AI Insights**: Machine learning-powered recommendations and analysis
- **European Compliance**: MiFID II, CSRD compliance features
- **Multi-tier Access**: From free tier to enterprise plans

## Key Features

### Core Value Proposition
- **Intelligent Analysis**: Beyond raw data - get insights, trends, and recommendations
- **Categorized Analytics**: Profitability, Risk, Efficiency, Growth, and Liquidity analysis
- **Ready-to-use Ratios**: 50+ financial ratios with explanations and benchmarks
- **Chart Generation**: Beautiful visualizations with base64-encoded images
- **European Focus**: Multi-currency support and regulatory compliance

### Technical Features
- **High Performance**: Async FastAPI with Redis caching
- **Multi-source Data**: Alpha Vantage, Financial Modeling Prep, Yahoo Finance
- **Rate Limiting**: Tiered plans with smart rate limiting
- **Data Quality**: Cross-validation and confidence scoring
- **Comprehensive Logging**: Structured logging with monitoring

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 13+
- Redis 6+
- External API keys (Alpha Vantage, Financial Modeling Prep)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/yieldflow-api.git
cd yieldflow-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Setup databases**
```bash
# PostgreSQL
createdb yieldflow_db

# Redis (start service)
redis-server
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/api/v1/docs`
- **ReDoc**: `http://localhost:8000/api/v1/redoc`

## Environment Configuration

Key environment variables (see `env.example` for complete list):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/yieldflow_db
REDIS_URL=redis://localhost:6379/0

# API Keys
ALPHA_VANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # Optional for AI features

# Security
SECRET_KEY=your-super-secret-key
```

## API Usage

### Authentication & API Key Generation

#### Option 1: Generate API Key (Recommended)
Use the provided script to generate API keys for different access tiers:

```bash
# Generate API key for testing
python create_api_key.py
```

This will prompt you to select a plan:
- **Free**: 1K requests/day, 10/min - Basic company info and financial data
- **Basic**: 10K requests/day, 60/min - Financial ratios and trend analysis  
- **Pro**: 50K requests/day, 300/min - Advanced analytics and peer comparison
- **Enterprise**: 200K requests/day, 1000/min - Full features and bulk data

The script will generate:
- Your API key (format: `yk_xxxxxxxxxxxxx`)
- User credentials and plan details
- Rate limits and feature access
- Example usage commands

#### Option 2: Use Test Endpoints (No Auth Required)
For quick testing, use the `/test/` endpoints that don't require authentication:

```bash
# Test company information
curl "http://localhost:8000/api/v1/financial/test/company/AAPL"

# Test financial ratios
curl "http://localhost:8000/api/v1/financial/test/ratios/AAPL?ratio_category=profitability"

# Test financial overview
curl "http://localhost:8000/api/v1/financial/test/overview/AAPL"
```

#### Using Your API Key
All authenticated endpoints require the API key in the Authorization header:

```bash
curl -H "Authorization: Bearer your_api_key_here" \
     "http://localhost:8000/api/v1/financial/company/AAPL"
```

**Important**: Replace `your_api_key_here` with the actual API key generated from the script.

### 📋 Available Endpoints

#### Test Endpoints (No Authentication Required)
Perfect for testing the API functionality before implementing authentication:

```bash
# Company Information
GET /api/v1/financial/test/company/{ticker}
curl "http://localhost:8000/api/v1/financial/test/company/AAPL"

# Financial Ratios by Category
GET /api/v1/financial/test/ratios/{ticker}?ratio_category={category}&period={period}
curl "http://localhost:8000/api/v1/financial/test/ratios/AAPL?ratio_category=profitability&period=annual"

# Complete Financial Overview
GET /api/v1/financial/test/overview/{ticker}
curl "http://localhost:8000/api/v1/financial/test/overview/AAPL"
```

**Available ratio categories**: `profitability`, `liquidity`, `leverage`, `efficiency`, `growth`

#### Authenticated Endpoints
These endpoints require a valid API key in the Authorization header:

#### 1. Company Information
```bash
# Basic company information
GET /api/v1/financial/company/{ticker}
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/company/AAPL"
```

#### 2. Financial Statements
```bash
# Get financial statements by type
GET /api/v1/financial/statements/{ticker}?statement_type={type}&period={period}&limit={limit}

# Examples:
# Income statements (annual, last 4 years)
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/statements/AAPL?statement_type=income&period=annual&limit=4"

# Balance sheets (quarterly, last 8 quarters)  
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/statements/AAPL?statement_type=balance&period=quarterly&limit=8"

# Cash flow statements
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/statements/AAPL?statement_type=cash_flow&period=annual&limit=3"
```

**Statement types**: `income`, `balance`, `cash_flow`  
**Periods**: `annual`, `quarterly`

#### 3. Financial Ratios & Analysis
```bash
# All financial ratios
GET /api/v1/financial/ratios/{ticker}?period={period}&ratio_category={category}
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/ratios/AAPL?ratio_category=all&period=annual"

# Specific ratio category
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/ratios/AAPL?ratio_category=profitability"
```

#### 4. Financial Analysis (Pro+ Features)
```bash
# Comprehensive financial analysis
GET /api/v1/financial/analysis/{ticker}?analysis_type={type}&period={period}
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/analysis/AAPL?analysis_type=comprehensive"

# Specific analysis types
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/analysis/AAPL?analysis_type=trends"
```

**Analysis types**: `comprehensive`, `trends`, `liquidity`, `profitability`, `cashflow`

#### 5. Financial Overview
```bash
# Complete financial overview with key metrics
GET /api/v1/financial/overview/{ticker}
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/overview/AAPL"
```

## Response Examples

### Test Company Information Response
```bash
curl "http://localhost:8000/api/v1/financial/test/company/AAPL"
```

```json
{
  "ticker": "AAPL",
  "status": "success",
  "test_mode": true,
  "message": "This is a test endpoint - use /financial/company/AAPL with API key for production",
  "data": {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "market_cap": 2850000000000,
    "pe_ratio": 25.8,
    "dividend_yield": 0.52,
    "52_week_high": 199.62,
    "52_week_low": 164.08,
    "confidence_score": 0.95
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Financial Ratios Response
```bash
curl "http://localhost:8000/api/v1/financial/test/ratios/AAPL?ratio_category=profitability"
```

```json
{
  "ticker": "AAPL",
  "period": "annual",
  "category": "profitability",
  "status": "success",
  "test_mode": true,
  "data": {
    "ratios": {
      "gross_profit_margin": 0.434,
      "operating_profit_margin": 0.297,
      "net_profit_margin": 0.254,
      "return_on_equity": 1.476,
      "return_on_assets": 0.287
    },
    "explanations": {
      "gross_profit_margin": "Measures the percentage of revenue retained after cost of goods sold",
      "net_profit_margin": "Shows the percentage of revenue that becomes profit"
    },
    "benchmarks": {
      "gross_profit_margin": {"industry_avg": 0.35, "performance": "above_average"},
      "net_profit_margin": {"industry_avg": 0.21, "performance": "excellent"}
    },
    "scores": {
      "profitability_score": 8.5,
      "overall_score": 8.2
    }
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Financial Overview Response
```bash
curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financial/overview/AAPL"
```

```json
{
  "ticker": "AAPL",
  "status": "success",
  "data": {
    "company_info": {
      "name": "Apple Inc.",
      "sector": "Technology",
      "market_cap": 2850000000000
    },
    "latest_financials": {
      "income_statement": {
        "fiscal_year": 2023,
        "total_revenue": 394328000000,
        "gross_profit": 169148000000,
        "operating_income": 114301000000,
        "net_income": 96995000000
      },
      "balance_sheet": {
        "fiscal_year": 2023,
        "total_assets": 352755000000,
        "total_liabilities": 290437000000,
        "shareholders_equity": 62318000000
      }
    },
    "key_ratios": {
      "profitability": {
        "gross_margin": 0.429,
        "operating_margin": 0.290,
        "net_margin": 0.246
      }
    },
    "trend_analysis": {
      "revenue_trend": "increasing",
      "growth_rate_3y": 0.078,
      "profitability_trend": "stable"
    },
    "summary": {
      "revenue_trend": "increasing",
      "profitability_score": 8.5,
      "data_quality": 0.95
    }
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Getting Started Guide

### Quick Test (No Authentication)
Try these commands to test the API immediately:

```bash
# 1. Test if the API is running
curl "http://localhost:8000/api/v1/financial/test/company/AAPL"

# 2. Get profitability ratios for Apple
curl "http://localhost:8000/api/v1/financial/test/ratios/AAPL?ratio_category=profitability"

# 3. Get complete financial overview for Microsoft
curl "http://localhost:8000/api/v1/financial/test/overview/MSFT"
```

### Generate Your API Key
```bash
# Run the key generator
python create_api_key.py

# Select a plan (or press Enter for Pro)
# Copy the generated API key (format: yk_xxxxxxxxxxxxx)
```

### Use Authenticated Endpoints
```bash
# Replace YOUR_API_KEY with the actual key from the generator
export API_KEY="yk_your_generated_api_key_here"

# Get company information
curl -H "Authorization: Bearer $API_KEY" \
     "http://localhost:8000/api/v1/financial/company/AAPL"

# Get financial statements
curl -H "Authorization: Bearer $API_KEY" \
     "http://localhost:8000/api/v1/financial/statements/AAPL?statement_type=income&period=annual&limit=3"

# Get financial ratios
curl -H "Authorization: Bearer $API_KEY" \
     "http://localhost:8000/api/v1/financial/ratios/AAPL?ratio_category=profitability"

# Get comprehensive analysis (Pro+ feature)
curl -H "Authorization: Bearer $API_KEY" \
     "http://localhost:8000/api/v1/financial/analysis/AAPL?analysis_type=comprehensive"
```

### Common Use Cases

#### 1. Financial Dashboard Data
```bash
# Get all key metrics for a stock dashboard
curl -H "Authorization: Bearer $API_KEY" \
     "http://localhost:8000/api/v1/financial/overview/AAPL"
```

#### 2. Portfolio Analysis
```bash
# Analyze multiple stocks
for ticker in AAPL MSFT GOOGL AMZN; do
  echo "Analyzing $ticker..."
  curl -H "Authorization: Bearer $API_KEY" \
       "http://localhost:8000/api/v1/financial/ratios/$ticker?ratio_category=profitability"
done
```

#### 3. Sector Comparison
```bash
# Compare tech companies
curl -H "Authorization: Bearer $API_KEY" \
     "http://localhost:8000/api/v1/financial/ratios/AAPL?ratio_category=all"
curl -H "Authorization: Bearer $API_KEY" \
     "http://localhost:8000/api/v1/financial/ratios/MSFT?ratio_category=all"
```

## Pro Tips

1. **Use Test Endpoints First**: Always test with the `/test/` endpoints before implementing authentication
2. **Cache Results**: The API includes confidence scores - cache high-confidence data locally
3. **Rate Limits**: Check your plan's rate limits and implement appropriate request throttling
4. **Error Handling**: All endpoints return standardized error formats with helpful messages
5. **Data Quality**: Check the `confidence_score` field to assess data reliability

## Development

### Project Structure
```
app/
├── core/           # Core configuration and security
├── api/            # API endpoints and routers
├── models/         # Database models
├── schemas/        # Pydantic schemas
├── services/       # Business logic services
├── utils/          # Utility functions
└── tests/          # Test suites
```

### Running Tests
```bash
pytest app/tests/ -v
```

### Code Quality
```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

## Data Sources

- **Alpha Vantage**: Real-time quotes and fundamentals
- **Financial Modeling Prep**: Financial statements and ratios
- **Yahoo Finance**: Market data and prices
- **FRED API**: Economic indicators

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔧 Troubleshooting

### Common Issues

#### 1. 401 Unauthorized Error
```bash
# Error: {"detail": "Invalid API key or expired"}
# Solution: Generate a new API key
python create_api_key.py
```

#### 2. 404 Ticker Not Found
```bash
# Error: {"detail": "Ticker 'XYZ' not found"}
# Solution: Verify ticker symbol or try a different data source
curl "http://localhost:8000/api/v1/financial/test/company/AAPL"  # Test with known ticker
```

#### 3. 503 Data Source Unavailable
```bash
# Error: {"detail": "Data source temporarily unavailable"}
# Solution: Check your API keys in .env file
# Verify Alpha Vantage API key is valid and has remaining quota
```

#### 4. Rate Limit Exceeded
```bash
# Error: {"detail": "Rate limit exceeded"}
# Solution: Wait for rate limit reset or upgrade plan
# Check your current plan limits with:
python create_api_key.py  # Shows rate limits for each plan
```

### Health Check
```bash
# Check if the API is running
curl "http://localhost:8000/health"

# Test with sample data
curl "http://localhost:8000/api/v1/financial/test/company/AAPL"
```

### API Documentation
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc Format**: `http://localhost:8000/redoc`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

## Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **GitHub**: [Yieldflow API Repository](https://github.com/flowistic-ai/Yieldflow_API)
- **Issues**: [Report Issues](https://github.com/flowistic-ai/Yieldflow_API/issues)

---

**Yieldflow API** - Transforming financial data into actionable insights. 
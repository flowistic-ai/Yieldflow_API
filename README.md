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

### 🎯 Core Value Proposition
- **Intelligent Analysis**: Beyond raw data - get insights, trends, and recommendations
- **Categorized Analytics**: Profitability, Risk, Efficiency, Growth, and Liquidity analysis
- **Ready-to-use Ratios**: 50+ financial ratios with explanations and benchmarks
- **Chart Generation**: Beautiful visualizations with base64-encoded images
- **European Focus**: Multi-currency support and regulatory compliance

### 🚀 Technical Features
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

### Authentication

All API requests require an API key in the header:

```bash
curl -H "X-API-KEY: your_api_key" \
     "http://localhost:8000/api/v1/financials/income-statements?ticker=AAPL"
```

### Core Endpoints

#### 1. Financial Statements
```bash
# Income Statements with Analytics
GET /api/v1/financials/income-statements?ticker=AAPL&period=annual&limit=4

# Balance Sheets with Liquidity Analysis
GET /api/v1/financials/balance-sheets?ticker=AAPL

# Cash Flow with Quality Analysis
GET /api/v1/financials/cash-flows?ticker=AAPL
```

#### 2. Analytics Endpoints
```bash
# Profitability Analysis
GET /api/v1/analytics/profitability/AAPL

# Risk Assessment
GET /api/v1/analytics/risk/AAPL

# Efficiency Analysis
GET /api/v1/analytics/efficiency/AAPL

# Growth Analysis
GET /api/v1/analytics/growth/AAPL

# Liquidity Analysis
GET /api/v1/analytics/liquidity/AAPL
```

#### 3. Financial Ratios
```bash
# All Ratios Categorized
GET /api/v1/ratios/AAPL

# Specific Category
GET /api/v1/ratios/category/profitability/AAPL
```

#### 4. Charts and Visualizations
```bash
# Financial Overview Chart
GET /api/v1/charts/financial-overview/AAPL

# Ratio Comparison Chart
GET /api/v1/charts/ratio-comparison/AAPL
```

#### 5. AI Insights
```bash
# AI-powered Analysis
GET /api/v1/insights/AAPL

# Peer Comparison
GET /api/v1/insights/peer-comparison/AAPL
```

#### 6. Compliance
```bash
# MiFID II Compliance
GET /api/v1/compliance/mifid/AAPL

# ESG Analysis
GET /api/v1/compliance/esg/AAPL
```

## Response Examples

### Enhanced Financial Data Response
```json
{
  "income_statements": [...],
  "analysis_summary": {
    "revenue_trend": "increasing",
    "profit_margin_trend": "stable",
    "growth_rate_3y": 0.156
  },
  "key_ratios": {
    "gross_margin": 0.42,
    "operating_margin": 0.18,
    "net_margin": 0.15
  }
}
```

### Analytics Response
```json
{
  "ticker": "AAPL",
  "profitability_score": 8.5,
  "category": "excellent",
  "metrics": {
    "gross_margin": 0.42,
    "net_margin": 0.20,
    "roe": 0.28
  },
  "peer_comparison": {
    "industry_avg_net_margin": 0.15,
    "percentile_ranking": 85
  },
  "insights": [
    "Margins consistently above industry average"
  ]
}
```

## API Plans

| Feature | Free | Basic | Pro | Enterprise |
|---------|------|-------|-----|------------|
| Daily Requests | 100 | 1,000 | 10,000 | Unlimited |
| Rate Limit/min | 10 | 60 | 300 | 1,000 |
| Basic Financials | ✅ | ✅ | ✅ | ✅ |
| Analytics | ❌ | ✅ | ✅ | ✅ |
| AI Insights | ❌ | ❌ | ✅ | ✅ |
| Charts | ❌ | ✅ | ✅ | ✅ |
| Compliance | ❌ | ❌ | ✅ | ✅ |

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

## Support

- **Documentation**: [API Docs](http://localhost:8000/api/v1/docs)
- **Issues**: [GitHub Issues](https://github.com/your-org/yieldflow-api/issues)
- **Contact**: support@yieldflow.com

---

**Yieldflow API** - Transforming financial data into actionable insights. 
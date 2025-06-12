# Yieldflow API

**Comprehensive Financial Analytics API** - Professional-grade financial data analysis with advanced ratio calculations, AI insights, and regulatory compliance features.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-6+-red.svg)](https://redis.io/)

## Overview

Yieldflow API is a comprehensive financial analytics platform that provides intelligent financial analysis beyond raw data. Built with FastAPI and designed for financial professionals, it offers multi-source data integration, advanced ratio calculations, and AI-powered insights with European regulatory compliance.

## Key Features

### Core Analytics
- **Financial Statements**: Complete income statements, balance sheets, and cash flow statements
- **Advanced Ratios**: 50+ financial ratios with automated calculations and trend analysis
- **AI Insights**: Machine learning-powered analysis and recommendations
- **Chart Generation**: Built-in visualization with multiple chart types
- **Multi-Source Data**: Integration with Alpha Vantage, Financial Modeling Prep, and Yahoo Finance

### Enterprise Features
- **Rate Limiting**: Tiered access plans with intelligent throttling
- **Data Quality**: Cross-validation and confidence scoring across multiple sources
- **Caching**: Redis-powered caching for optimal performance
- **Compliance**: MiFID II and CSRD compliance features
- **Monitoring**: Comprehensive logging and error tracking

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- API keys for external data sources

### Installation

1. **Clone and setup**
```bash
git clone https://github.com/flowistic-ai/Yieldflow_API.git
cd yieldflow-api
```

2. **Environment setup (uv recommended)**
```bash
# Using uv (recommended for development)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync

# Or using pip (traditional)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Database setup**
```bash
# PostgreSQL
createdb yieldflow_db

# Redis (start service)
redis-server
```

5. **Run migrations**
```bash
alembic upgrade head
```

6. **Start the application**
```bash
# Using uv (faster)
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Or using traditional method
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Access Points:**
- API Server: `http://localhost:8000`
- Documentation: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Authentication & API Keys

### Generating API Keys

Use the provided script to generate API keys for different access levels:

```bash
python create_api_key.py
```

**Available Plans:**
- **Free**: 1K requests/day, 10/min - Basic financial data
- **Basic**: 10K requests/day, 60/min - Financial ratios and analysis
- **Pro**: 50K requests/day, 300/min - Advanced analytics and insights
- **Enterprise**: 200K requests/day, 1000/min - Full features and bulk access

The script generates:
- API key (format: `yk_xxxxxxxxxxxxx`)
- User credentials and plan details
- Rate limits and feature access
- Usage examples

### Using API Keys

Include the API key in the Authorization header for all authenticated requests:

```bash
curl -H "Authorization: Bearer your_api_key_here" \
     "http://localhost:8000/api/v1/financials/income-statements?ticker=AAPL"
```

## API Endpoints

### Financial Statements

#### Income Statements
```bash
GET /api/v1/financials/income-statements?ticker={ticker}&period={period}&limit={limit}

curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financials/income-statements?ticker=AAPL&period=annual&limit=4"
```

#### Balance Sheets
```bash
GET /api/v1/financials/balance-sheets?ticker={ticker}&period={period}&limit={limit}

curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financials/balance-sheets?ticker=AAPL&period=annual&limit=4"
```

#### Cash Flow Statements
```bash
GET /api/v1/financials/cash-flows?ticker={ticker}&period={period}&limit={limit}

curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/financials/cash-flows?ticker=AAPL&period=annual&limit=4"
```

**Parameters:**
- `ticker`: Stock symbol (e.g., AAPL, MSFT)
- `period`: `annual` or `quarterly`
- `limit`: Number of periods to retrieve (1-10)

### Financial Ratios

#### Calculate All Ratios
```bash
GET /api/v1/ratios/calculate/{ticker}?period={period}&limit={limit}

curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/ratios/calculate/AAPL?period=annual&limit=4"
```

**Available Ratio Categories:**
- Profitability ratios (ROE, ROA, margins)
- Liquidity ratios (current, quick, cash ratios)
- Leverage ratios (debt-to-equity, interest coverage)
- Efficiency ratios (asset turnover, inventory turnover)
- Valuation ratios (P/E, P/B, EV/EBITDA)

### Charts & Visualizations

#### Generate Financial Charts
```bash
GET /api/v1/charts/generate/{ticker}?chart_type={type}&metric={metric}&period={period}&limit={limit}

curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/charts/generate/AAPL?chart_type=line&metric=revenue&period=annual&limit=4"
```

**Chart Types:**
- `line`: Line charts for trends
- `bar`: Bar charts for comparisons
- `area`: Area charts for cumulative data

**Available Metrics:**
- `revenue`, `profit`, `assets`, `equity`, `cash_flow`

### AI Insights

#### Comprehensive Analysis
```bash
GET /api/v1/insights/analyze/{ticker}?period={period}&limit={limit}&analysis_type={type}

curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/insights/analyze/AAPL?analysis_type=comprehensive&period=annual&limit=4"
```

**Analysis Types:**
- `comprehensive`: Complete financial analysis
- `profitability`: Focus on profit metrics
- `liquidity`: Liquidity and cash analysis
- `growth`: Growth trend analysis

### Compliance & ESG

#### ESG Analysis
```bash
GET /api/v1/compliance/esg/{ticker}?period={period}&limit={limit}

curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/compliance/esg/AAPL?period=annual&limit=4"
```

### Authentication

#### Generate New API Key
```bash
POST /api/v1/auth/api-key

curl -X POST "http://localhost:8000/api/v1/auth/api-key" \
     -H "Content-Type: application/json" \
     -d '{"plan": "pro"}'
```

#### Validate API Key
```bash
GET /api/v1/auth/validate

curl -H "Authorization: Bearer your_api_key" \
     "http://localhost:8000/api/v1/auth/validate"
```

## Response Format

All endpoints return standardized JSON responses:

```json
{
  "status": "success",
  "data": {
    "ticker": "AAPL",
    "period": "annual",
    "statements": [
      {
        "fiscal_year": 2023,
        "total_revenue": 394328000000,
        "net_income": 96995000000,
        "confidence_score": 0.95
      }
    ]
  },
  "metadata": {
    "source": "alpha_vantage",
    "cache_hit": false,
    "processing_time": 0.245
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "TICKER_NOT_FOUND",
    "message": "Ticker 'XYZ' not found or not supported",
    "details": "Please verify the ticker symbol"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Environment Configuration

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/yieldflow_db
REDIS_URL=redis://localhost:6379/0

# External API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FMP_API_KEY=your_fmp_key
POLYGON_API_KEY=your_polygon_key
TWELVEDATA_API_KEY=your_twelvedata_key

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ALGORITHM=HS256

# Cache Settings
CACHE_TTL=3600
ENABLE_RATE_LIMITING=true
```

## Development

### Project Structure
```
app/
├── core/                  # Core configuration and dependencies
│   ├── config.py         # Settings and environment variables
│   ├── database.py       # Database connection and models
│   ├── security.py       # Authentication and security
│   └── deps.py           # FastAPI dependencies
├── api/                  # API layer
│   └── api_v1/
│       ├── endpoints/    # API endpoint definitions
│       └── api.py        # Router configuration
├── models/               # Database models
├── schemas/              # Pydantic response/request schemas
├── services/             # Business logic
│   ├── data_provider.py  # Multi-source data integration
│   ├── ratio_calculator.py # Financial ratio calculations
│   ├── financial_analyzer.py # Analysis engine
│   └── chart_generator.py # Visualization service
└── utils/                # Utility functions
```

### Adding Dependencies

**Using uv (recommended):**
```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update requirements.txt for compatibility
uv pip compile pyproject.toml -o requirements.txt
```

**Using pip (traditional):**
```bash
pip install package-name
pip freeze > requirements.txt
```

### Running Tests
```bash
pytest app/tests/ -v --cov=app
```

### Code Quality
```bash
# Format and lint
black app/
isort app/
flake8 app/
mypy app/
```

## Data Sources

The API integrates multiple financial data sources for comprehensive coverage:

- **Alpha Vantage**: Real-time quotes and fundamental data
- **Financial Modeling Prep**: Detailed financial statements
- **Yahoo Finance**: Market data and historical prices
- **Polygon.io**: Real-time market data (Enterprise)
- **TwelveData**: Global market coverage (Enterprise)

### Data Quality Features

- **Cross-validation**: Multiple source verification
- **Confidence scoring**: Data reliability assessment
- **Automatic fallback**: Seamless source switching
- **Error handling**: Graceful degradation

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t yieldflow-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e ALPHA_VANTAGE_API_KEY=your_key \
  yieldflow-api
```

### Production Considerations

- Use PostgreSQL with connection pooling
- Configure Redis for production workloads
- Implement reverse proxy (nginx/traefik)
- Set up monitoring and logging
- Configure rate limiting per plan
- Use SSL/TLS certificates

## Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Error: "Invalid API key"
# Solution: Generate new API key
python create_api_key.py
```

#### Data Source Errors
```bash
# Error: "Data source unavailable"
# Check API keys in .env file
# Verify external API quotas
```

#### Rate Limit Exceeded
```bash
# Error: "Rate limit exceeded"
# Wait for reset or upgrade plan
# Check current limits in API key details
```

### Health Checks
```bash
# API health
curl "http://localhost:8000/health"

# Financial data health
curl "http://localhost:8000/api/v1/financials/health"

# Analytics health
curl "http://localhost:8000/api/v1/analytics/health"
```

## Performance Optimization

- **Caching**: Redis caching with configurable TTL
- **Async Operations**: Full async/await implementation
- **Connection Pooling**: Database connection optimization
- **Data Compression**: Gzip compression for large responses
- **Query Optimization**: Efficient database queries

## Security Features

- **API Key Authentication**: Secure token-based access
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses
- **Logging**: Comprehensive audit trails

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format code (`black app/ && isort app/`)
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [API Documentation](http://localhost:8000/api/v1/docs)
- **Repository**: [GitHub](https://github.com/flowistic-ai/Yieldflow_API)
- **Issues**: [Report Issues](https://github.com/flowistic-ai/Yieldflow_API/issues)

---

**Yieldflow API** - Professional financial analytics for modern applications. 
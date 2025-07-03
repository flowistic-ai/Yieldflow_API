# Yieldflow API

**Professional Financial Analytics Platform** - Comprehensive dividend analysis with real-time data, advanced metrics, and beautiful visualizations.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19+-blue.svg)](https://reactjs.org/)

## Overview

Yieldflow API provides intelligent dividend analysis that goes beyond raw data to deliver actionable insights. Built with FastAPI backend and React frontend, it offers comprehensive dividend analytics, growth tracking, risk assessment, and sustainability analysis.

**Key Features:**
- 📊 **Comprehensive Dividend Analysis** - Current yield, growth trends, sustainability metrics
- 📈 **Advanced Charts** - Growth tracking, peer comparison, total return analysis  
- 🔍 **Risk Assessment** - Dividend quality scoring and sustainability analysis
- 🎯 **Real-time Data** - Multi-source integration (Yahoo Finance, Alpha Vantage, FMP)
- 🚀 **Professional UI** - Modern React frontend with Material-UI components

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL (optional - uses SQLite by default)
- Redis (optional - for caching)

### 🚀 Docker Quick Start (zero-install)

```bash
# Spin up API (FastAPI) and its dependencies
docker compose up --build

# —or— build/run the backend image yourself
docker build -t yieldflow-api .
docker run -p 8000:8000 yieldflow-api
```

The Docker image installs Python packages with the ultra-fast [uv](https://github.com/astral-sh/uv) resolver, so image builds finish 2-3× quicker than traditional `pip`.

### 1. Clone Repository
```bash
git clone https://github.com/flowistic-ai/Yieldflow_API.git
cd Yieldflow_API
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Preferred: fast & reproducible via uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv pip install -r requirements-uv.txt --system

# (Optional) traditional fallback
# pip install -r requirements.txt

3. **Environment configuration**
```bash
cp env.example .env
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

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will run on:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd yieldflow-frontend

# Install dependencies
npm install

# Start development server
npm start
```

**Frontend will run on:** `http://localhost:3000`

### 4. Access the Application

1. **Frontend:** Open `http://localhost:3000` in your browser
2. **Backend API:** Access `http://localhost:8000/docs` for API documentation
3. **Test with:** Enter a stock ticker (e.g., AAPL, MSFT, JNJ) in the frontend

## Environment Configuration

Create a `.env` file in the root directory:

```bash
# Database (optional - uses SQLite by default)
DATABASE_URL=postgresql://user:password@localhost/yieldflow_db

# External API Keys (get from respective providers)
ALPHA_VANTAGE_API_KEY=your_key_here
FMP_API_KEY=your_key_here
FRED_API_KEY=your_key_here

# Application Settings
DEBUG=True
SECRET_KEY=your-secret-key
```

## API Usage

### Quick Test (No Auth Required)
```bash
# Test endpoint
curl "http://localhost:8000/financial/test/company/AAPL"
```

### With API Key
```bash
# Generate API key first
python create_api_key.py

# Use the generated key
curl -H "X-API-Key: yk_your_generated_key" \
     "http://localhost:8000/api/v1/dividends/AAPL/current"
```

### Main Dividend Endpoints
- **Current Info:** `GET /api/v1/dividends/{ticker}/current`
- **Full Analysis:** `GET /api/v1/dividends/{ticker}/analysis`
- **Growth Chart:** `GET /api/v1/dividends/{ticker}/charts/growth`
- **History:** `GET /api/v1/dividends/{ticker}/history`

## Project Structure

```
yieldflow-API/
├── app/                    # FastAPI backend
│   ├── api/               # API routes
│   ├── core/              # Configuration & database
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── yieldflow-frontend/    # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   └── services/      # API services
│   └── public/
├── requirements-uv.txt    # Python deps (primary, used by uv)
├── uv.lock               # Locked versions for reproducible builds
├── requirements.txt       # Legacy dependency list
└── README.md             # This file
```

## Features

### Dividend Analysis
- **Current Metrics:** Yield, payout ratio, payment frequency
- **Growth Analysis:** Historical growth rates, consistency metrics
- **Sustainability:** Coverage ratios, risk assessment, quality scoring
- **Forecasting:** Future dividend predictions with confidence intervals

### Charts & Visualizations
- **Growth Charts:** Historical dividend payments over time
- **Peer Comparison:** Compare against industry peers
- **Total Return:** Price appreciation vs dividend contribution
- **Yield vs Price:** Identify value opportunities

### Risk Assessment
- **Quality Scoring:** Comprehensive dividend quality grades
- **Sustainability Analysis:** Payout ratios and coverage metrics
- **Risk Factors:** Identify potential dividend risks
- **Stress Testing:** Economic scenario analysis

## Deployment

### Production Backend
```bash
# Using production WSGI server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Production Frontend
```bash
cd yieldflow-frontend
npm run build
# Serve the build folder with your preferred web server
```

## Development

### Backend Development
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black app/
isort app/
```

### Frontend Development
```bash
cd yieldflow-frontend

# Start development server with hot reload
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Troubleshooting

### Common Issues

1. **Backend not starting:** Check if port 8000 is available
2. **Frontend API errors:** Ensure backend is running on port 8000
3. **Missing data:** API keys might be required for external data sources
4. **Database errors:** Make sure PostgreSQL is running (or use SQLite default)

### Support

For issues or questions:
- Check the [API documentation](http://localhost:8000/docs) when running
- Review the project structure and example usage above
- Ensure all prerequisites are installed correctly

## License

MIT License - see LICENSE file for details. 

# Yieldflow API - Render Deployment Guide

This guide will help you deploy the Yieldflow API to Render with PostgreSQL and Redis.

## 🚀 Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/flowistic-ai/Yieldflow_API)

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Fork or clone this repository
3. **API Keys**: Obtain the required API keys (see below)

## 🔑 Required API Keys

Before deployment, obtain these API keys:

| Service | Purpose | Get Key From |
|---------|---------|--------------|
| Alpha Vantage | Financial data | [alphavantage.co](https://www.alphavantage.co/support/#api-key) |
| Financial Modeling Prep | Alternative financial data | [financialmodelingprep.com](https://financialmodelingprep.com/developer/docs) |
| OpenAI | AI insights (optional) | [platform.openai.com](https://platform.openai.com/api-keys) |

## 🎯 Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository containing this code

2. **Configure Environment Variables**
   
   Render will automatically create the services based on `render.yaml`. You need to set these environment variables:

   ```bash
   # Required API Keys
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
   FMP_API_KEY=your_fmp_key
   
   # Optional but recommended
   OPENAI_API_KEY=your_openai_key
   
   # Auto-generated (don't set manually)
   SECRET_KEY=auto-generated-by-render
   DATABASE_URL=auto-populated-by-render
   REDIS_URL=auto-populated-by-render
   ```

3. **Deploy**
   - Click "Apply" to deploy all services
   - Wait for deployment to complete (5-10 minutes)

### Option 2: Manual Service Creation

If you prefer manual setup:

#### 1. Create PostgreSQL Database
- Service Type: PostgreSQL
- Name: `yieldflow-db`
- Database Name: `yieldflow_db`
- User: `yieldflow_user`

#### 2. Create Redis Cache
- Service Type: Redis
- Name: `yieldflow-redis`
- Plan: Starter

#### 3. Create Web Service
- Service Type: Web Service
- Name: `yieldflow-api`
- Environment: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🔧 Environment Configuration

Set these environment variables in your Render web service:

### Core Configuration
```env
# Application
PROJECT_NAME=Yieldflow API
VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# API Keys (Set these manually)
ALPHA_VANTAGE_API_KEY=your_actual_key
FMP_API_KEY=your_actual_key
OPENAI_API_KEY=your_actual_key

# Auto-populated by Render
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
SECRET_KEY=${SECRET_KEY}
```

### Optional Configuration
```env
# Rate Limiting
RATE_LIMIT_ENABLED=true

# Caching
ENABLE_CACHING=true
CACHE_TTL_HOT=300
CACHE_TTL_ANALYTICS=3600

# Features
ENABLE_COMPLIANCE_FEATURES=true
ENABLE_AI_INSIGHTS=true

# CORS (add your frontend domains)
BACKEND_CORS_ORIGINS=["https://yieldflow-api.onrender.com","https://your-frontend.com"]
```

## 🌐 Service URLs

After deployment, your services will be available at:

- **API**: `https://yieldflow-api.onrender.com`
- **Documentation**: `https://yieldflow-api.onrender.com/api/v1/docs`
- **Health Check**: `https://yieldflow-api.onrender.com/health`

## 📊 Testing Deployment

1. **Health Check**
   ```bash
   curl https://yieldflow-api.onrender.com/health
   ```

2. **Create API Key**
   ```bash
   curl -X POST https://yieldflow-api.onrender.com/api/v1/auth/api-key \
        -H "Content-Type: application/json" \
        -d '{"user_id": "test-user", "plan": "professional"}'
   ```

3. **Test Financial Data**
   ```bash
   curl "https://yieldflow-api.onrender.com/api/v1/financials/income-statements?ticker=AAPL" \
        -H "X-API-Key: your-generated-api-key"
   ```

## 🔍 Monitoring and Logs

### View Logs
- Go to Render Dashboard
- Select your `yieldflow-api` service
- Click "Logs" tab

### Key Metrics to Monitor
- Response times
- Error rates
- Database connections
- Cache hit rates
- API key usage

## 🛠 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```
   Solution: Check DATABASE_URL is properly set
   ```

2. **Redis Connection Failed**
   ```
   Solution: Verify REDIS_URL environment variable
   ```

3. **API Key Errors**
   ```
   Solution: Ensure API keys are set and valid
   ```

4. **CORS Errors**
   ```
   Solution: Add your frontend domain to BACKEND_CORS_ORIGINS
   ```

### Debug Mode
To enable debug mode temporarily:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🔄 Updates and Rollbacks

### Auto-Deploy
- Enabled by default for main branch
- Triggered on every push to GitHub

### Manual Deploy
- Go to Render Dashboard
- Select service
- Click "Manual Deploy"

### Rollback
- Go to "Events" tab
- Find previous successful deployment
- Click "Rollback"

## 💰 Cost Optimization

### Starter Plan Resources
- **Web Service**: $7/month
- **PostgreSQL**: $7/month  
- **Redis**: $7/month
- **Total**: ~$21/month

### Production Scaling
For higher traffic, consider:
- Upgrading to Standard plans
- Enabling horizontal scaling
- Using CDN for static assets

## 🔐 Security Best Practices

1. **Environment Variables**
   - Never commit API keys to Git
   - Use Render's environment variable encryption
   - Rotate keys regularly

2. **Database Security**
   - Enable connection SSL
   - Regular backups (included in Render)
   - Monitor access logs

3. **API Security**
   - Implement rate limiting
   - Use HTTPS only
   - Monitor unusual access patterns

## 📞 Support

For deployment issues:
1. Check [Render Documentation](https://render.com/docs)
2. Review application logs
3. Contact Render Support
4. File GitHub issues for application bugs

---

**🎉 Your Yieldflow API is now live on Render!**

Visit your API documentation at: `https://yieldflow-api.onrender.com/api/v1/docs` 
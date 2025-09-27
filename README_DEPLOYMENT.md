# 🚀 Deployment Guide for Voice Agent Demo

This guide provides comprehensive instructions for deploying your voice agent demo to production platforms, making it accessible to users worldwide.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Deployment Options](#-deployment-options)
- [Prerequisites](#-prerequisites)
- [Step-by-Step Deployment](#-step-by-step-deployment)
- [Environment Configuration](#-environment-configuration)
- [Testing & Validation](#-testing--validation)
- [Troubleshooting](#-troubleshooting)
- [Cost Estimation](#-cost-estimation)

## 🎯 Quick Start

### One-Click Deploy (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/cerebras-realtime-live-demo&env=DEEPGRAM_API_KEY,CEREBRAS_API_KEY,DAILY_API_KEY&envDescription=Required%20API%20keys%20for%20the%20voice%20agent&envLink=https://github.com/your-username/cerebras-realtime-live-demo#api-keys)

**What this does:**
- Deploys the frontend to Vercel
- Sets up environment variables
- Provides a public URL for your demo

**Limitations:**
- Text-only functionality (no WebRTC voice chat)
- No conversation persistence
- No MCP integrations

## 🏗️ Deployment Options

### Option 1: Frontend-Only (Quick Demo)
- **Platform**: Vercel
- **Features**: Text chat, basic AI responses
- **Setup Time**: 5 minutes
- **Cost**: Free tier available

### Option 2: Hybrid Deployment (Full Features)
- **Frontend**: Vercel
- **Backend**: Railway/Render/Fly.io
- **Database**: External service (PlanetScale/Supabase)
- **Features**: All features including WebRTC voice chat
- **Setup Time**: 15-30 minutes
- **Cost**: $5-25/month

### Option 3: Full Stack (Self-Hosted)
- **Platform**: VPS/Cloud Server
- **Features**: Complete control, all features
- **Setup Time**: 1-2 hours
- **Cost**: $10-50/month

## 🔑 Prerequisites

### Required API Keys

1. **Deepgram API Key** (Required)
   - Sign up: [Deepgram Console](https://console.deepgram.com/)
   - Used for: Speech-to-Text and Text-to-Speech
   - Cost: Pay-per-use (check current pricing)

2. **Cerebras API Key** (Required)
   - Sign up: [Cerebras Cloud](https://cloud.cerebras.ai/)
   - Used for: Large Language Model processing
   - Cost: Pay-per-use (check current pricing)

3. **Daily API Key** (Optional)
   - Sign up: [Daily Dashboard](https://dashboard.daily.co/)
   - Used for: WebRTC voice features
   - Cost: Free tier available

### Optional Integrations

4. **PayPal API Keys** (Optional)
   - Sign up: [PayPal Developer Dashboard](https://developer.paypal.com/)
   - Used for: MCP PayPal integration
   - Cost: Free for sandbox testing

## 🚀 Step-by-Step Deployment

### Frontend-Only Deployment (Vercel)

#### Step 1: Prepare Your Repository

```bash
# Fork or clone the repository
git clone https://github.com/your-username/cerebras-realtime-live-demo.git
cd cerebras-realtime-live-demo

# Ensure you're on the main branch
git checkout main
```

#### Step 2: Deploy to Vercel

1. **Connect to Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Build Settings**:
   - Framework Preset: `Vite`
   - Root Directory: `client`
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Add Environment Variables**:
   ```
   DEEPGRAM_API_KEY=your_deepgram_key_here
   CEREBRAS_API_KEY=your_cerebras_key_here
   DAILY_API_KEY=your_daily_key_here
   ```

4. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (2-3 minutes)
   - Get your public URL

#### Step 3: Test Your Deployment

1. Visit your Vercel URL
2. Check that the interface loads
3. Try sending a text message
4. Verify AI responses are working

### Hybrid Deployment (Full Features)

#### Step 1: Deploy Backend to Railway

1. **Connect to Railway**:
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"

2. **Configure Service**:
   - Select your repository
   - Root Directory: `server`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python sesame.py run --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**:
   ```
   DEEPGRAM_API_KEY=your_deepgram_key_here
   CEREBRAS_API_KEY=your_cerebras_key_here
   DAILY_API_KEY=your_daily_key_here
   DATABASE_URL=postgresql://user:pass@host:port/db
   WEBAPP_PORT=7860
   ```

4. **Add Database Service**:
   - In Railway dashboard, add PostgreSQL service
   - Copy the connection string
   - Update `DATABASE_URL` environment variable

5. **Deploy**:
   - Railway will automatically deploy
   - Note the generated URL (e.g., `https://your-app.railway.app`)

#### Step 2: Update Frontend Configuration

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add/Update:
   ```
   VITE_SERVER_URL=https://your-app.railway.app/api
   ```
3. Redeploy the frontend

#### Step 3: Test Full Integration

1. Visit your Vercel URL
2. Test text chat functionality
3. Test voice chat (if Daily API key is configured)
4. Verify conversation persistence

## ⚙️ Environment Configuration

### Frontend Environment Variables (Vercel)

```bash
# Required
DEEPGRAM_API_KEY=your_deepgram_key
CEREBRAS_API_KEY=your_cerebras_key
VITE_SERVER_URL=https://your-backend.railway.app/api

# Optional
DAILY_API_KEY=your_daily_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_ENVIRONMENT=SANDBOX
```

### Backend Environment Variables (Railway)

```bash
# Required
DEEPGRAM_API_KEY=your_deepgram_key
CEREBRAS_API_KEY=your_cerebras_key
DATABASE_URL=postgresql://user:pass@host:port/db

# Optional
DAILY_API_KEY=your_daily_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_ENVIRONMENT=SANDBOX

# MCP Configuration
MCP_FILESYSTEM_ENABLED=false
MCP_PAYPAL_SANDBOX_ENABLED=true
MCP_DATABASE_ENABLED=false
MCP_WEATHER_ENABLED=false
MCP_CALENDAR_ENABLED=false

# Application Settings
WEBAPP_PORT=7860
WEBAPP_LOG_LEVEL=INFO
BOT_LOG_LEVEL=INFO
BOT_MAX_VOICE_SESSION_TIME=900
```

## 🧪 Testing & Validation

### 1. Frontend Tests

```bash
# Test locally
cd client
npm run dev
# Visit http://localhost:5173

# Test build
npm run build
npm run preview
```

### 2. Backend Tests

```bash
# Test locally
cd server
python sesame.py run
# Visit http://localhost:7860

# Test API endpoints
curl http://localhost:7860/
curl http://localhost:7860/docs
```

### 3. Integration Tests

```bash
# Run integration tests
python test_integration.py
```

### 4. Production Tests

1. **Frontend**:
   - Visit your Vercel URL
   - Check console for errors
   - Test all UI components

2. **Backend**:
   - Visit `https://your-backend.railway.app/`
   - Check API docs at `/docs`
   - Test API endpoints

3. **Integration**:
   - Send test messages
   - Verify responses
   - Check database persistence

## 🚨 Troubleshooting

### Common Issues

#### Frontend Issues

**Build fails on Vercel**:
```bash
# Check build logs in Vercel dashboard
# Common fixes:
# 1. Ensure all dependencies are in package.json
# 2. Check for TypeScript errors
# 3. Verify environment variables are set
```

**Environment variables not loading**:
```bash
# Ensure variables start with VITE_ for client-side access
# Check Vercel dashboard → Settings → Environment Variables
# Redeploy after adding variables
```

#### Backend Issues

**Railway deployment fails**:
```bash
# Check Railway logs
# Common fixes:
# 1. Ensure requirements.txt is in server directory
# 2. Check Python version compatibility
# 3. Verify all environment variables are set
```

**Database connection errors**:
```bash
# Check DATABASE_URL format
# Ensure PostgreSQL service is running
# Verify connection string is correct
```

#### Integration Issues

**CORS errors**:
```bash
# Check backend CORS configuration
# Ensure frontend URL is allowed
# Verify VITE_SERVER_URL is correct
```

**API key errors**:
```bash
# Verify API keys are valid
# Check API quotas and limits
# Ensure no extra spaces in environment variables
```

### Debug Commands

```bash
# Check environment variables
echo $DEEPGRAM_API_KEY
echo $CEREBRAS_API_KEY

# Test API keys
curl -H "Authorization: Token $DEEPGRAM_API_KEY" https://api.deepgram.com/v1/projects

# Check backend health
curl https://your-backend.railway.app/

# View logs
# Vercel: Dashboard → Functions → View Function Logs
# Railway: Dashboard → Deployments → View Logs
```

## 💰 Cost Estimation

### Vercel (Frontend)
- **Hobby Plan**: Free
  - 100GB bandwidth/month
  - Unlimited personal projects
  - Custom domains
- **Pro Plan**: $20/month
  - 1TB bandwidth/month
  - Team collaboration
  - Advanced analytics

### Railway (Backend)
- **Starter Plan**: $5/month
  - 512MB RAM
  - 1GB storage
  - $5 credit included
- **Developer Plan**: $20/month
  - 8GB RAM
  - 100GB storage
  - $20 credit included

### API Costs (Estimated)
- **Deepgram**: $0.0043 per minute of audio
- **Cerebras**: Varies by model and usage
- **Daily**: Free tier available

### Total Monthly Cost
- **Basic Setup**: $0-5 (using free tiers)
- **Full Features**: $25-45 (with paid plans)
- **High Usage**: $50+ (depending on API usage)

## 🎉 Success!

Once deployed, your voice agent demo will be accessible to users worldwide. Share the Vercel URL and let users experience the power of real-time voice AI with MCP integrations!

### Next Steps

1. **Share Your Demo**: Post the URL on social media, forums, or communities
2. **Gather Feedback**: Collect user feedback to improve the experience
3. **Monitor Usage**: Track API usage and costs
4. **Iterate**: Make improvements based on user feedback
5. **Scale**: Consider upgrading plans as usage grows

## 📞 Support

- **Documentation**: Check the main README.md
- **Issues**: Create GitHub issues for bugs
- **Community**: Join our Discord/community channels
- **API Support**: Contact respective API providers for service issues

---

**Happy Deploying! 🚀**

Your voice agent demo is now ready to showcase the future of conversational AI!

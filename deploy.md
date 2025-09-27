# Deployment Guide

This guide provides step-by-step instructions for deploying the Voice Agent Demo to production.

## 🚀 Quick Deploy Options

### Option 1: One-Click Deploy (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/cerebras-realtime-live-demo&env=DEEPGRAM_API_KEY,CEREBRAS_API_KEY,DAILY_API_KEY&envDescription=Required%20API%20keys%20for%20the%20voice%20agent&envLink=https://github.com/your-username/cerebras-realtime-live-demo#api-keys)

### Option 2: Manual Deployment

## 📋 Prerequisites

### Required API Keys

1. **Deepgram API Key** (Required)
   - Sign up at [Deepgram Console](https://console.deepgram.com/)
   - Create a new API key
   - Used for Speech-to-Text and Text-to-Speech

2. **Cerebras API Key** (Required)
   - Sign up at [Cerebras Cloud](https://cloud.cerebras.ai/)
   - Create a new API key
   - Used for Large Language Model processing

3. **Daily API Key** (Optional)
   - Sign up at [Daily Dashboard](https://dashboard.daily.co/)
   - Create a new API key
   - Used for WebRTC voice features

### Optional Integrations

4. **PayPal API Keys** (Optional)
   - Sign up at [PayPal Developer Dashboard](https://developer.paypal.com/)
   - Create a new application
   - Get Client ID and Client Secret
   - Used for MCP PayPal integration

## 🎯 Deployment Strategies

### Strategy 1: Frontend-Only (Text Chat)

**Best for**: Quick demo, text-only functionality

**Steps**:
1. Deploy frontend to Vercel
2. Configure environment variables
3. Use external API services directly

**Limitations**:
- No WebRTC voice chat
- No conversation persistence
- No MCP integrations

### Strategy 2: Hybrid Deployment (Full Features)

**Best for**: Complete functionality with all features

**Steps**:
1. Deploy frontend to Vercel
2. Deploy backend to Railway/Render/Fly.io
3. Set up external database
4. Configure CORS and environment variables

## 🔧 Vercel Deployment (Frontend)

### Step 1: Prepare Repository

```bash
# Fork or clone the repository
git clone https://github.com/your-username/cerebras-realtime-live-demo.git
cd cerebras-realtime-live-demo
```

### Step 2: Deploy to Vercel

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
   DEEPGRAM_API_KEY=your_deepgram_key
   CEREBRAS_API_KEY=your_cerebras_key
   DAILY_API_KEY=your_daily_key
   VITE_SERVER_URL=https://your-backend.railway.app/api
   ```

4. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete

### Step 3: Configure Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

## 🚂 Railway Deployment (Backend)

### Step 1: Prepare Backend

```bash
# Ensure you're in the project root
cd cerebras-realtime-live-demo
```

### Step 2: Deploy to Railway

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
   DEEPGRAM_API_KEY=your_deepgram_key
   CEREBRAS_API_KEY=your_cerebras_key
   DAILY_API_KEY=your_daily_key
   DATABASE_URL=postgresql://user:pass@host:port/db
   WEBAPP_PORT=7860
   ```

4. **Deploy**:
   - Railway will automatically deploy
   - Note the generated URL (e.g., `https://your-app.railway.app`)

### Step 3: Update Frontend Configuration

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `VITE_SERVER_URL` to your Railway backend URL:
   ```
   VITE_SERVER_URL=https://your-app.railway.app/api
   ```
3. Redeploy the frontend

## 🗄️ Database Setup

### Option 1: Railway PostgreSQL (Recommended)

1. In Railway dashboard, add PostgreSQL service
2. Copy the connection string
3. Update `DATABASE_URL` environment variable

### Option 2: Supabase (Alternative)

1. Create account at [Supabase](https://supabase.com/)
2. Create new project
3. Get connection string from Settings → Database
4. Update `DATABASE_URL` environment variable

## 🔐 Environment Variables Reference

### Frontend (Vercel)

```bash
# Required
DEEPGRAM_API_KEY=your_deepgram_key
CEREBRAS_API_KEY=your_cerebras_key
VITE_SERVER_URL=https://your-backend.railway.app/api

# Optional
DAILY_API_KEY=your_daily_key
```

### Backend (Railway)

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
```

## 🧪 Testing Deployment

### 1. Test Frontend
- Visit your Vercel URL
- Check that the interface loads correctly
- Verify environment variables are loaded

### 2. Test Backend
- Visit `https://your-backend.railway.app/`
- Should see "Sesame is running"
- Check API docs at `https://your-backend.railway.app/docs`

### 3. Test Integration
- Try sending a text message
- Check browser network tab for API calls
- Verify responses are received

### 4. Test Voice Features (if enabled)
- Click "Real-Time Voice AI Agent"
- Grant microphone permissions
- Test voice input/output

## 🚨 Troubleshooting

### Common Issues

**Frontend not loading**:
- Check Vercel build logs
- Verify environment variables are set
- Ensure `VITE_SERVER_URL` points to correct backend

**Backend connection failed**:
- Check Railway deployment logs
- Verify all environment variables are set
- Test backend URL directly

**CORS errors**:
- Ensure backend has CORS configured for your frontend domain
- Check that `VITE_SERVER_URL` is correct

**API key errors**:
- Verify all required API keys are set
- Check API key validity in respective dashboards
- Ensure no extra spaces or quotes in environment variables

### Debug Commands

```bash
# Check environment variables
echo $DEEPGRAM_API_KEY
echo $CEREBRAS_API_KEY

# Test backend locally
cd server
python sesame.py run

# Test frontend locally
cd client
npm run dev
```

## 📊 Monitoring

### Vercel Analytics
- Enable Vercel Analytics in project settings
- Monitor page views and performance

### Railway Logs
- Check Railway dashboard for application logs
- Monitor resource usage and errors

### API Monitoring
- Monitor API usage in Deepgram/Cerebras dashboards
- Set up alerts for quota limits

## 🔄 Updates and Maintenance

### Updating the Application
1. Push changes to GitHub
2. Vercel will automatically redeploy frontend
3. Railway will automatically redeploy backend

### Environment Variable Updates
1. Update in respective dashboards
2. Redeploy services if needed

### Database Backups
- Railway PostgreSQL includes automatic backups
- Consider additional backup strategies for production

## 💰 Cost Estimation

### Vercel (Frontend)
- **Hobby Plan**: Free (100GB bandwidth)
- **Pro Plan**: $20/month (1TB bandwidth)

### Railway (Backend)
- **Starter Plan**: $5/month (512MB RAM)
- **Developer Plan**: $20/month (8GB RAM)

### API Costs
- **Deepgram**: Pay-per-use (check pricing)
- **Cerebras**: Pay-per-use (check pricing)
- **Daily**: Free tier available

## 🎉 Success!

Once deployed, your voice agent demo will be accessible to users worldwide. Share the Vercel URL and let users experience the power of real-time voice AI with MCP integrations!

## 📞 Support

- **Documentation**: Check the main README.md
- **Issues**: Create GitHub issues for bugs
- **Community**: Join our Discord/community channels
- **API Support**: Contact respective API providers for service issues

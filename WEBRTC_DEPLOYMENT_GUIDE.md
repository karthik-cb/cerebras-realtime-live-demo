# 🎯 WebRTC-Compatible Deployment Guide

This guide provides comprehensive instructions for deploying your voice agent demo to platforms that support WebRTC and long-running Python processes.

## 🚨 Why Not Vercel?

Vercel's serverless architecture has limitations for WebRTC applications:

- ❌ **No Persistent Connections**: WebRTC requires long-lived connections
- ❌ **Request Timeouts**: Serverless functions have execution time limits
- ❌ **No WebSocket Support**: Real-time communication needs persistent connections
- ❌ **Cold Starts**: Can cause latency issues for voice applications

## 🏆 Recommended Platforms

### 1. Railway (Recommended for Simplicity)

**Why Railway is Perfect:**
- ✅ Full WebRTC support with persistent connections
- ✅ Native Python/FastAPI support
- ✅ Built-in PostgreSQL database
- ✅ Automatic deployments from GitHub
- ✅ Daily.co integration works seamlessly

**Pricing**: $5/month starter, $20/month developer

**Deployment Steps:**
```bash
# 1. Connect Railway to your GitHub repo
# 2. Add PostgreSQL service
# 3. Set environment variables
# 4. Deploy automatically
```

### 2. Render (Great Balance)

**Why Render Works Well:**
- ✅ Supports long-running processes
- ✅ Built-in PostgreSQL
- ✅ Auto-deploy from Git
- ✅ Custom domains and SSL

**Pricing**: $7/month for web services

**Deployment Steps:**
```bash
# 1. Connect Render to your GitHub repo
# 2. Use render.yaml configuration
# 3. Set environment variables
# 4. Deploy both frontend and backend
```

### 3. Fly.io (Best for Global Performance)

**Why Fly.io is Excellent:**
- ✅ Optimized for real-time applications
- ✅ Global edge deployment
- ✅ Low-latency worldwide
- ✅ Docker-based deployment

**Pricing**: $1.94/month shared CPU

**Deployment Steps:**
```bash
# 1. Install Fly CLI
npm install -g @fly/flyctl

# 2. Login and create app
fly auth login
fly launch

# 3. Set secrets
fly secrets set DEEPGRAM_API_KEY=your_key
fly secrets set CEREBRAS_API_KEY=your_key
fly secrets set DAILY_API_KEY=your_key

# 4. Deploy
fly deploy
```

## 🚀 Quick Start: Railway Deployment

### Step 1: Prepare Your Repository

```bash
# Ensure your code is pushed to GitHub
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Deploy to Railway

1. **Go to Railway Dashboard**:
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Services**:
   - **Backend Service**: Root directory `server`
   - **PostgreSQL Database**: Add from Railway's database options
   - **Frontend Service**: Root directory `client` (optional, can use Vercel)

4. **Configure Environment Variables**:
   ```
   DEEPGRAM_API_KEY=your_deepgram_key
   CEREBRAS_API_KEY=your_cerebras_key
   DAILY_API_KEY=your_daily_key
   DATABASE_URL=postgresql://user:pass@host:port/db
   WEBAPP_PORT=7860
   ```

5. **Deploy**:
   - Railway automatically builds and deploys
   - Get your backend URL (e.g., `https://your-app.railway.app`)

### Step 3: Deploy Frontend (Optional)

**Option A: Deploy to Vercel (Hybrid)**
```bash
# 1. Go to Vercel Dashboard
# 2. Import your GitHub repo
# 3. Set root directory to "client"
# 4. Add environment variable:
VITE_SERVER_URL=https://your-app.railway.app/api
```

**Option B: Deploy to Railway (Full-Stack)**
```bash
# 1. Add another service in Railway
# 2. Root directory: "client"
# 3. Build command: "npm run build"
# 4. Start command: "npm run preview -- --host 0.0.0.0 --port $PORT"
```

## 🔧 Environment Variables Setup

### Required Variables

```bash
# API Keys (Required)
DEEPGRAM_API_KEY=your_deepgram_key_here
CEREBRAS_API_KEY=your_cerebras_key_here
DAILY_API_KEY=your_daily_key_here

# Database (Auto-configured on Railway/Render)
DATABASE_URL=postgresql://user:pass@host:port/db

# Application Settings
WEBAPP_PORT=7860
WEBAPP_LOG_LEVEL=INFO
BOT_LOG_LEVEL=INFO
BOT_MAX_VOICE_SESSION_TIME=900
```

### Optional Variables

```bash
# PayPal Integration
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_ENVIRONMENT=SANDBOX

# MCP Configuration
MCP_FILESYSTEM_ENABLED=false
MCP_PAYPAL_SANDBOX_ENABLED=true
MCP_DATABASE_ENABLED=false
MCP_WEATHER_ENABLED=false
MCP_CALENDAR_ENABLED=false
```

## 🧪 Testing WebRTC Deployment

### 1. Test Backend Health
```bash
# Check if backend is running
curl https://your-app.railway.app/
# Should return: "Sesame is running"

# Check API documentation
curl https://your-app.railway.app/docs
# Should return API documentation
```

### 2. Test Frontend Connection
```bash
# Visit your frontend URL
# Check browser console for connection errors
# Verify VITE_SERVER_URL is correct
```

### 3. Test WebRTC Voice Chat
1. Click "Real-Time Voice AI Agent"
2. Grant microphone permissions
3. Test voice input/output
4. Check for WebRTC connection logs

### 4. Test MCP Integrations
1. Try PayPal-related commands
2. Check server logs for MCP connections
3. Verify API responses

## 🚨 Troubleshooting WebRTC Issues

### Common WebRTC Problems

**Connection Failed**:
```bash
# Check Daily.co API key
# Verify WebRTC is enabled in browser
# Check network connectivity
# Review server logs for errors
```

**Audio Issues**:
```bash
# Check microphone permissions
# Verify audio device selection
# Test with different browsers
# Check browser console for errors
```

**Latency Issues**:
```bash
# Use Fly.io for global deployment
# Check network latency
# Optimize audio codec settings
# Monitor server performance
```

### Debug Commands

```bash
# Check environment variables
echo $DEEPGRAM_API_KEY
echo $CEREBRAS_API_KEY
echo $DAILY_API_KEY

# Test API connectivity
curl -H "Authorization: Token $DEEPGRAM_API_KEY" https://api.deepgram.com/v1/projects

# Check database connection
python -c "import os; print(os.getenv('DATABASE_URL'))"

# View application logs
# Railway: Dashboard → Deployments → View Logs
# Render: Dashboard → Services → View Logs
# Fly.io: fly logs
```

## 💰 Cost Comparison

### Railway
- **Starter**: $5/month (512MB RAM, 1GB storage)
- **Developer**: $20/month (8GB RAM, 100GB storage)
- **Database**: Included in plan

### Render
- **Web Service**: $7/month (512MB RAM)
- **Database**: $7/month (1GB storage)
- **Total**: ~$14/month

### Fly.io
- **Shared CPU**: $1.94/month (256MB RAM)
- **Dedicated CPU**: $5.50/month (256MB RAM)
- **Database**: External (PlanetScale, Supabase)

### Google Cloud Run
- **Pay-per-request**: ~$0-10/month (depending on usage)
- **Database**: Cloud SQL (additional cost)

## 🎯 Platform Recommendations

### For Beginners: Railway
- Easiest setup and management
- Built-in database
- Automatic deployments
- Great documentation

### For Performance: Fly.io
- Global edge deployment
- Lowest latency
- Docker-based
- Pay-as-you-scale

### For Enterprise: Google Cloud Run
- Enterprise-grade reliability
- Auto-scaling
- Full Google Cloud integration
- Advanced monitoring

### For Budget: Render
- Good balance of features and cost
- Built-in database
- Auto-deploy from Git
- Free tier available

## 🚀 Next Steps

1. **Choose Your Platform**: Based on your needs and budget
2. **Deploy Backend**: Follow platform-specific instructions
3. **Deploy Frontend**: Either to same platform or Vercel
4. **Configure Environment**: Set all required API keys
5. **Test WebRTC**: Verify voice chat functionality
6. **Monitor Performance**: Set up logging and monitoring
7. **Share Your Demo**: Get users to test the voice features!

## 📞 Support

- **Railway**: [Railway Documentation](https://docs.railway.app/)
- **Render**: [Render Documentation](https://render.com/docs)
- **Fly.io**: [Fly.io Documentation](https://fly.io/docs/)
- **Daily.co**: [Daily.co Documentation](https://docs.daily.co/)

---

**Your voice agent demo is now ready for real-time WebRTC communication! 🎉**

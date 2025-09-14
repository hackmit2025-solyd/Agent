# 🚀 Railway.app Deployment Guide

## Why Railway.app?
- ✅ **FREE** tier: 500 hours/month (perfect for ~100 runs)
- ✅ **Zero config** deployment
- ✅ **Automatic HTTPS** and custom domains
- ✅ **Built-in environment variables**
- ✅ **GitHub integration** (auto-deploy on push)
- ✅ **Docker support** (we created Dockerfile)

## 🚀 Quick Deploy (5 minutes)

### Step 1: Prepare Your Code
1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add Railway deployment config"
   git push origin main
   ```

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway will auto-detect the Dockerfile and deploy!

### Step 3: Set Environment Variables
In Railway dashboard, go to **Variables** tab and add:

```bash
# Claude API (Required)
CLAUDE_SECRET=your-claude-api-key-here

# UAgents Configuration (Optional - for online agents)
UAGENTS_SEED=your-seed-phrase-here
UAGENTS_ENDPOINT=https://agentverse.ai
UAGENTS_MAILBOX_KEY=your-mailbox-key-here

# Agentverse (Optional - for online connectivity)
AGENTVERSE_API_KEY=your-agentverse-api-key
AGENTVERSE_ENDPOINT=https://agentverse.ai

# Database (Optional - defaults to local)
DATABASE_SERVICE_URL=http://localhost:3000/api/query
DATABASE_SERVICE_API_KEY=your-api-key-here

# LiveKit (Optional - for voice features)
LIVEKIT_SERVER_URL=http://localhost:7880

# Port (Railway sets this automatically)
PORT=8080
```

### Step 4: Test Your Deployment
Your app will be available at: `https://your-app-name.railway.app`

Test endpoints:
- `GET /` - API documentation
- `GET /api/system-status` - Health check
- `POST /api/doctor-query` - Main functionality

## 🔧 Advanced Configuration

### Custom Domain (Optional)
1. In Railway dashboard → Settings → Domains
2. Add your custom domain
3. Update DNS records as shown

### Environment-Specific Settings
Create different environments:
- **Production**: `main` branch
- **Staging**: `develop` branch

### Monitoring
Railway provides:
- Real-time logs
- CPU/Memory usage
- Request metrics
- Error tracking

## 💰 Cost Breakdown
- **FREE Tier**: 500 hours/month
- **Your usage**: ~100 runs = ~10 hours/month
- **Cost**: $0/month ✅

## 🚨 Troubleshooting

### Common Issues:
1. **Build fails**: Check Dockerfile syntax
2. **App crashes**: Check environment variables
3. **Port issues**: Railway sets PORT automatically
4. **Memory issues**: Upgrade to paid plan if needed

### Debug Commands:
```bash
# Check logs
railway logs

# Connect to container
railway shell

# Check environment
railway variables
```

## 📊 Expected Performance
- **Cold start**: ~2-3 seconds
- **Warm requests**: ~200-500ms
- **Concurrent users**: 10-20 (free tier)
- **Uptime**: 99.9%

## 🎯 Next Steps After Deployment
1. Test all API endpoints
2. Set up monitoring alerts
3. Configure custom domain (optional)
4. Set up GitHub auto-deploy
5. Add database (if needed)

Your healthcare agent system will be live and accessible worldwide! 🌍

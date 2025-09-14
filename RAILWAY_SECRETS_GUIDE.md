# 🔐 Railway.app Secrets & Environment Variables Guide

## 🎯 **The Good News: It's Super Easy!**

Railway handles secrets securely and makes it very easy to manage environment variables. Here's exactly how to do it:

## 📋 **Step-by-Step Secret Management**

### **Step 1: Identify Your Required Secrets**

Based on your code, here are the secrets you need:

#### **🔴 REQUIRED (Must Have):**
```bash
CLAUDE_SECRET=your-claude-api-key-here
```

#### **🟡 OPTIONAL (Nice to Have):**
```bash
# For online agent connectivity
UAGENTS_SEED=your-seed-phrase-here
UAGENTS_MAILBOX_KEY=your-mailbox-key-here
AGENTVERSE_API_KEY=your-agentverse-api-key

# For database connectivity
DATABASE_SERVICE_URL=http://your-database-url
DATABASE_SERVICE_API_KEY=your-database-api-key

# For voice features
LIVEKIT_SERVER_URL=http://your-livekit-server
```

### **Step 2: Get Your Claude API Key**

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up/Login
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-...`)

### **Step 3: Set Secrets in Railway**

#### **Method 1: Railway Dashboard (Easiest)**
1. Go to your Railway project
2. Click on your service
3. Go to **"Variables"** tab
4. Click **"New Variable"**
5. Add each secret:
   - **Name**: `CLAUDE_SECRET`
   - **Value**: `sk-ant-your-actual-key-here`
6. Click **"Add"**

#### **Method 2: Railway CLI (Advanced)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Set variables
railway variables set CLAUDE_SECRET=sk-ant-your-key-here
railway variables set UAGENTS_SEED=your-seed-phrase
```

### **Step 4: Verify Your Setup**

Your app will automatically use these environment variables. Test with:

```bash
# Test your deployed app
curl https://your-app-name.railway.app/api/system-status
```

## 🔒 **Security Best Practices**

### **✅ DO:**
- Use Railway's built-in secret management
- Never commit secrets to Git
- Use different secrets for different environments
- Rotate secrets regularly

### **❌ DON'T:**
- Put secrets in your code
- Commit `.env` files to Git
- Share secrets in chat/email
- Use production secrets in development

## 🛠️ **Environment-Specific Configuration**

### **Development (Local)**
Create `.env` file:
```bash
CLAUDE_SECRET=sk-ant-your-dev-key
DEBUG=true
LOG_LEVEL=DEBUG
```

### **Production (Railway)**
Set in Railway dashboard:
```bash
CLAUDE_SECRET=sk-ant-your-prod-key
DEBUG=false
LOG_LEVEL=INFO
PORT=8080
```

## 🚨 **Troubleshooting Secrets**

### **Common Issues:**

1. **"Claude API key not found"**
   - Check if `CLAUDE_SECRET` is set in Railway
   - Verify the key is correct (starts with `sk-ant-`)
   - Redeploy after adding the variable

2. **"Environment variable not loading"**
   - Make sure variable name matches exactly
   - Check for typos in variable names
   - Restart the service after adding variables

3. **"Secret not working"**
   - Verify the API key is active
   - Check if you have sufficient credits
   - Test the key locally first

### **Debug Commands:**
```bash
# Check Railway logs
railway logs

# List all variables
railway variables

# Test locally with Railway variables
railway run python app.py
```

## 💡 **Pro Tips**

1. **Start Simple**: Deploy with just `CLAUDE_SECRET` first
2. **Add Gradually**: Add other secrets one by one
3. **Test Each Step**: Verify each secret works before adding the next
4. **Use Defaults**: Your app has sensible defaults for optional variables
5. **Monitor Usage**: Check Claude API usage to avoid unexpected charges

## 🎉 **You're All Set!**

Once you add `CLAUDE_SECRET` to Railway, your healthcare agent system will be fully functional in the cloud!

**Next Steps:**
1. Add `CLAUDE_SECRET` to Railway
2. Deploy your app
3. Test the endpoints
4. Add other secrets as needed

Your app will be live at: `https://your-app-name.railway.app` 🚀

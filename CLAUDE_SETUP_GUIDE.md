# 🤖 Claude API Setup Guide

## Current Status
✅ **System is working with mock data and mock responses**  
❌ **Claude API key not set - using fallback responses**

## Quick Setup (5 minutes)

### 1. Get Claude API Key
1. Visit: https://console.anthropic.com/
2. Sign up or log in
3. Go to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

### 2. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:CLAUDE_SECRET="your-actual-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set CLAUDE_SECRET=your-actual-api-key-here
```

**Linux/Mac:**
```bash
export CLAUDE_SECRET=your-actual-api-key-here
```

### 3. Restart Flask Server
```bash
python app.py
```

### 4. Test Real Claude
```bash
python test_real_claude.py
```

## What You'll Get with Real Claude

### Before (Mock Responses):
```
🤖 Agent: Hello John Smith! I'm your healthcare agent calling for a follow-up. How have you been feeling since your last visit?
🤖 Agent: Thank you for that information. Can you tell me more about how you've been managing your condition?
🤖 Agent: Thank you for that information. Can you tell me more about how you've been managing your condition?
```

### After (Real Claude):
```
🤖 Agent: Hello John! I'm calling from your healthcare team to check in on your diabetes management. I see you've been experiencing some vision concerns - how have those been affecting your daily activities?
🤖 Agent: I understand the vision issues are concerning. Are you still taking your Metformin as prescribed, and have you noticed any changes in your blood sugar levels recently?
🤖 Agent: Based on what you've shared, I think it would be best to schedule you for an eye exam within the next week. I'll also flag this for Dr. Smith to review your medication regimen. Does that sound good to you?
```

## System Components Status

### ✅ Working Components:
- **Flask API Server** (localhost:8080)
- **Mock Database Service** (localhost:3000)
- **Complete Healthcare Flow**
- **Sub-Agent Management**
- **Conversation API**

### 🔧 Needs Claude API Key:
- **Intelligent Query Parsing**
- **Smart Conversation Starters**
- **Context-Aware Responses**
- **Intelligent Termination Logic**
- **Medical Decision Making**

## API Endpoints

### Doctor Query Flow:
```bash
POST http://localhost:8080/api/doctor-query
{
  "doctor_query": "Follow up with all diabetic patients from last week who have been experiencing vision problems"
}
```

### Conversation Flow:
```bash
# Start conversation
POST http://localhost:8080/api/conversation/start
{
  "agent_id": "sub_agent_PAT001_1234567890"
}

# Respond to patient
POST http://localhost:8080/api/conversation/respond
{
  "agent_id": "sub_agent_PAT001_1234567890",
  "patient_message": "I've been having vision problems lately"
}
```

## Troubleshooting

### Issue: "401 Unauthorized" errors
**Solution:** Your Claude API key is invalid or not set
```bash
# Check if key is set
echo $env:CLAUDE_SECRET  # Windows
echo $CLAUDE_SECRET      # Linux/Mac
```

### Issue: "Claude Available: False"
**Solution:** Restart Flask server after setting environment variable
```bash
# Stop current server (Ctrl+C)
python app.py
```

### Issue: Still getting mock responses
**Solution:** Check API key format - should start with `sk-ant-`
```bash
# Test with real key
python test_real_claude.py
```

## Cost Information
- **Claude 3 Haiku**: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- **Typical conversation**: ~$0.001-0.01 per patient
- **Very cost-effective** for healthcare applications

## Next Steps
1. Set your Claude API key
2. Restart the Flask server
3. Run `python test_real_claude.py`
4. See intelligent, context-aware conversations!

---

**🎉 Once you set your Claude API key, you'll have a fully intelligent healthcare agent system!**
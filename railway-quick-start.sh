#!/bin/bash
# Railway.app Quick Deploy Script

echo "🚀 Railway.app Quick Deploy for Healthcare Agent System"
echo "======================================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit for Railway deployment"
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "🔗 Please add your GitHub remote:"
    echo "   git remote add origin https://github.com/yourusername/your-repo.git"
    echo "   git push -u origin main"
    echo ""
    echo "Then run this script again!"
    exit 1
fi

echo "✅ Git repository ready"
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Add Railway deployment configuration"
git push origin main

echo ""
echo "🎉 Code pushed to GitHub!"
echo ""
echo "Next steps:"
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub"
echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
echo "4. Select your repository"
echo "5. Add environment variables from railway-env.txt"
echo "6. Your app will be live at https://your-app-name.railway.app"
echo ""
echo "📋 Environment variables to set in Railway:"
echo "   - CLAUDE_SECRET (required)"
echo "   - Others are optional (see railway-env.txt)"
echo ""
echo "🔧 Test your deployment:"
echo "   curl https://your-app-name.railway.app/api/system-status"

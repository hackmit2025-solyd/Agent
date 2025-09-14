"""
Setup script to configure Claude API key for the healthcare agent system.
"""
import os
import sys

def setup_claude_api():
    """Setup Claude API key for the system."""
    print("🤖 Claude API Setup for Healthcare Agent System")
    print("=" * 50)
    
    print("\n1. 📋 Claude API Key Setup")
    print("-" * 30)
    print("To use real Claude responses, you need to:")
    print("1. Get a Claude API key from: https://console.anthropic.com/")
    print("2. Set the environment variable CLAUDE_SECRET")
    print("3. Or create a .env file with your API key")
    
    print("\n2. 🔧 Current Environment Status")
    print("-" * 30)
    
    # Check current environment
    claude_secret = os.getenv("CLAUDE_SECRET")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if claude_secret and claude_secret != "your-claude-api-key-here":
        print("✅ CLAUDE_SECRET is set")
    else:
        print("❌ CLAUDE_SECRET is not set")
    
    if anthropic_key and anthropic_key != "your-claude-api-key-here":
        print("✅ ANTHROPIC_API_KEY is set")
    else:
        print("❌ ANTHROPIC_API_KEY is not set")
    
    print("\n3. 🚀 Quick Setup Options")
    print("-" * 30)
    print("Option 1: Set environment variable (temporary)")
    print("  Windows: set CLAUDE_SECRET=your-actual-api-key")
    print("  Linux/Mac: export CLAUDE_SECRET=your-actual-api-key")
    
    print("\nOption 2: Create .env file (permanent)")
    print("  Create a .env file in the project root with:")
    print("  CLAUDE_SECRET=your-actual-api-key")
    print("  ANTHROPIC_API_KEY=your-actual-api-key")
    
    print("\n4. 🧪 Test Claude Integration")
    print("-" * 30)
    
    if claude_secret and claude_secret != "your-claude-api-key-here":
        print("✅ Ready to test Claude integration!")
        print("Run: python test_llm_direct.py")
    else:
        print("❌ Please set your Claude API key first")
        print("Then run: python test_llm_direct.py")
    
    print("\n5. 📊 Database Service Setup")
    print("-" * 30)
    print("The system also needs a database service running on localhost:3000")
    print("This is where patient data comes from")
    print("For now, the system uses mock data when database is unavailable")
    
    print("\n🎉 Setup Complete!")
    print("Once you set your Claude API key, the system will use real AI responses!")

if __name__ == "__main__":
    setup_claude_api()

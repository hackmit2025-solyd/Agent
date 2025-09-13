"""
Claude Setup Helper
Helps you set up Claude API integration for the healthcare agent system.
"""
import os
import sys


def setup_claude():
    """Guide user through Claude API setup."""
    print("🤖 Claude API Setup for Healthcare Agent System")
    print("=" * 60)
    
    print("\n📋 Step 1: Get Your Anthropic API Key")
    print("1. Go to: https://console.anthropic.com/")
    print("2. Sign up or log in to your account")
    print("3. Navigate to 'API Keys' section")
    print("4. Create a new API key")
    print("5. Copy the key (it starts with 'sk-ant-...')")
    
    print("\n📋 Step 2: Set Up Environment Variable")
    print("Choose one of these methods:")
    
    print("\nMethod A: Environment Variable (Recommended)")
    print("Windows:")
    print("  set ANTHROPIC_API_KEY=your_key_here")
    print("\nLinux/Mac:")
    print("  export ANTHROPIC_API_KEY=your_key_here")
    
    print("\nMethod B: .env File")
    print("1. Create a .env file in the project root")
    print("2. Add: ANTHROPIC_API_KEY=your_key_here")
    print("3. The system will automatically load it")
    
    print("\n📋 Step 3: Test Your Setup")
    print("Run: python test_claude_integration.py")
    
    # Check current status
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"\n🔍 Current Status:")
    if api_key:
        print(f"✅ ANTHROPIC_API_KEY is set: {api_key[:10]}...")
        print("🚀 You're ready to use Claude!")
    else:
        print("❌ ANTHROPIC_API_KEY not found")
        print("📝 Please follow the steps above to set it up")
    
    print(f"\n💡 What Claude Will Do:")
    print("• Parse complex doctor queries intelligently")
    print("• Generate realistic patient conversations")
    print("• Make smart decisions about follow-up actions")
    print("• Provide detailed medical reasoning")
    print("• Handle edge cases and complex scenarios")
    
    print(f"\n🎯 Example Queries Claude Can Handle:")
    examples = [
        "Follow up with all diabetic patients who had high blood sugar last week",
        "Check on patients with chest pain who are taking blood thinners",
        "Review all elderly patients with multiple medications for drug interactions",
        "Find patients with depression who haven't been seen in 2 months",
        "Schedule urgent appointments for patients with severe symptoms"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    
    print(f"\n🚀 Ready to test? Run: python test_claude_integration.py")


if __name__ == "__main__":
    setup_claude()

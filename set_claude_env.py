"""
Script to set Claude environment variable and test the system.
"""
import os
import sys

def set_claude_environment():
    """Set Claude environment variable and test the system."""
    print("🤖 Setting Claude Environment Variable")
    print("=" * 50)
    
    # Check if CLAUDE_SECRET is already set
    current_secret = os.getenv("CLAUDE_SECRET")
    if current_secret and current_secret != "your-claude-api-key-here":
        print(f"✅ CLAUDE_SECRET is already set: {current_secret[:10]}...")
        return True
    
    print("❌ CLAUDE_SECRET is not set")
    print("\n🔧 To set your Claude API key:")
    print("1. Get your API key from: https://console.anthropic.com/")
    print("2. Run one of these commands:")
    print("   Windows: set CLAUDE_SECRET=your-actual-api-key")
    print("   Linux/Mac: export CLAUDE_SECRET=your-actual-api-key")
    print("3. Then restart the Flask server: python app.py")
    
    # Try to set a test value (this won't work for real API calls)
    print("\n🧪 Setting test environment variable...")
    os.environ["CLAUDE_SECRET"] = "test-key-for-demo"
    print("✅ Test environment variable set")
    
    return False

def test_llm_service():
    """Test the LLM service with current environment."""
    print("\n🧪 Testing LLM Service")
    print("-" * 30)
    
    try:
        from services.llm_service import llm_service
        
        print(f"✅ LLM Service Available: {llm_service.available}")
        print(f"✅ Provider: {llm_service.provider}")
        
        if llm_service.available:
            print("🎉 LLM Service is ready for real API calls!")
        else:
            print("❌ LLM Service is not available - check your API key")
            
    except Exception as e:
        print(f"❌ Error testing LLM service: {e}")

if __name__ == "__main__":
    set_claude_environment()
    test_llm_service()

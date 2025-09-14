"""
Test Claude API key directly to verify it's working.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_claude_key():
    """Test the Claude API key directly."""
    print("🔑 Testing Claude API Key")
    print("=" * 30)
    
    # Get the API key
    api_key = os.getenv("CLAUDE_SECRET")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    print(f"✅ Key length: {len(api_key)} characters")
    
    # Test with Anthropic client directly
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        
        print("\n🧪 Testing API call...")
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello, can you respond with just 'API key is working'?"}
            ]
        )
        
        print("✅ API call successful!")
        print(f"✅ Response: {response.content[0].text}")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        
        # Check specific error types
        if "401" in str(e):
            print("❌ 401 Unauthorized - API key is invalid or expired")
        elif "403" in str(e):
            print("❌ 403 Forbidden - API key doesn't have permission")
        elif "429" in str(e):
            print("❌ 429 Rate Limited - Too many requests")
        else:
            print(f"❌ Other error: {e}")

if __name__ == "__main__":
    test_claude_key()

"""
Demo script showing the difference between mock and real Claude responses.
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def demo_mock_vs_real():
    """Demonstrate the difference between mock and real responses."""
    print("🤖 Mock vs Real Claude Response Demo")
    print("=" * 50)
    
    # Check if Claude API key is set
    claude_secret = os.getenv("CLAUDE_SECRET")
    has_real_key = claude_secret and claude_secret != "your-claude-api-key-here" and claude_secret != "test-key-for-demo"
    
    print(f"🔑 Claude API Key Status: {'✅ Set' if has_real_key else '❌ Not Set'}")
    print()
    
    # Test data
    patient_data = {
        "name": "Sarah Johnson",
        "medical_history": ["Diabetes Type 2", "Diabetic Retinopathy"],
        "current_medications": ["Insulin", "Metformin"],
        "symptoms": ["vision problems", "numbness in feet"]
    }
    
    class MockContext:
        action = "follow_up"
    
    try:
        from services.llm_service import llm_service
        
        print("🧪 Testing Conversation Starter")
        print("-" * 30)
        
        # Test conversation starter
        starter = await llm_service.generate_conversation_starter(patient_data, MockContext())
        print(f"🤖 Agent Starter: {starter}")
        
        if "Thank you for that information" in starter:
            print("❌ This is a MOCK response (Claude API key not set)")
        else:
            print("✅ This is a REAL Claude response!")
        
        print("\n🧪 Testing Conversation Response")
        print("-" * 30)
        
        # Test conversation response
        conversation_history = [
            {"speaker": "agent", "message": starter},
            {"speaker": "patient", "message": "I've been having more vision problems lately, especially at night"}
        ]
        
        response = await llm_service.generate_conversation_response(
            "I've been having more vision problems lately, especially at night",
            conversation_history,
            patient_data,
            MockContext(),
            1
        )
        
        print(f"🤖 Agent Response: {response['response']}")
        print(f"📊 Should Terminate: {response['should_terminate']}")
        print(f"📝 Termination Reason: {response['termination_reason']}")
        
        if "Thank you for that information" in response['response']:
            print("❌ This is a MOCK response (Claude API key not set)")
        else:
            print("✅ This is a REAL Claude response!")
        
        print("\n📊 System Status")
        print("-" * 30)
        print(f"✅ LLM Service Available: {llm_service.available}")
        print(f"✅ Provider: {llm_service.provider}")
        
        if not has_real_key:
            print("\n🔧 To Enable Real Claude Responses:")
            print("1. Get API key from: https://console.anthropic.com/")
            print("2. Set environment variable:")
            print("   Windows: $env:CLAUDE_SECRET='your-key'")
            print("   Linux/Mac: export CLAUDE_SECRET='your-key'")
            print("3. Restart Flask server: python app.py")
            print("4. Run this demo again!")
        else:
            print("\n🎉 Real Claude responses are working!")
            print("Your healthcare agent is now fully intelligent!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(demo_mock_vs_real())

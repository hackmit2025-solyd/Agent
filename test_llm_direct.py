"""
Test LLM service directly to verify Claude integration.
"""
import asyncio
from services.llm_service import llm_service

async def test_llm_direct():
    """Test LLM service directly."""
    print("🤖 Testing LLM Service Directly")
    print("=" * 40)
    
    # Test 1: Check if LLM is available
    print(f"\n1. 📊 LLM Status")
    print(f"   Available: {llm_service.available}")
    print(f"   Provider: {llm_service.provider}")
    
    # Test 2: Test conversation starter
    print(f"\n2. 💬 Test Conversation Starter")
    patient_data = {
        "name": "John Smith",
        "medical_history": ["Diabetes Type 2"],
        "current_medications": ["Metformin"],
        "symptoms": ["blurred vision"]
    }
    
    class MockContext:
        action = "follow_up"
    
    context = MockContext()
    
    try:
        starter = await llm_service.generate_conversation_starter(patient_data, context)
        print(f"   Starter: {starter}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Test conversation response
    print(f"\n3. 🗣️ Test Conversation Response")
    conversation_history = [
        {"speaker": "agent", "message": "Hello John! How are you feeling?"},
        {"speaker": "patient", "message": "I've been having vision problems"}
    ]
    
    try:
        response = await llm_service.generate_conversation_response(
            "Yes, I'm taking my Metformin as prescribed",
            conversation_history,
            patient_data,
            context,
            2
        )
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"\n🎉 LLM Direct Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_llm_direct())

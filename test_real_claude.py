"""
Test script to demonstrate real Claude integration.
"""
import os
import asyncio
import requests

async def test_real_claude():
    """Test the system with real Claude API key."""
    print("🤖 Testing Real Claude Integration")
    print("=" * 50)
    
    # Check current environment
    claude_secret = os.getenv("CLAUDE_SECRET")
    print(f"🔑 Current CLAUDE_SECRET: {claude_secret[:10] if claude_secret else 'Not set'}...")
    
    if not claude_secret or claude_secret == "your-claude-api-key-here":
        print("\n❌ Please set your real Claude API key first!")
        print("1. Get your API key from: https://console.anthropic.com/")
        print("2. Set environment variable:")
        print("   Windows: set CLAUDE_SECRET=your-actual-api-key")
        print("   Linux/Mac: export CLAUDE_SECRET=your-actual-api-key")
        print("3. Restart Flask server: python app.py")
        return
    
    # Test LLM service directly
    print("\n🧪 Testing LLM Service Directly")
    print("-" * 30)
    
    try:
        from services.llm_service import llm_service
        
        # Test conversation starter
        patient_data = {
            "name": "John Smith",
            "medical_history": ["Diabetes Type 2"],
            "current_medications": ["Metformin"],
            "symptoms": ["blurred vision"]
        }
        
        class MockContext:
            action = "follow_up"
        
        print("🤖 Generating conversation starter...")
        starter = await llm_service.generate_conversation_starter(patient_data, MockContext())
        print(f"✅ Conversation Starter: {starter}")
        
        # Test conversation response
        print("\n🤖 Testing conversation response...")
        conversation_history = [
            {"speaker": "agent", "message": starter},
            {"speaker": "patient", "message": "I've been having vision problems lately"}
        ]
        
        response = await llm_service.generate_conversation_response(
            "I've been having vision problems lately",
            conversation_history,
            patient_data,
            MockContext(),
            1
        )
        
        print(f"✅ Agent Response: {response['response']}")
        print(f"✅ Should Terminate: {response['should_terminate']}")
        print(f"✅ Termination Reason: {response['termination_reason']}")
        
    except Exception as e:
        print(f"❌ Error testing LLM service: {e}")
        return
    
    # Test Flask API
    print("\n🌐 Testing Flask API")
    print("-" * 30)
    
    try:
        # Test system status
        response = requests.get("http://localhost:8080/api/system-status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Claude Available: {data['claude_status']['available']}")
            print(f"✅ Provider: {data['claude_status']['provider']}")
        else:
            print(f"❌ API Error: {response.status_code}")
            return
        
        # Test doctor query
        print("\n🩺 Testing Doctor Query...")
        query_data = {
            "doctor_query": "Follow up with all diabetic patients from last week who have been experiencing vision problems"
        }
        
        response = requests.post("http://localhost:8080/api/doctor-query", json=query_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query processed successfully!")
            print(f"✅ Patients found: {data['patients_found']}")
            print(f"✅ Sub-agents created: {data['sub_agents_created']}")
        else:
            print(f"❌ Doctor Query Error: {response.status_code}")
            print(f"Error: {response.text}")
            return
        
        # Test conversation
        print("\n💬 Testing Conversation...")
        
        # Get the first sub-agent
        response = requests.get("http://localhost:8080/api/sub-agents")
        if response.status_code == 200:
            data = response.json()
            if data['sub_agents']:
                agent_id = list(data['sub_agents'].keys())[0]
                print(f"✅ Using sub-agent: {agent_id}")
                
                # Start conversation
                response = requests.post("http://localhost:8080/api/conversation/start", 
                                       json={"agent_id": agent_id})
                if response.status_code == 200:
                    data = response.json()
                    print(f"🤖 Agent: {data['agent_message']}")
                    
                    # Test response
                    response = requests.post("http://localhost:8080/api/conversation/respond",
                                           json={
                                               "agent_id": agent_id,
                                               "patient_message": "I've been having vision problems lately"
                                           })
                    if response.status_code == 200:
                        data = response.json()
                        print(f"🤖 Agent: {data['agent_message']}")
                        
                        if "Thank you for that information" in data['agent_message']:
                            print("❌ This is still a mock response - check your API key")
                        else:
                            print("✅ This looks like a real Claude response!")
                    else:
                        print(f"❌ Conversation response error: {response.status_code}")
                else:
                    print(f"❌ Start conversation error: {response.status_code}")
            else:
                print("❌ No sub-agents available")
        else:
            print(f"❌ Get sub-agents error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Flask API: {e}")
    
    print("\n🎉 Test Complete!")
    print("If you see real Claude responses above, your integration is working!")

if __name__ == "__main__":
    asyncio.run(test_real_claude())

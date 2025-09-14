"""
Test the system with real Claude API key setup instructions.
"""
import os
import requests

def test_with_real_claude():
    """Test system and show how to enable real Claude."""
    print("🤖 Testing Healthcare Agent System with Real Claude Setup")
    print("=" * 60)
    
    # Check current Claude status
    print("\n1. 📊 Current Claude Status")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8080/api/system-status")
        if response.status_code == 200:
            data = response.json()
            claude_available = data['claude_status']['available']
            claude_provider = data['claude_status']['provider']
            
            print(f"✅ Claude Available: {claude_available}")
            print(f"✅ Provider: {claude_provider}")
            
            if claude_available:
                print("🎉 Claude is working! You should see intelligent responses.")
            else:
                print("❌ Claude is not working. You'll see mock responses.")
        else:
            print("❌ Cannot connect to API server")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test database connection
    print("\n2. 🗄️ Database Service Status")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:3000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database Service: {data['status']}")
            print(f"✅ Patients Available: {data['patients_available']}")
        else:
            print("❌ Database service not running")
    except Exception as e:
        print(f"❌ Database Error: {e}")
    
    # Test a simple conversation
    print("\n3. 💬 Testing Conversation")
    print("-" * 30)
    
    try:
        # Create a sub-agent
        sub_agent_data = {
            "patient_id": "PAT001",
            "context": {
                "action": "follow_up",
                "time_filter": "today",
                "condition_filter": "diabetes",
                "patient_criteria": {"status": "active"}
            }
        }
        
        response = requests.post("http://localhost:8080/api/create-sub-agent", json=sub_agent_data)
        if response.status_code == 200:
            data = response.json()
            agent_id = data['sub_agent']['agent_id']
            print(f"✅ Created sub-agent: {agent_id}")
            
            # Start conversation
            response = requests.post("http://localhost:8080/api/conversation/start", json={"agent_id": agent_id})
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Agent: {data['agent_message']}")
                
                # Test response
                response = requests.post("http://localhost:8080/api/conversation/respond", json={
                    "agent_id": agent_id,
                    "patient_message": "I've been having vision problems"
                })
                if response.status_code == 200:
                    data = response.json()
                    print(f"🤖 Agent: {data['agent_message']}")
                    
                    if "Thank you for that information" in data['agent_message']:
                        print("❌ This is a mock response - Claude API key not set")
                    else:
                        print("✅ This looks like a real Claude response!")
                else:
                    print(f"❌ Conversation error: {response.status_code}")
            else:
                print(f"❌ Start conversation error: {response.status_code}")
        else:
            print(f"❌ Create sub-agent error: {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {e}")
    
    # Show setup instructions
    print("\n4. 🔧 To Enable Real Claude Responses")
    print("-" * 30)
    print("1. Get Claude API key from: https://console.anthropic.com/")
    print("2. Set environment variable:")
    print("   Windows: set CLAUDE_SECRET=your-actual-api-key")
    print("   Linux/Mac: export CLAUDE_SECRET=your-actual-api-key")
    print("3. Restart the Flask server: python app.py")
    print("4. Run this test again to see real Claude responses!")
    
    print("\n🎉 Test Complete!")
    print("The system is working with mock data and mock responses.")
    print("Set your Claude API key to see real AI-powered conversations!")

if __name__ == "__main__":
    test_with_real_claude()

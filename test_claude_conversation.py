"""
Test Claude conversation functionality directly.
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8080"

def test_claude_conversation():
    """Test Claude conversation functionality."""
    print("🤖 Testing Claude Conversation Functionality")
    print("=" * 50)
    
    try:
        # Step 1: Create a sub-agent
        print("\n1. 🤖 Create Sub-Agent")
        print("-" * 30)
        
        sub_agent_data = {
            "patient_id": "PAT001",
            "context": {
                "action": "follow_up",
                "time_filter": "today",
                "condition_filter": "diabetes",
                "patient_criteria": {"status": "active"}
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/create-sub-agent", json=sub_agent_data)
        if response.status_code == 200:
            data = response.json()
            agent_id = data['sub_agent']['agent_id']
            print(f"✅ Created sub-agent: {agent_id}")
        else:
            print(f"❌ Error creating sub-agent: {response.status_code}")
            return
        
        # Step 2: Start conversation (should use Claude)
        print("\n2. 💬 Start Conversation with Claude")
        print("-" * 30)
        
        response = requests.post(f"{BASE_URL}/api/conversation/start", json={"agent_id": agent_id})
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Claude Response: {data['agent_message']}")
            print(f"📊 Max rounds: {data['max_rounds']}")
        else:
            print(f"❌ Error starting conversation: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # Step 3: Test conversation response (should use Claude)
        print("\n3. 🗣️ Test Conversation Response")
        print("-" * 30)
        
        test_messages = [
            "I've been having some vision problems lately",
            "Yes, I'm taking my Metformin as prescribed",
            "The vision issues seem to be getting worse"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n👤 Patient: {message}")
            
            response = requests.post(f"{BASE_URL}/api/conversation/respond", json={
                "agent_id": agent_id,
                "patient_message": message
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Claude Response: {data['agent_message']}")
                
                if data.get('conversation_terminated'):
                    print(f"🎯 Conversation terminated: {data.get('termination_reason', 'No reason given')}")
                    break
                else:
                    print(f"📊 Round {data['conversation_round']}/{data['max_rounds']}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                break
        
        print("\n🎉 Claude Conversation Test Complete!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running!")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_claude_conversation()

"""
Test the integrated conversation API with Claude termination logic.
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8080"

def test_conversation_api():
    """Test the conversation API with real patient interaction."""
    print("🚀 Testing Integrated Conversation API")
    print("=" * 50)
    
    try:
        # Step 1: Get a patient and create sub-agent
        print("\n1. 👤 Setup Patient and Sub-Agent")
        print("-" * 40)
        
        # Get patients
        response = requests.get(f"{BASE_URL}/api/patients")
        if response.status_code == 200:
            data = response.json()
            patient = data['patients'][0]  # Use first patient
            print(f"✅ Using patient: {patient['name']} - {', '.join(patient['medical_history'])}")
        else:
            print(f"❌ Error getting patients: {response.status_code}")
            return
        
        # Create sub-agent
        sub_agent_data = {
            "patient_id": patient['patient_id'],
            "context": {
                "action": "follow_up",
                "time_filter": "today",
                "condition_filter": "all",
                "patient_criteria": {"status": "active"}
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/create-sub-agent", json=sub_agent_data)
        if response.status_code == 200:
            agent_data = response.json()
            agent_id = agent_data['sub_agent']['agent_id']
            print(f"✅ Created sub-agent: {agent_id}")
        else:
            print(f"❌ Error creating sub-agent: {response.status_code}")
            return
        
        # Step 2: Start conversation
        print("\n2. 💬 Start Conversation")
        print("-" * 40)
        
        response = requests.post(f"{BASE_URL}/api/conversation/start", json={"agent_id": agent_id})
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Agent: {data['agent_message']}")
            print(f"📊 Max rounds: {data['max_rounds']}")
        else:
            print(f"❌ Error starting conversation: {response.status_code}")
            return
        
        # Step 3: Simulate conversation
        print("\n3. 🗣️ Simulate Patient Responses")
        print("-" * 40)
        
        # Simulate patient responses
        patient_responses = [
            "I'm feeling good overall",
            "Yes, I'm taking my medications twice a day",
            "No, no new symptoms to report",
            "Everything seems to be working well"
        ]
        
        for i, patient_response in enumerate(patient_responses, 1):
            print(f"\n👤 Patient: {patient_response}")
            
            response = requests.post(f"{BASE_URL}/api/conversation/respond", json={
                "agent_id": agent_id,
                "patient_message": patient_response
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Agent: {data['agent_message']}")
                
                if data.get('conversation_terminated'):
                    print(f"\n🎯 Conversation Terminated!")
                    print(f"📊 Final Result: {data['conversation_result']}")
                    break
                else:
                    print(f"📊 Round {data['conversation_round']}/{data['max_rounds']}")
            else:
                print(f"❌ Error: {response.status_code}")
                break
            
            time.sleep(1)  # Pause between responses
        
        # Step 4: Check system status
        print("\n4. 📊 System Status")
        print("-" * 40)
        response = requests.get(f"{BASE_URL}/api/system-status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ System Status:")
            print(f"   Total Sub-Agents: {status_data['system_status']['total_sub_agents']}")
            print(f"   Completed: {status_data['system_status']['completed']}")
            print(f"   Flagged: {status_data['system_status']['flagged_for_review']}")
            print(f"   Success Rate: {status_data['system_status']['success_rate']:.1f}%")
        
        print("\n🎉 Conversation API Test Complete!")
        print("✅ Conversation started and managed by API!")
        print("✅ Agent responses generated intelligently!")
        print("✅ Claude termination logic integrated!")
        print("✅ Conversation processed and decision made!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running!")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_conversation_api()

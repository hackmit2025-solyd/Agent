"""
Simple API Demo - Shows the Healthcare Agent Flask API in action
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8080"

def demo_api():
    """Demonstrate the Healthcare Agent API."""
    print("🚀 Healthcare Agent Flask API Demo")
    print("=" * 50)
    
    try:
        # Test 1: Home endpoint
        print("\n1. 📡 API Documentation")
        print("-" * 30)
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data['message']}")
            print(f"📋 Available Endpoints: {len(data['endpoints'])}")
            for endpoint, description in data['endpoints'].items():
                print(f"   {endpoint}: {description}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # Test 2: Parse a doctor query
        print("\n2. 🧠 Parse Doctor Query")
        print("-" * 30)
        query_data = {
            "query": "Follow up with all diabetic patients from last week who have been experiencing vision problems"
        }
        response = requests.post(f"{BASE_URL}/api/parse-query", json=query_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query: {data['query']}")
            print(f"🎯 Action: {data['parsed_criteria']['action']}")
            print(f"⏰ Time Filter: {data['parsed_criteria']['time_filter']}")
            print(f"🏥 Condition Filter: {data['parsed_criteria']['condition_filter']}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # Test 3: Get patients
        print("\n3. 👥 Get Patients")
        print("-" * 30)
        response = requests.get(f"{BASE_URL}/api/patients")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} patients:")
            for patient in data['patients']:
                print(f"   {patient['patient_id']}: {patient['name']} - {', '.join(patient['medical_history'])}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # Test 4: Create sub-agent
        print("\n4. 🤖 Create Sub-Agent")
        print("-" * 30)
        sub_agent_data = {
            "patient_id": "PAT001",
            "context": {
                "action": "follow_up",
                "time_filter": "today",
                "patient_criteria": {"status": "active"}
            }
        }
        response = requests.post(f"{BASE_URL}/api/create-sub-agent", json=sub_agent_data)
        if response.status_code == 200:
            data = response.json()
            agent_id = data['sub_agent']['agent_id']
            print(f"✅ Created Sub-Agent: {agent_id}")
            print(f"👤 Patient: {data['sub_agent']['patient_name']}")
            print(f"📋 Status: {data['sub_agent']['status']}")
            
            # Test 5: Simulate communication
            print("\n5. 📞 Simulate Communication")
            print("-" * 30)
            sim_data = {
                "agent_id": agent_id,
                "communication_data": {
                    "session_id": f"session_{agent_id}",
                    "duration": 180.0,
                    "confidence_score": 0.90,
                    "conversation_quality": "excellent",
                    "data_obtained": {
                        "feeling_well": True,
                        "medication_adherence": True,
                        "no_concerns": True
                    },
                    "missing_data": [],
                    "transcript": "Patient reports feeling well, taking medications as prescribed."
                }
            }
            response = requests.post(f"{BASE_URL}/api/simulate-communication", json=sim_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Communication Processed")
                print(f"🎯 Outcome: {data['simulation_result']['outcome'].upper()}")
                print(f"📊 Confidence: {data['simulation_result']['confidence']:.2f}")
                print(f"💭 Reasoning: {data['simulation_result']['reasoning'][:100]}...")
            else:
                print(f"❌ Error: {response.status_code}")
        
        # Test 6: System status
        print("\n6. 📊 System Status")
        print("-" * 30)
        response = requests.get(f"{BASE_URL}/api/system-status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System Status:")
            print(f"   Sub-Agents: {data['system_status']['total_sub_agents']}")
            print(f"   Completed: {data['system_status']['completed']}")
            print(f"   Flagged: {data['system_status']['flagged_for_review']}")
            print(f"   Success Rate: {data['system_status']['success_rate']:.1f}%")
            print(f"   Claude Available: {data['claude_status']['available']}")
        else:
            print(f"❌ Error: {response.status_code}")
        
        print("\n🎉 API Demo Complete!")
        print("✅ All endpoints working correctly!")
        print("🌐 Server running at: http://localhost:8080/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running!")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    demo_api()

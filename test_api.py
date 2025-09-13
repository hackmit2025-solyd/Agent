"""
Test Client for Healthcare Agent Flask API
Demonstrates all API endpoints and functionality.
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8080"

def test_api():
    """Test all API endpoints."""
    print("🧪 Testing Healthcare Agent Flask API")
    print("=" * 50)
    
    # Test 1: Home endpoint
    print("\n1. Testing Home Endpoint")
    print("-" * 30)
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 2: Parse query
    print("\n2. Testing Query Parsing")
    print("-" * 30)
    query_data = {
        "query": "Follow up with all diabetic patients from last week who have been experiencing vision problems"
    }
    response = requests.post(f"{BASE_URL}/api/parse-query", json=query_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 3: Get patients
    print("\n3. Testing Get Patients")
    print("-" * 30)
    response = requests.get(f"{BASE_URL}/api/patients")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 4: Create sub-agent
    print("\n4. Testing Create Sub-Agent")
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
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        agent_id = response.json()["sub_agent"]["agent_id"]
        
        # Test 5: Process communication
        print("\n5. Testing Process Communication")
        print("-" * 30)
        comm_data = {"agent_id": agent_id}
        response = requests.post(f"{BASE_URL}/api/process-communication", json=comm_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 6: Simulate communication
        print("\n6. Testing Simulate Communication")
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
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 7: Get sub-agents
    print("\n7. Testing Get Sub-Agents")
    print("-" * 30)
    response = requests.get(f"{BASE_URL}/api/sub-agents")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 8: System status
    print("\n8. Testing System Status")
    print("-" * 30)
    response = requests.get(f"{BASE_URL}/api/system-status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test 9: Demo
    print("\n9. Testing Demo")
    print("-" * 30)
    demo_data = {"type": "full"}
    response = requests.post(f"{BASE_URL}/api/demo", json=demo_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    print("\n🎉 API Testing Complete!")

if __name__ == "__main__":
    test_api()

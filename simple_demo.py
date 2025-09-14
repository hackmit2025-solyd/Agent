"""
Simple Healthcare Agent Demo
Just query database and create sub-agents - no communication processing.
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8080"

def simple_demo():
    """Simple demo: query database and create sub-agents."""
    print("🚀 Simple Healthcare Agent Demo")
    print("=" * 50)
    
    try:
        # Step 1: Get all patients from database
        print("\n1. 📊 Query Database for All Patients")
        print("-" * 40)
        response = requests.get(f"{BASE_URL}/api/patients")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} patients in database:")
            for patient in data['patients']:
                print(f"   {patient['patient_id']}: {patient['name']} - {', '.join(patient['medical_history'])}")
        else:
            print(f"❌ Error: {response.status_code}")
            return
        
        # Step 2: Create sub-agents for ALL patients
        print("\n2. 🤖 Create Sub-Agents for All Patients")
        print("-" * 40)
        
        sub_agents = []
        for i, patient in enumerate(data['patients'], 1):
            print(f"\n   Creating Sub-Agent {i} for {patient['name']}...")
            
            sub_agent_data = {
                "patient_id": patient['patient_id'],
                "context": {
                    "action": "follow_up",
                    "time_filter": "all",
                    "condition_filter": "all",
                    "patient_criteria": {"status": "active"}
                }
            }
            
            response = requests.post(f"{BASE_URL}/api/create-sub-agent", json=sub_agent_data)
            if response.status_code == 200:
                agent_data = response.json()
                agent_id = agent_data['sub_agent']['agent_id']
                sub_agents.append({
                    'agent_id': agent_id,
                    'patient_name': patient['name'],
                    'patient_id': patient['patient_id'],
                    'medical_history': patient['medical_history']
                })
                print(f"   ✅ Created: {agent_id}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        
        print(f"\n✅ Successfully created {len(sub_agents)} sub-agents!")
        
        # Step 3: Show all sub-agents
        print("\n3. 🤖 All Sub-Agents Created")
        print("-" * 40)
        response = requests.get(f"{BASE_URL}/api/sub-agents")
        if response.status_code == 200:
            agents_data = response.json()
            print(f"✅ Total Sub-Agents: {agents_data['count']}")
            for agent in agents_data['sub_agents']:
                print(f"   {agent['agent_id']}: {agent['patient_name']} - {agent['status']}")
        
        # Step 4: System status
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
            print(f"   Claude Available: {status_data['claude_status']['available']}")
        
        print("\n🎉 Simple Demo Complete!")
        print("✅ Database queried successfully!")
        print("✅ All patients have sub-agents!")
        print("✅ Ready for further processing!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running!")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    simple_demo()

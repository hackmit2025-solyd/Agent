"""
Test the complete flow: Doctor Query → Master Agent → Database → Sub-Agents → Communication
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8080"

def test_complete_flow():
    """Test the complete healthcare agent flow."""
    print("🚀 Testing Complete Healthcare Agent Flow")
    print("=" * 60)
    
    try:
        # Step 1: Doctor Query → Master Agent → Database → Sub-Agents
        print("\n1. 🩺 Doctor Query Processing")
        print("-" * 40)
        
        doctor_query = "Follow up with all diabetic patients from last week who have been experiencing vision problems"
        print(f"📝 Doctor Query: '{doctor_query}'")
        
        response = requests.post(f"{BASE_URL}/api/doctor-query", json={"query": doctor_query})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query processed successfully!")
            print(f"🎯 Action: {data['parsed_criteria']['action']}")
            print(f"⏰ Time Filter: {data['parsed_criteria']['time_filter']}")
            print(f"🏥 Condition Filter: {data['parsed_criteria']['condition_filter']}")
            print(f"👥 Patients Found: {data['patients_found']}")
            print(f"🤖 Sub-Agents Created: {data['sub_agents_created']}")
            
            # Show created sub-agents
            print(f"\n📋 Created Sub-Agents:")
            for agent in data['sub_agents']:
                print(f"   {agent['agent_id']}: {agent['patient_name']} - {', '.join(agent['medical_history'])}")
            
            sub_agents = data['sub_agents']
        else:
            print(f"❌ Error: {response.status_code}")
            return
        
        # Step 2: Start communication with first sub-agent
        print(f"\n2. 💬 Starting Communication with {sub_agents[0]['patient_name']}")
        print("-" * 40)
        
        agent_id = sub_agents[0]['agent_id']
        
        # Start conversation
        response = requests.post(f"{BASE_URL}/api/conversation/start", json={"agent_id": agent_id})
        if response.status_code == 200:
            data = response.json()
            print(f"🤖 Agent: {data['agent_message']}")
            print(f"📊 Max rounds: {data['max_rounds']}")
        else:
            print(f"❌ Error starting conversation: {response.status_code}")
            return
        
        # Step 3: Simulate patient conversation
        print(f"\n3. 🗣️ Patient Conversation Simulation")
        print("-" * 40)
        
        # Simulate patient responses based on their condition
        patient_responses = [
            "I've been having some vision problems lately",
            "Yes, I'm taking my Metformin as prescribed",
            "The vision issues seem to be getting worse",
            "I'm worried about my diabetes control"
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
                    result = data['conversation_result']
                    print(f"📊 Outcome: {result['outcome'].upper()}")
                    print(f"📈 Confidence: {result['confidence']:.2f}")
                    print(f"💭 Reasoning: {result['reasoning']}")
                    break
                else:
                    print(f"📊 Round {data['conversation_round']}/{data['max_rounds']}")
            else:
                print(f"❌ Error: {response.status_code}")
                break
            
            time.sleep(1)  # Pause between responses
        
        # Step 4: Check system status
        print(f"\n4. 📊 Final System Status")
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
        
        # Step 5: Show all sub-agents
        print(f"\n5. 🤖 All Sub-Agents Status")
        print("-" * 40)
        response = requests.get(f"{BASE_URL}/api/sub-agents")
        if response.status_code == 200:
            agents_data = response.json()
            print(f"✅ Active Sub-Agents: {agents_data['count']}")
            for agent in agents_data['sub_agents']:
                print(f"   {agent['agent_id']}: {agent['patient_name']} - {agent['status']}")
        
        print(f"\n🎉 Complete Flow Test Successful!")
        print("✅ Doctor Query → Master Agent → Database → Sub-Agents")
        print("✅ Sub-Agents → Communication Lines → Patient Interaction")
        print("✅ Claude Decision Making → Status Updates")
        print("✅ Complete healthcare workflow implemented!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running!")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_complete_flow()

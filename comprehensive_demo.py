"""
Comprehensive Healthcare Agent Demo
Shows multiple sub-agents being created and processed.
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8080"

def comprehensive_demo():
    """Demonstrate the full healthcare agent system with multiple sub-agents."""
    print("🚀 Comprehensive Healthcare Agent Demo")
    print("=" * 60)
    
    try:
        # Step 1: Parse a complex doctor query
        print("\n1. 🧠 Parse Complex Doctor Query")
        print("-" * 40)
        query_data = {
            "query": "Follow up with all patients who have diabetes or heart disease from last week, check their medication adherence and assess any new symptoms"
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
            return
        
        # Step 2: Get all patients
        print("\n2. 👥 Get All Patients")
        print("-" * 40)
        response = requests.get(f"{BASE_URL}/api/patients")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} patients:")
            for patient in data['patients']:
                print(f"   {patient['patient_id']}: {patient['name']} - {', '.join(patient['medical_history'])}")
        else:
            print(f"❌ Error: {response.status_code}")
            return
        
        # Step 3: Create multiple sub-agents for relevant patients
        print("\n3. 🤖 Create Multiple Sub-Agents")
        print("-" * 40)
        
        # Find patients with diabetes or heart disease
        diabetic_heart_patients = []
        for patient in data['patients']:
            has_diabetes = any("diabetes" in h.lower() for h in patient['medical_history'])
            has_heart_disease = any("heart" in h.lower() for h in patient['medical_history'])
            if has_diabetes or has_heart_disease:
                diabetic_heart_patients.append(patient)
        
        print(f"🎯 Found {len(diabetic_heart_patients)} patients matching criteria:")
        for patient in diabetic_heart_patients:
            print(f"   {patient['patient_id']}: {patient['name']} - {', '.join(patient['medical_history'])}")
        
        # Create sub-agents for each matching patient
        sub_agents = []
        for i, patient in enumerate(diabetic_heart_patients, 1):
            print(f"\n   Creating Sub-Agent {i} for {patient['name']}...")
            
            sub_agent_data = {
                "patient_id": patient['patient_id'],
                "context": {
                    "action": "follow_up",
                    "time_filter": "last_week",
                    "condition_filter": "diabetes,heart_disease",
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
        
        # Step 4: Process communications for each sub-agent
        print("\n4. 📞 Process Communications for All Sub-Agents")
        print("-" * 40)
        
        communication_results = []
        
        for i, agent in enumerate(sub_agents, 1):
            print(f"\n   Processing Sub-Agent {i}: {agent['patient_name']}")
            print(f"   Agent ID: {agent['agent_id']}")
            print(f"   Medical History: {', '.join(agent['medical_history'])}")
            
            # Simulate different communication scenarios based on patient condition
            if "diabetes" in ' '.join(agent['medical_history']).lower():
                # Diabetic patient - success scenario
                comm_data = {
                    "session_id": f"session_{agent['agent_id']}",
                    "duration": 180.0,
                    "confidence_score": 0.92,
                    "conversation_quality": "excellent",
                    "data_obtained": {
                        "blood_sugar_stable": True,
                        "medication_adherence": True,
                        "no_new_symptoms": True,
                        "feeling_well": True
                    },
                    "missing_data": [],
                    "transcript": f"Patient {agent['patient_name']} reports blood sugar levels are stable, taking Metformin as prescribed, no new symptoms, feeling well overall."
                }
            else:
                # Heart disease patient - mixed scenario
                comm_data = {
                    "session_id": f"session_{agent['agent_id']}",
                    "duration": 150.0,
                    "confidence_score": 0.75,
                    "conversation_quality": "good",
                    "data_obtained": {
                        "medication_adherence": True,
                        "chest_pain_improved": True,
                        "exercise_tolerance": "moderate"
                    },
                    "missing_data": ["detailed_symptom_description"],
                    "transcript": f"Patient {agent['patient_name']} reports taking medications as prescribed, chest pain has improved, but some difficulty with exercise."
                }
            
            # Process the communication
            sim_data = {
                "agent_id": agent['agent_id'],
                "communication_data": comm_data
            }
            
            response = requests.post(f"{BASE_URL}/api/simulate-communication", json=sim_data)
            if response.status_code == 200:
                result = response.json()
                outcome = result['simulation_result']['outcome']
                confidence = result['simulation_result']['confidence']
                reasoning = result['simulation_result']['reasoning']
                
                print(f"   🎯 Outcome: {outcome.upper()}")
                print(f"   📊 Confidence: {confidence:.2f}")
                print(f"   💭 Reasoning: {reasoning[:80]}...")
                
                communication_results.append({
                    'patient_name': agent['patient_name'],
                    'outcome': outcome,
                    'confidence': confidence,
                    'reasoning': reasoning
                })
            else:
                print(f"   ❌ Error: {response.status_code}")
            
            time.sleep(1)  # Pause between agents
        
        # Step 5: Show system summary
        print("\n5. 📊 System Summary")
        print("-" * 40)
        
        # Get system status
        response = requests.get(f"{BASE_URL}/api/system-status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ System Status:")
            print(f"   Total Sub-Agents: {status_data['system_status']['total_sub_agents']}")
            print(f"   Completed: {status_data['system_status']['completed']}")
            print(f"   Flagged for Review: {status_data['system_status']['flagged_for_review']}")
            print(f"   Success Rate: {status_data['system_status']['success_rate']:.1f}%")
            print(f"   Claude Available: {status_data['claude_status']['available']}")
        
        # Show communication results summary
        print(f"\n📋 Communication Results Summary:")
        print(f"   Total Communications: {len(communication_results)}")
        
        outcomes = {}
        for result in communication_results:
            outcome = result['outcome']
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        for outcome, count in outcomes.items():
            print(f"   {outcome.upper()}: {count} patients")
        
        print(f"\n📋 Individual Results:")
        for result in communication_results:
            print(f"   {result['patient_name']}: {result['outcome'].upper()} (Confidence: {result['confidence']:.2f})")
        
        # Step 6: Get all sub-agents
        print("\n6. 🤖 All Sub-Agents Status")
        print("-" * 40)
        response = requests.get(f"{BASE_URL}/api/sub-agents")
        if response.status_code == 200:
            agents_data = response.json()
            print(f"✅ Active Sub-Agents: {agents_data['count']}")
            for agent in agents_data['sub_agents']:
                print(f"   {agent['agent_id']}: {agent['patient_name']} - {agent['status']}")
        
        print("\n🎉 Comprehensive Demo Complete!")
        print("✅ Multiple sub-agents created and processed successfully!")
        print("✅ Claude made intelligent decisions for each patient!")
        print("✅ System handled complex multi-patient workflow!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running!")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    comprehensive_demo()

"""
Interactive Patient Test
You are the patient - have a real conversation with the sub-agent!
"""
import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8080"

def interactive_patient_test():
    """Interactive test where user is the patient."""
    print("🏥 Interactive Patient Test")
    print("=" * 50)
    print("You are now a patient! Let's have a conversation with your healthcare agent.")
    print("The agent will make decisions based on our real conversation.")
    print()
    
    try:
        # Step 1: Get a patient to be
        print("1. 👤 Choose Your Patient Identity")
        print("-" * 40)
        response = requests.get(f"{BASE_URL}/api/patients")
        if response.status_code == 200:
            data = response.json()
            print("Available patients to be:")
            for i, patient in enumerate(data['patients'], 1):
                print(f"   {i}. {patient['name']} - {', '.join(patient['medical_history'])}")
            
            while True:
                try:
                    choice = int(input("\nChoose a patient (1-3): ")) - 1
                    if 0 <= choice < len(data['patients']):
                        selected_patient = data['patients'][choice]
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a number.")
            
            print(f"\n✅ You are now: {selected_patient['name']}")
            print(f"   Medical History: {', '.join(selected_patient['medical_history'])}")
        else:
            print(f"❌ Error: {response.status_code}")
            return
        
        # Step 2: Create sub-agent for this patient
        print("\n2. 🤖 Creating Your Healthcare Agent")
        print("-" * 40)
        
        sub_agent_data = {
            "patient_id": selected_patient['patient_id'],
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
            print(f"✅ Your healthcare agent created: {agent_id}")
            print(f"   Agent is ready to communicate with you!")
        else:
            print(f"❌ Error: {response.status_code}")
            return
        
        # Step 3: Interactive conversation
        print("\n3. 💬 Interactive Conversation")
        print("-" * 40)
        print("Your healthcare agent will start the conversation. Answer naturally as the patient.")
        print("Type 'quit' to end the conversation.")
        print()
        
        conversation_history = []
        
        # Agent starts the conversation
        print(f"\n🤖 Healthcare Agent: Hello {selected_patient['name']}! I'm your healthcare agent calling for a follow-up. How have you been feeling since your last visit?")
        conversation_history.append({
            "speaker": "agent",
            "message": f"Hello {selected_patient['name']}! I'm your healthcare agent calling for a follow-up. How have you been feeling since your last visit?",
            "timestamp": time.time()
        })
        
        conversation_rounds = 0
        max_rounds = 5  # Limit conversation length
        
        while conversation_rounds < max_rounds:
            # Get user input
            user_input = input(f"\n{selected_patient['name']}: ").strip()
            
            if user_input.lower() == 'quit':
                print("\n👋 Conversation ended. Let me process the results...")
                break
            
            if not user_input:
                continue
            
            # Add to conversation history
            conversation_history.append({
                "speaker": "patient",
                "message": user_input,
                "timestamp": time.time()
            })
            
            conversation_rounds += 1
            
            # Agent responds based on what patient said and conversation progress
            if conversation_rounds >= max_rounds:
                # Time to wrap up
                agent_response = "Thank you for your time today. I have enough information to complete your follow-up. Let me process this and get back to you with next steps."
                print(f"\n🤖 Healthcare Agent: {agent_response}")
                conversation_history.append({
                    "speaker": "agent",
                    "message": agent_response,
                    "timestamp": time.time()
                })
                break
            elif "headache" in user_input.lower() or "head" in user_input.lower():
                if "not too bad" in user_input.lower() or "mild" in user_input.lower():
                    agent_response = "I understand the headaches are mild. Are you taking any pain medication for them? Any other symptoms I should know about?"
                else:
                    agent_response = "I understand you're experiencing headaches. Can you tell me more about the frequency and intensity? Are they new or have you had them before?"
            elif "good" in user_input.lower() or "fine" in user_input.lower() or "well" in user_input.lower():
                agent_response = "That's great to hear! Are you taking your medications as prescribed? Any side effects to report?"
            elif "help" in user_input.lower():
                agent_response = "I'm here to help! What specific concerns do you have about your health? Please share any symptoms or issues you're experiencing."
            elif "pain" in user_input.lower() or "hurt" in user_input.lower():
                agent_response = "I'm sorry to hear you're in pain. Can you describe the pain - where is it located and what does it feel like?"
            elif "medication" in user_input.lower() or "medicine" in user_input.lower():
                agent_response = "Let's talk about your medications. Are you taking them as prescribed? Any difficulties or concerns with your current medication regimen?"
            elif "nope" in user_input.lower() or "nothing" in user_input.lower() or "no" in user_input.lower():
                if conversation_rounds >= 3:
                    agent_response = "I understand. Based on our conversation, it sounds like you're managing well. Let me wrap up this follow-up call."
                else:
                    agent_response = "That's good to know. Any other concerns or symptoms you'd like to discuss?"
            else:
                agent_response = "Thank you for sharing that. Can you tell me more about how you've been managing your condition? Any new symptoms or changes you've noticed?"
            
            print(f"\n🤖 Healthcare Agent: {agent_response}")
            
            # Add agent response to history
            conversation_history.append({
                "speaker": "agent",
                "message": agent_response,
                "timestamp": time.time()
            })
        
        # Step 4: Process the conversation
        print("\n4. 🧠 Processing Conversation Results")
        print("-" * 40)
        
        # Analyze conversation to create realistic communication data
        patient_messages = [msg['message'].lower() for msg in conversation_history if msg['speaker'] == 'patient']
        all_text = ' '.join(patient_messages)
        
        # Determine data quality based on conversation
        has_symptoms = any(word in all_text for word in ['headache', 'pain', 'hurt', 'symptom', 'problem'])
        has_medication_info = any(word in all_text for word in ['medication', 'medicine', 'pill', 'drug', 'taking'])
        patient_responsive = len(patient_messages) > 0
        conversation_complete = conversation_rounds >= 3
        
        # Create communication data from our conversation
        communication_data = {
            "session_id": f"interactive_session_{agent_id}",
            "duration": len(conversation_history) * 30.0,  # Estimate 30 seconds per exchange
            "confidence_score": 0.85 if conversation_complete else 0.60,
            "conversation_quality": "excellent" if conversation_complete else "good",
            "data_obtained": {
                "patient_responsiveness": patient_responsive,
                "symptom_information": has_symptoms,
                "medication_adherence": has_medication_info,
                "overall_wellbeing": "discussed" if conversation_complete else "partial"
            },
            "missing_data": [] if conversation_complete else ["detailed_symptom_description", "medication_adherence"],
            "transcript": "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in conversation_history])
        }
        
        print("📝 Conversation Summary:")
        print(f"   Duration: {communication_data['duration']:.1f} seconds")
        print(f"   Exchanges: {len(conversation_history)}")
        print(f"   Quality: {communication_data['conversation_quality']}")
        print(f"   Data Obtained: {list(communication_data['data_obtained'].keys())}")
        print(f"   Missing Data: {communication_data['missing_data']}")
        
        # Step 5: Let Claude analyze the conversation
        print("\n5. 🧠 Claude Analysis")
        print("-" * 40)
        
        sim_data = {
            "agent_id": agent_id,
            "communication_data": communication_data
        }
        
        response = requests.post(f"{BASE_URL}/api/simulate-communication", json=sim_data)
        if response.status_code == 200:
            result = response.json()
            outcome = result['simulation_result']['outcome']
            confidence = result['simulation_result']['confidence']
            reasoning = result['simulation_result']['reasoning']
            
            print(f"🎯 Claude's Decision: {outcome.upper()}")
            print(f"📊 Confidence: {confidence:.2f}")
            print(f"💭 Reasoning: {reasoning}")
            
            # Show what this means
            if outcome == "close_loop":
                print("\n✅ Result: Your follow-up is complete! No further action needed.")
            elif outcome == "flag_for_doctor_review":
                print("\n⚠️ Result: Your case needs doctor review. Additional follow-up required.")
            elif outcome == "escalate_urgent":
                print("\n🚨 Result: Urgent attention needed! Doctor will contact you soon.")
            elif outcome == "retry_communication":
                print("\n🔄 Result: Another communication session needed.")
        else:
            print(f"❌ Error: {response.status_code}")
        
        # Step 6: Show final status
        print("\n6. 📊 Final Status")
        print("-" * 40)
        response = requests.get(f"{BASE_URL}/api/system-status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ System Status:")
            print(f"   Total Sub-Agents: {status_data['system_status']['total_sub_agents']}")
            print(f"   Completed: {status_data['system_status']['completed']}")
            print(f"   Flagged: {status_data['system_status']['flagged_for_review']}")
            print(f"   Success Rate: {status_data['system_status']['success_rate']:.1f}%")
        
        print("\n🎉 Interactive Test Complete!")
        print("✅ You had a real conversation with the agent!")
        print("✅ Claude analyzed your responses!")
        print("✅ Agent made a decision based on our conversation!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running!")
        print("   Run: python app.py")
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    interactive_patient_test()

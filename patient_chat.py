"""
Patient Chat Interface
Command-line chat interface for interacting with sub-agents
"""
import requests
import json
import time
import os
import sys

class PatientChat:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.current_agent = None
        self.conversation_history = []
        
    def list_agents(self):
        """List all available sub-agents."""
        try:
            response = requests.get(f"{self.base_url}/api/sub-agents")
            if response.status_code == 200:
                data = response.json()
                agents = data.get('sub_agents', [])
                
                if not agents:
                    print("❌ No sub-agents available. Create some first!")
                    return []
                
                print("\n🤖 Available Sub-Agents:")
                print("=" * 50)
                for i, agent in enumerate(agents, 1):
                    print(f"{i}. {agent.get('agent_id', 'Unknown')}")
                    print(f"   Patient: {agent.get('patient_name', 'Unknown')}")
                    print(f"   Status: {agent.get('status', 'Unknown')}")
                    print()
                
                return agents
            else:
                print(f"❌ Error fetching agents: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return []
    
    def select_agent(self, agents):
        """Select an agent to chat with."""
        while True:
            try:
                choice = input("Enter agent number (or 'q' to quit): ").strip()
                if choice.lower() == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < len(agents):
                    return agents[index]
                else:
                    print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def start_conversation(self, agent):
        """Start a conversation with the selected agent."""
        self.current_agent = agent
        agent_id = agent['agent_id']
        
        print(f"\n💬 Starting conversation with {agent['patient_name']}")
        print(f"🆔 Agent ID: {agent_id}")
        print("=" * 50)
        
        # Get initial message from agent
        try:
            response = requests.post(f"{self.base_url}/api/conversation/start", 
                                   json={"agent_id": agent_id})
            if response.status_code == 200:
                data = response.json()
                agent_message = data.get('agent_message', 'Hello!')
                print(f"\n🤖 Agent: {agent_message}")
                self.conversation_history.append({"role": "agent", "message": agent_message})
            else:
                print(f"❌ Error starting conversation: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Start chat loop
        self.chat_loop(agent_id)
    
    def chat_loop(self, agent_id):
        """Main chat loop."""
        print("\n💡 Type your message as the patient (or 'quit' to exit):")
        print("-" * 50)
        
        while True:
            try:
                # Get patient input
                patient_message = input("\n👤 You (as patient): ").strip()
                
                if patient_message.lower() in ['quit', 'exit', 'q']:
                    print("👋 Ending conversation...")
                    break
                
                if not patient_message:
                    continue
                
                # Send message to agent
                response = requests.post(f"{self.base_url}/api/conversation/respond",
                                       json={
                                           "agent_id": agent_id,
                                           "patient_message": patient_message
                                       })
                
                if response.status_code == 200:
                    data = response.json()
                    agent_response = data.get('agent_message', 'I understand.')
                    should_terminate = data.get('should_terminate', False)
                    termination_reason = data.get('termination_reason', '')
                    
                    # Store conversation
                    self.conversation_history.append({"role": "patient", "message": patient_message})
                    self.conversation_history.append({"role": "agent", "message": agent_response})
                    
                    # Display agent response
                    print(f"\n🤖 Agent: {agent_response}")
                    
                    # Check if conversation should end
                    if should_terminate:
                        print(f"\n📊 Conversation ended: {termination_reason}")
                        break
                else:
                    print(f"❌ Error: {response.status_code}")
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                break
    
    def show_conversation_summary(self):
        """Show conversation summary."""
        if not self.conversation_history:
            return
        
        print("\n📋 Conversation Summary:")
        print("=" * 50)
        for i, msg in enumerate(self.conversation_history, 1):
            role = "Agent" if msg["role"] == "agent" else "Patient"
            print(f"{i}. {role}: {msg['message']}")
        print("=" * 50)
    
    def run(self):
        """Main run loop."""
        print("🏥 Patient Chat Interface")
        print("=" * 50)
        
        while True:
            print("\n📋 Options:")
            print("1. List sub-agents")
            print("2. Chat with patient")
            print("3. Show conversation summary")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                agents = self.list_agents()
            elif choice == '2':
                agents = self.list_agents()
                if agents:
                    agent = self.select_agent(agents)
                    if agent:
                        self.start_conversation(agent)
            elif choice == '3':
                self.show_conversation_summary()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main function."""
    print("🚀 Starting Patient Chat Interface...")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8080/api/system-status", timeout=5)
        if response.status_code != 200:
            print("❌ Flask server not responding!")
            print("   Please start the server: python app.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server!")
        print("   Please start the server: python app.py")
        return
    
    # Start chat interface
    chat = PatientChat()
    chat.run()

if __name__ == "__main__":
    main()

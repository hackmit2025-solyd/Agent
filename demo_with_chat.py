"""
Demo with Patient Chat Interface
Shows the complete workflow with interactive patient chat
"""
import requests
import json
import time
import subprocess
import sys

def demo_workflow():
    """Run the complete demo workflow."""
    print("🏥 Healthcare Agent System - Complete Demo with Chat")
    print("=" * 60)
    
    # Step 1: Check servers
    print("\n1. 🔍 Checking servers...")
    try:
        response = requests.get("http://localhost:8080/api/system-status", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running")
        else:
            print("❌ Flask server not responding")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Flask server not running")
        print("   Please start: python app.py")
        return
    
    # Step 2: Submit doctor query
    print("\n2. 🩺 Submitting doctor query...")
    query = "Follow up with all patients who I saw 4 days ago"
    print(f"   Query: {query}")
    
    try:
        response = requests.get(f"http://localhost:8080/api/healthcare-query?query={query}", stream=True)
        if response.status_code == 200:
            print("✅ Query submitted successfully!")
            
            # Process streaming response
            agents_created = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            status = data.get('status', 'unknown')
                            message = data.get('message', '')
                            
                            if status == 'agent_created':
                                agent_id = data.get('agent_id', 'Unknown')
                                agents_created.append(agent_id)
                                print(f"   🤖 Created agent: {agent_id}")
                            elif status == 'completed':
                                print(f"   ✅ {message}")
                                break
                        except json.JSONDecodeError:
                            pass
        else:
            print(f"❌ Error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 3: Show available agents
    print("\n3. 🤖 Available Sub-Agents:")
    try:
        response = requests.get("http://localhost:8080/api/sub-agents")
        if response.status_code == 200:
            data = response.json()
            agents = data.get('sub_agents', [])
            
            for i, agent in enumerate(agents, 1):
                print(f"   {i}. {agent.get('agent_id', 'Unknown')}")
                print(f"      Patient: {agent.get('patient_name', 'Unknown')}")
                print(f"      Status: {agent.get('status', 'Unknown')}")
        else:
            print(f"❌ Error fetching agents: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Step 4: Launch chat interface
    print("\n4. 💬 Launching Patient Chat Interface...")
    print("   This will open a new window for patient conversations.")
    
    try:
        # Launch chat in new console window
        subprocess.Popen([sys.executable, "patient_chat.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        print("✅ Chat interface launched!")
        print("\n📋 Instructions:")
        print("   1. In the chat window, select 'List sub-agents'")
        print("   2. Choose an agent to chat with")
        print("   3. Type messages as the patient")
        print("   4. See the AI agent respond intelligently")
        print("   5. Type 'quit' to end conversation")
        
    except Exception as e:
        print(f"❌ Error launching chat: {e}")
        print("   You can manually run: python patient_chat.py")
    
    print("\n🎉 Demo complete!")
    print("=" * 60)
    print("✅ Doctor query processed")
    print("✅ Sub-agents created")
    print("✅ Chat interface launched")
    print("✅ Ready for patient conversations!")

if __name__ == "__main__":
    demo_workflow()

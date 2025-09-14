"""
Test the streaming healthcare query API
Demonstrates live streaming of processing state
"""
import requests
import json
import time

def test_streaming_api():
    """Test the streaming healthcare query API."""
    print("🌐 Testing Streaming Healthcare Query API")
    print("=" * 50)
    
    # Test query
    query = "Follow up with all diabetic patients from last week who have been experiencing vision problems"
    url = f"http://localhost:8080/api/healthcare-query?query={query}"
    
    print(f"📝 Query: {query}")
    print(f"🔗 URL: {url}")
    print("\n🔄 Starting live stream...")
    print("-" * 50)
    
    try:
        # Make streaming request
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            print("✅ Connection established!")
            print("📡 Live stream started...\n")
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                            
                            # Display status update
                            status = data.get('status', 'unknown')
                            message = data.get('message', '')
                            
                            # Format output based on status
                            if status == 'started':
                                print(f"🚀 {message}")
                            elif status == 'parsing':
                                print(f"🧠 {message}")
                            elif status == 'parsed':
                                print(f"✅ {message}")
                                if 'criteria' in data:
                                    criteria = data['criteria']
                                    print(f"   📋 Action: {criteria.get('action', 'N/A')}")
                                    print(f"   📋 Time Filter: {criteria.get('time_filter', 'N/A')}")
                            elif status == 'database':
                                print(f"🗄️ {message}")
                            elif status == 'database_found':
                                print(f"✅ {message}")
                                if 'patients' in data:
                                    for patient in data['patients']:
                                        print(f"   👤 {patient.get('name', 'Unknown')} - {', '.join(patient.get('medical_history', []))}")
                            elif status == 'creating_agents':
                                print(f"🤖 {message}")
                            elif status == 'agent_created':
                                print(f"✅ {message}")
                                if 'agent_id' in data:
                                    print(f"   🆔 Agent ID: {data['agent_id']}")
                            elif status == 'starting_chat':
                                print(f"💬 {message}")
                                if 'agent_id' in data:
                                    print(f"   🆔 Agent ID: {data['agent_id']}")
                            elif status == 'agent_message':
                                print(f"\n🤖 Agent ({data.get('patient_name', 'Unknown')}): {message}")
                            elif status == 'patient_message':
                                print(f"👤 Patient: {message}")
                            elif status == 'agent_response':
                                print(f"🤖 Agent: {message}")
                            elif status == 'conversation_ended':
                                print(f"📊 {message}")
                            elif status == 'completed':
                                print(f"🎉 {message}")
                                if 'agents' in data:
                                    print(f"   📊 Total Agents: {data.get('total_agents', 0)}")
                                    for agent in data['agents']:
                                        print(f"   🤖 {agent.get('agent_id', 'Unknown')} - {agent.get('patient_name', 'Unknown')}")
                            elif status == 'done':
                                print(f"✨ {message}")
                                print("\n🎉 Stream completed successfully!")
                                break
                            else:
                                print(f"📝 {message}")
                                
                        except json.JSONDecodeError as e:
                            print(f"❌ Error parsing JSON: {e}")
                            print(f"   Raw line: {line_str}")
                    else:
                        print(f"📝 Raw: {line_str}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask server is running!")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_streaming_api()

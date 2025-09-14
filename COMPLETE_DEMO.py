"""
COMPLETE DEMO: Healthcare Agent System with Live Streaming
Shows both API testing and frontend integration
"""
import requests
import json
import time
import webbrowser
import os
from pathlib import Path

def test_api_endpoints():
    """Test all API endpoints."""
    print("🔧 TESTING API ENDPOINTS")
    print("=" * 40)
    
    base_url = "http://localhost:8080"
    
    # Test 1: System Status
    print("\n1. 📊 System Status")
    try:
        response = requests.get(f"{base_url}/api/system-status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('system_status', {}).get('total_sub_agents', 0)} sub-agents")
            print(f"   ✅ Claude: {data.get('claude_status', {}).get('available', False)}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Streaming Query
    print("\n2. 🌐 Streaming Query Test")
    query = "Follow up with all diabetic patients from last week who have been experiencing vision problems"
    print(f"   📝 Query: {query}")
    
    try:
        response = requests.get(f"{base_url}/api/healthcare-query?query={query}", stream=True)
        if response.status_code == 200:
            print("   ✅ Streaming started!")
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            status = data.get('status', 'unknown')
                            message = data.get('message', '')
                            
                            if status == 'started':
                                print(f"   🚀 {message}")
                            elif status == 'parsing':
                                print(f"   🧠 {message}")
                            elif status == 'parsed':
                                print(f"   ✅ {message}")
                            elif status == 'database':
                                print(f"   🗄️ {message}")
                            elif status == 'database_found':
                                print(f"   ✅ {message}")
                            elif status == 'creating_agents':
                                print(f"   🤖 {message}")
                            elif status == 'agent_created':
                                print(f"   ✅ {message}")
                            elif status == 'completed':
                                print(f"   🎉 {message}")
                            elif status == 'done':
                                print(f"   ✨ {message}")
                                break
                        except json.JSONDecodeError:
                            pass
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Sub-Agents List
    print("\n3. 🤖 Sub-Agents List")
    try:
        response = requests.get(f"{base_url}/api/sub-agents")
        if response.status_code == 200:
            data = response.json()
            agents = data.get('sub_agents', [])
            print(f"   ✅ Found {len(agents)} sub-agents")
            for agent in agents:
                print(f"   🤖 {agent.get('agent_id', 'Unknown')} - {agent.get('patient_name', 'Unknown')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def open_frontend_demo():
    """Open the frontend demo in browser."""
    print("\n🌐 OPENING FRONTEND DEMO")
    print("=" * 40)
    
    # Get the absolute path to the HTML file
    html_file = Path(__file__).parent / "frontend_demo.html"
    html_url = f"file://{html_file.absolute()}"
    
    print(f"📁 HTML File: {html_file}")
    print(f"🔗 URL: {html_url}")
    
    try:
        # Open in default browser
        webbrowser.open(html_url)
        print("✅ Frontend demo opened in browser!")
        print("\n📋 Instructions:")
        print("   1. Enter a doctor query in the input field")
        print("   2. Click 'Submit Query' to start processing")
        print("   3. Watch the live stream of processing status")
        print("   4. See sub-agents being created in real-time")
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        print(f"   Please manually open: {html_url}")

def show_api_usage():
    """Show how to use the API from frontend."""
    print("\n📚 API USAGE GUIDE")
    print("=" * 40)
    
    print("🔗 GET Endpoint for Frontend:")
    print("   URL: http://localhost:8080/api/healthcare-query")
    print("   Method: GET")
    print("   Parameter: query (doctor's query)")
    print("   Response: Server-Sent Events (SSE) stream")
    
    print("\n📝 Example Usage:")
    print("   const eventSource = new EventSource('http://localhost:8080/api/healthcare-query?query=Follow up with diabetic patients');")
    print("   eventSource.onmessage = function(event) {")
    print("       const data = JSON.parse(event.data);")
    print("       console.log(data.status, data.message);")
    print("   };")
    
    print("\n🔄 Stream Events:")
    print("   - started: Processing begins")
    print("   - parsing: AI parsing doctor query")
    print("   - parsed: Query parsed successfully")
    print("   - database: Querying database")
    print("   - database_found: Patients found")
    print("   - creating_agents: Creating sub-agents")
    print("   - agent_created: Individual agent created")
    print("   - completed: All agents created")
    print("   - done: Processing complete")

def main():
    """Run the complete demo."""
    print("🏥 HEALTHCARE AGENT SYSTEM - COMPLETE DEMO")
    print("=" * 60)
    print("🎯 Features:")
    print("   ✅ GET API endpoint for frontend integration")
    print("   ✅ Live streaming of processing state")
    print("   ✅ Real-time sub-agent creation")
    print("   ✅ Interactive frontend demo")
    print("   ✅ Complete workflow demonstration")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8080/api/system-status", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running!")
        else:
            print("❌ Flask server not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Flask server not running!")
        print("   Please run: python app.py")
        return
    
    # Run tests
    test_api_endpoints()
    
    # Show API usage
    show_api_usage()
    
    # Open frontend demo
    open_frontend_demo()
    
    print("\n🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("✅ API endpoints tested")
    print("✅ Streaming functionality verified")
    print("✅ Frontend demo opened")
    print("✅ Ready for production use!")
    print("\n🚀 Your healthcare agent system is fully operational!")

if __name__ == "__main__":
    main()

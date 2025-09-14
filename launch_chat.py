"""
Launch Patient Chat Interface
Automatically opens chat when sub-agents are created
"""
import subprocess
import time
import requests
import sys

def check_servers():
    """Check if servers are running."""
    print("🔍 Checking servers...")
    
    # Check Flask server
    try:
        response = requests.get("http://localhost:8080/api/system-status", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running")
        else:
            print("❌ Flask server not responding")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask server not running")
        return False
    
    # Check Database server
    try:
        response = requests.get("http://localhost:3000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Database server is running")
        else:
            print("❌ Database server not responding")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Database server not running")
        return False
    
    return True

def start_servers():
    """Start the required servers."""
    print("🚀 Starting servers...")
    
    # Start Flask server
    print("   Starting Flask server...")
    subprocess.Popen(["python", "app.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(3)
    
    # Start Database server
    print("   Starting Database server...")
    subprocess.Popen(["python", "mock_database_service.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(2)
    
    print("✅ Servers started!")

def main():
    """Main function."""
    print("🏥 Healthcare Agent Chat Launcher")
    print("=" * 50)
    
    # Check if servers are running
    if not check_servers():
        print("\n🔧 Starting servers...")
        start_servers()
        
        # Wait a bit for servers to fully start
        print("⏳ Waiting for servers to start...")
        time.sleep(5)
        
        # Check again
        if not check_servers():
            print("❌ Failed to start servers. Please start manually:")
            print("   Terminal 1: python app.py")
            print("   Terminal 2: python mock_database_service.py")
            return
    
    print("\n🎯 Starting Patient Chat Interface...")
    print("=" * 50)
    
    # Launch chat interface
    try:
        subprocess.run([sys.executable, "patient_chat.py"])
    except KeyboardInterrupt:
        print("\n👋 Chat launcher stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

"""
Feasibility test for webhook reception from LiveKit server.
Tests whether the agent can successfully receive POST requests with voice data.
"""
import requests
import json
import time
import threading
import subprocess
import sys
from datetime import datetime


class WebhookReceptionTest:
    """Test class for webhook reception functionality."""
    
    def __init__(self, webhook_url="http://localhost:8000"):
        self.webhook_url = webhook_url
        self.test_results = []
    
    def test_basic_webhook_reception(self):
        """Test basic webhook endpoint availability."""
        print("Testing basic webhook reception...")
        
        try:
            response = requests.get(f"{self.webhook_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Webhook server is running and accessible")
                return True
            else:
                print(f"❌ Webhook server returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to webhook server: {str(e)}")
            return False
    
    def test_voice_data_webhook(self):
        """Test sending voice data to the webhook endpoint."""
        print("\nTesting voice data webhook...")
        
        # Sample voice data payload
        test_payload = {
            "session_id": "test_session_001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "audio_url": "https://example.com/audio/test_recording.wav",
            "transcript": "Hello doctor, I am experiencing some chest pain and shortness of breath.",
            "participant_id": "patient_12345",
            "duration": 15.7,
            "metadata": {
                "room_id": "consultation_room_1",
                "doctor_id": "dr_smith_456"
            }
        }
        
        try:
            response = requests.post(
                f"{self.webhook_url}/webhook/voice-data",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Voice data webhook test successful")
                print(f"   Response: {json.dumps(result, indent=2)}")
                return True
            else:
                print(f"❌ Voice data webhook failed with status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Voice data webhook request failed: {str(e)}")
            return False
    
    def test_raw_webhook(self):
        """Test sending raw data to webhook endpoint."""
        print("\nTesting raw webhook reception...")
        
        test_data = {
            "event_type": "call_ended",
            "session_id": "test_raw_001",
            "raw_audio_data": "base64_encoded_audio_data_here",
            "custom_headers": {
                "X-LiveKit-Event": "call_ended",
                "X-Session-Duration": "120"
            }
        }
        
        try:
            response = requests.post(
                f"{self.webhook_url}/webhook/raw",
                json=test_data,
                headers={
                    "Content-Type": "application/json",
                    "X-LiveKit-Event": "call_ended",
                    "X-Test-Header": "webhook_test"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Raw webhook test successful")
                print(f"   Response: {json.dumps(result, indent=2)}")
                return True
            else:
                print(f"❌ Raw webhook failed with status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Raw webhook request failed: {str(e)}")
            return False
    
    def test_webhook_error_handling(self):
        """Test webhook error handling with invalid data."""
        print("\nTesting webhook error handling...")
        
        # Send invalid data
        invalid_payload = {
            "invalid_field": "test",
            # Missing required fields
        }
        
        try:
            response = requests.post(
                f"{self.webhook_url}/webhook/voice-data",
                json=invalid_payload,
                timeout=10
            )
            
            if response.status_code == 422:  # FastAPI validation error
                print("✅ Webhook properly handles invalid data with 422 status")
                return True
            elif response.status_code >= 400:
                print(f"✅ Webhook properly returns error status: {response.status_code}")
                return True
            else:
                print(f"❌ Webhook should reject invalid data but returned: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error handling test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all webhook reception tests."""
        print("[TEST] Starting Webhook Reception Feasibility Tests")
        print("=" * 60)
        
        tests = [
            ("Basic Webhook Reception", self.test_basic_webhook_reception),
            ("Voice Data Webhook", self.test_voice_data_webhook),
            ("Raw Webhook Reception", self.test_raw_webhook),
            ("Error Handling", self.test_webhook_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n[RUN] {test_name}")
            print("-" * 30)
            
            try:
                result = test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"[RESULT] Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("[SUCCESS] All webhook reception tests passed!")
            print("[CONFIRMED] FEASIBILITY: Agent can receive webhooks from external server")
        else:
            print("⚠️  Some tests failed. Check webhook server setup.")
        
        return passed == total


def start_webhook_server():
    """Start the webhook server for testing."""
    print("Starting webhook server for testing...")
    try:
        # Start the webhook server in the background
        process = subprocess.Popen([
            sys.executable, "-m", "services.webhook_receiver"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give the server time to start
        time.sleep(3)
        
        return process
    except Exception as e:
        print(f"Failed to start webhook server: {str(e)}")
        return None


def main():
    """Main test execution."""
    print("[TEST] Webhook Reception Feasibility Test")
    print("This test verifies that a Fetch.ai agent can receive webhooks from external services.")
    print()
    
    # Check if server is already running
    test = WebhookReceptionTest()
    if not test.test_basic_webhook_reception():
        print("⚠️  Webhook server not detected. Attempting to start it...")
        server_process = start_webhook_server()
        
        if server_process:
            print("✅ Webhook server started successfully")
            time.sleep(2)  # Additional time for startup
        else:
            print("❌ Failed to start webhook server automatically")
            print("Please run 'python -m services.webhook_receiver' in another terminal")
            return False
    
    # Run the tests
    result = test.run_all_tests()
    
    # Cleanup
    try:
        if 'server_process' in locals() and server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("\n🧹 Cleaned up test server")
    except:
        pass
    
    return result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

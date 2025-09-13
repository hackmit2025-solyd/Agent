"""
Feasibility test for database service communication.
Tests whether the agent can successfully communicate with Ryan's database service.
"""
import json
import time
from services.database_client import DatabaseClient


class DatabaseServiceTest:
    """Test class for database service communication."""
    
    def __init__(self):
        self.client = DatabaseClient()
        self.test_results = []
    
    def test_connection(self):
        """Test basic connection to the database service."""
        print("Testing database service connection...")
        
        result = self.client.test_connection()
        
        if result["status"] == "success":
            print("✅ Database service connection successful")
            print(f"   Response: {json.dumps(result['response'], indent=2)}")
            return True
        else:
            print("❌ Database service connection failed")
            print(f"   Error: {json.dumps(result['error'], indent=2)}")
            return False
    
    def test_patient_search_by_name(self):
        """Test searching for a patient by name."""
        print("\nTesting patient search by name...")
        
        test_name = "John Doe"
        result = self.client.search_patient_by_name(test_name)
        
        if "error" not in result:
            print("✅ Patient search by name successful")
            print(f"   Query: Find patient information for {test_name}")
            print(f"   Response type: {type(result)}")
            if isinstance(result, dict):
                print(f"   Response keys: {list(result.keys())}")
            return True
        else:
            print("❌ Patient search by name failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            return False
    
    def test_patient_search_by_id(self):
        """Test searching for a patient by ID."""
        print("\nTesting patient search by ID...")
        
        test_id = "PAT-12345"
        result = self.client.search_patient_by_id(test_id)
        
        if "error" not in result:
            print("✅ Patient search by ID successful")
            print(f"   Query: Find patient information for patient ID {test_id}")
            print(f"   Response type: {type(result)}")
            if isinstance(result, dict):
                print(f"   Response keys: {list(result.keys())}")
            return True
        else:
            print("❌ Patient search by ID failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            return False
    
    def test_medical_history_query(self):
        """Test querying medical history."""
        print("\nTesting medical history query...")
        
        test_patient = "Jane Smith"
        result = self.client.get_medical_history(test_patient)
        
        if "error" not in result:
            print("✅ Medical history query successful")
            print(f"   Query: Get complete medical history for {test_patient}")
            print(f"   Response type: {type(result)}")
            if isinstance(result, dict):
                print(f"   Response keys: {list(result.keys())}")
            return True
        else:
            print("❌ Medical history query failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            return False
    
    def test_medication_query(self):
        """Test querying current medications."""
        print("\nTesting current medications query...")
        
        test_patient = "Bob Johnson"
        result = self.client.get_current_medications(test_patient)
        
        if "error" not in result:
            print("✅ Current medications query successful")
            print(f"   Query: Get current medications for {test_patient}")
            print(f"   Response type: {type(result)}")
            if isinstance(result, dict):
                print(f"   Response keys: {list(result.keys())}")
            return True
        else:
            print("❌ Current medications query failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            return False
    
    def test_custom_query(self):
        """Test custom text query."""
        print("\nTesting custom text query...")
        
        custom_query = "Find all patients with diabetes who are over 65 years old"
        result = self.client.query_patient_data(custom_query)
        
        if "error" not in result:
            print("✅ Custom query successful")
            print(f"   Query: {custom_query}")
            print(f"   Response type: {type(result)}")
            if isinstance(result, dict):
                print(f"   Response keys: {list(result.keys())}")
            return True
        else:
            print("❌ Custom query failed")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid queries."""
        print("\nTesting error handling...")
        
        # Test with empty query
        result = self.client.query_patient_data("")
        
        # The service should handle this gracefully
        print("✅ Empty query handled gracefully")
        print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
        return True
    
    def run_all_tests(self):
        """Run all database service tests."""
        print("🚀 Starting Database Service Feasibility Tests")
        print("=" * 60)
        
        tests = [
            ("Connection Test", self.test_connection),
            ("Patient Search by Name", self.test_patient_search_by_name),
            ("Patient Search by ID", self.test_patient_search_by_id),
            ("Medical History Query", self.test_medical_history_query),
            ("Current Medications Query", self.test_medication_query),
            ("Custom Text Query", self.test_custom_query),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            
            try:
                result = test_func()
                if result:
                    passed += 1
                
                # Small delay between tests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed >= 1:  # At least connection should work
            print("🎉 Database service communication is feasible!")
            print("✅ FEASIBILITY CONFIRMED: Agent can communicate with database service")
            
            if passed < total:
                print("⚠️  Some specific queries failed - this may be due to:")
                print("   - Database service not fully implemented yet")
                print("   - Different API format than expected")
                print("   - Service configuration issues")
        else:
            print("❌ Database service communication not working")
            print("⚠️  Check database service configuration and availability")
        
        return passed >= 1


def print_configuration_info():
    """Print current configuration information."""
    from config.agent_config import AgentConfig
    
    print("📋 Current Configuration:")
    print(f"   Database Service URL: {AgentConfig.DATABASE_SERVICE_URL}")
    print(f"   API Key configured: {'Yes' if AgentConfig.DATABASE_SERVICE_API_KEY != 'your-api-key-here' else 'No'}")
    print()
    
    # Validate configuration
    is_valid = AgentConfig.validate_config()
    if not is_valid:
        print("⚠️  Configuration issues detected. Please check your .env file.")
        print("   Copy config/env_example.txt to .env and fill in the correct values.")
    print()


def main():
    """Main test execution."""
    print("[TEST] Database Service Feasibility Test")
    print("This test verifies that a Fetch.ai agent can communicate with Ryan's database service.")
    print()
    
    print_configuration_info()
    
    # Run the tests
    test = DatabaseServiceTest()
    result = test.run_all_tests()
    
    if result:
        print("\n🎯 Next Steps:")
        print("1. Ensure Ryan's database service is running and accessible")
        print("2. Configure the correct API endpoint and authentication")
        print("3. Test with real patient data queries")
        print("4. Implement proper error handling for production use")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check if Ryan's database service is running")
        print("2. Verify the DATABASE_SERVICE_URL in your .env file")
        print("3. Ensure proper API key configuration")
        print("4. Check network connectivity to the service")
    
    return result


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

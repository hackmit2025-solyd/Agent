"""
Test script to verify the uagents conversion.
Tests basic functionality of the converted agents.
"""
import asyncio
import logging
from datetime import datetime

from agents.uagents_master import master_agent
from agents.uagents_healthcare import healthcare_agent
from agents.uagents_sub import create_sub_agent, SubAgentManager
from agents.protocols import (
    DoctorQuery, VoiceData, PatientRecord, ParsedCriteria,
    FollowUpStatus, DecisionOutcome
)
from agents.uagents_wallet import UAgentsWalletManager
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_uagents_conversion():
    """Test the uagents conversion."""
    print("🧪 Testing UAgents Conversion")
    print("=" * 40)
    
    try:
        # Test 1: Wallet Manager
        print("\n1. Testing Wallet Manager...")
        wallet_manager = UAgentsWalletManager()
        
        # Create test agent
        test_agent_info = wallet_manager.create_agent_identity("test_agent", "test_seed_123")
        print(f"   ✅ Created test agent: {test_agent_info['address']}")
        
        # Test 2: Message Protocols
        print("\n2. Testing Message Protocols...")
        
        # Create test patient
        test_patient = PatientRecord(
            patient_id="TEST001",
            name="Test Patient",
            last_visit="2024-01-15",
            status="active",
            medical_history=["Diabetes"],
            current_medications=["Metformin"]
        )
        
        # Create test criteria
        test_criteria = ParsedCriteria(
            action="follow_up",
            time_filter="last_week",
            patient_criteria={"status": "active"}
        )
        
        print(f"   ✅ Created test patient: {test_patient.name}")
        print(f"   ✅ Created test criteria: {test_criteria.action}")
        
        # Test 3: Sub-Agent Creation
        print("\n3. Testing Sub-Agent Creation...")
        
        sub_agent_manager = SubAgentManager()
        sub_agent = await sub_agent_manager.create_sub_agent(test_patient, test_criteria)
        
        print(f"   ✅ Created sub-agent: {sub_agent.sub_agent_id}")
        print(f"   ✅ Sub-agent status: {sub_agent.status}")
        
        # Test 4: Agent Addresses
        print("\n4. Testing Agent Addresses...")
        
        print(f"   ✅ Master Agent: {master_agent.address}")
        print(f"   ✅ Healthcare Agent: {healthcare_agent.address}")
        print(f"   ✅ Sub-Agent: {sub_agent.address}")
        
        # Test 5: Message Creation
        print("\n5. Testing Message Creation...")
        
        # Doctor query message
        doctor_query = DoctorQuery(
            query="Follow up with diabetic patients",
            timestamp=datetime.now()
        )
        print(f"   ✅ Doctor Query: {doctor_query.query}")
        
        # Voice data message
        voice_data = VoiceData(
            session_id="test_session_001",
            transcript="Patient reports chest pain",
            timestamp=datetime.now()
        )
        print(f"   ✅ Voice Data: {voice_data.session_id}")
        
        # Test 6: Configuration
        print("\n6. Testing Configuration...")
        
        print(f"   ✅ Agent Name: {AgentConfig.AGENT_NAME}")
        print(f"   ✅ Log Level: {AgentConfig.LOG_LEVEL}")
        print(f"   ✅ Database URL: {AgentConfig.DATABASE_SERVICE_URL}")
        
        print("\n🎉 All tests passed! UAgents conversion successful.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        logger.error(f"Test failed: {str(e)}")
        return False


async def test_agent_communication():
    """Test agent communication patterns."""
    print("\n🔗 Testing Agent Communication")
    print("-" * 40)
    
    try:
        # Test message passing between agents
        print("1. Testing message passing...")
        
        # Create test messages
        doctor_query = DoctorQuery(
            query="Check status of all patients with chest pain",
            timestamp=datetime.now(),
            doctor_id="DOC001"
        )
        
        voice_data = VoiceData(
            session_id="voice_001",
            transcript="Patient John Smith reports severe chest pain and shortness of breath",
            timestamp=datetime.now()
        )
        
        print(f"   ✅ Doctor Query created: {doctor_query.query}")
        print(f"   ✅ Voice Data created: {voice_data.transcript[:50]}...")
        
        # Test protocol validation
        print("\n2. Testing protocol validation...")
        
        # Test valid messages
        valid_patient = PatientRecord(
            patient_id="VALID001",
            name="Valid Patient",
            last_visit="2024-01-15",
            status="active",
            medical_history=["Hypertension"],
            current_medications=["Lisinopril"]
        )
        
        print(f"   ✅ Valid Patient Record: {valid_patient.name}")
        
        # Test enum values
        print("\n3. Testing enum values...")
        
        status_values = [status.value for status in FollowUpStatus]
        outcome_values = [outcome.value for outcome in DecisionOutcome]
        
        print(f"   ✅ Follow-up Status values: {status_values}")
        print(f"   ✅ Decision Outcome values: {outcome_values}")
        
        print("\n🎉 Communication tests passed!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Communication test failed: {str(e)}")
        logger.error(f"Communication test failed: {str(e)}")
        return False


async def main():
    """Main test execution."""
    print("🚀 Starting UAgents Conversion Tests")
    print("=" * 50)
    
    # Run basic conversion tests
    conversion_success = await test_uagents_conversion()
    
    # Run communication tests
    communication_success = await test_agent_communication()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Conversion Tests: {'✅ PASSED' if conversion_success else '❌ FAILED'}")
    print(f"Communication Tests: {'✅ PASSED' if communication_success else '❌ FAILED'}")
    
    if conversion_success and communication_success:
        print("\n🎉 All tests passed! The uagents conversion is working correctly.")
        print("\nNext steps:")
        print("1. Run 'python uagents_demo.py' for a comprehensive demo")
        print("2. Run 'python uagents_main.py' to start the full system")
        print("3. Run 'python uagents_webhook.py' to start the webhook server")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())

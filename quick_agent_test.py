"""
Quick Agent Test - Shows Expected Outputs
Demonstrates the healthcare agent system with expected outputs.
"""
import asyncio
import json
from datetime import datetime
from agents.master_agent import MasterAgent, PatientRecord, ParsedCriteria
from agents.sub_agent import SubAgent, SubAgentManager, FollowUpStatus, DecisionOutcome
from services.llm_service import llm_service


async def quick_agent_test():
    """Quick test showing expected outputs."""
    print("🤖 Quick Agent Test - Expected Outputs")
    print("=" * 60)
    
    # Initialize system
    master_agent = MasterAgent()
    sub_agent_manager = SubAgentManager()
    
    print("✅ System initialized")
    
    # Test 1: Master Agent Query Parsing
    print(f"\n📝 Test 1: Master Agent Query Parsing")
    print("-" * 40)
    
    doctor_query = "Follow up with all diabetic patients from last week who have been experiencing vision problems"
    print(f"Doctor Query: {doctor_query}")
    
    parsed = await master_agent.parse_doctor_query(doctor_query)
    print(f"Claude Parsed:")
    print(f"  Action: {parsed.action}")
    print(f"  Time Filter: {parsed.time_filter}")
    print(f"  Condition Filter: {parsed.condition_filter}")
    print(f"  Patient Criteria: {parsed.patient_criteria}")
    
    # Test 2: Patient Data
    print(f"\n👥 Test 2: Patient Data")
    print("-" * 40)
    
    patient = PatientRecord(
        patient_id="TEST001",
        name="John Smith",
        last_visit="2024-01-15",
        status="active",
        medical_history=["Diabetes Type 2", "Hypertension"],
        current_medications=["Metformin", "Lisinopril"],
        symptoms=["blurred vision", "fatigue"]
    )
    
    print(f"Patient: {patient.name}")
    print(f"History: {', '.join(patient.medical_history)}")
    print(f"Medications: {', '.join(patient.current_medications)}")
    print(f"Symptoms: {', '.join(patient.symptoms or [])}")
    
    # Test 3: Sub-Agent Creation
    print(f"\n🤖 Test 3: Sub-Agent Creation")
    print("-" * 40)
    
    context = ParsedCriteria(
        action="follow_up",
        time_filter="today",
        patient_criteria={"status": "active"}
    )
    
    sub_agent = await sub_agent_manager.create_sub_agent(patient, context)
    print(f"Sub-Agent Created: {sub_agent.sub_agent_id}")
    print(f"Patient: {sub_agent.patient_data.name}")
    print(f"Context: {sub_agent.master_context.action}")
    
    # Test 4: Communication Processing
    print(f"\n📞 Test 4: Communication Processing")
    print("-" * 40)
    
    print("Claude is processing communication...")
    result = await sub_agent.initiate_communication()
    
    print(f"Communication Result:")
    print(f"  Status: {result.status.value}")
    print(f"  Outcome: {result.outcome.value}")
    print(f"  Confidence: {result.confidence_score:.2f}")
    print(f"  Data Obtained: {len(result.data_obtained)} items")
    print(f"  Missing Data: {len(result.missing_data)} items")
    
    # Test 5: Claude's Decision
    print(f"\n🧠 Test 5: Claude's Decision")
    print("-" * 40)
    
    print(f"Decision: {result.outcome.value.upper()}")
    print(f"Reasoning: {result.notes[:200]}...")
    
    # Test 6: System Summary
    print(f"\n📊 Test 6: System Summary")
    print("-" * 40)
    
    status = sub_agent_manager.get_system_status()
    print(f"Total Sub-Agents: {status['total_sub_agents']}")
    print(f"Completed: {status['completed']}")
    print(f"Flagged for Review: {status['flagged_for_review']}")
    print(f"Success Rate: {status['success_rate']:.1f}%")
    
    print(f"\n🎉 Quick Agent Test Complete!")
    print("✅ All systems operational with Claude!")


if __name__ == "__main__":
    asyncio.run(quick_agent_test())

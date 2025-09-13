"""
Phase 3 Decision Logic Test
Tests all possible decision outcomes for sub-agent communication.
"""
import asyncio
from agents.sub_agent import SubAgent, SubAgentManager, FollowUpStatus, DecisionOutcome
from agents.master_agent import PatientRecord, ParsedCriteria


async def test_all_decision_outcomes():
    """Test all possible decision outcomes."""
    print("🧠 Phase 3 Decision Logic Test - All Outcomes")
    print("=" * 60)
    
    # Test scenarios for different outcomes
    test_scenarios = [
        {
            "name": "Routine Follow-up (Close Loop)",
            "patient": PatientRecord(
                patient_id="ROUTINE001",
                name="Alice Wilson",
                last_visit="2024-01-15",
                status="active",
                medical_history=["Hypertension"],
                current_medications=["Lisinopril"],
                symptoms=["mild headache"]
            ),
            "context": ParsedCriteria(action="follow_up", time_filter="today", patient_criteria={"status": "active"}),
            "expected": "CLOSE_LOOP"
        },
        {
            "name": "Urgent Condition (Escalate)",
            "patient": PatientRecord(
                patient_id="URGENT001",
                name="Bob Davis",
                last_visit="2024-01-15",
                status="active",
                medical_history=["Heart Disease"],
                current_medications=["Atorvastatin"],
                symptoms=["chest pain", "shortness of breath"]
            ),
            "context": ParsedCriteria(action="review", time_filter="today", patient_criteria={"status": "active"}),
            "expected": "ESCALATE_URGENT"
        },
        {
            "name": "Incomplete Data (Flag for Review)",
            "patient": PatientRecord(
                patient_id="INCOMPLETE001",
                name="Carol Brown",
                last_visit="2024-01-15",
                status="active",
                medical_history=["Diabetes Type 2"],
                current_medications=["Metformin"],
                symptoms=["fatigue", "blurred vision"]
            ),
            "context": ParsedCriteria(action="check_status", time_filter="today", patient_criteria={"status": "active"}),
            "expected": "FLAG_FOR_DOCTOR_REVIEW"
        }
    ]
    
    manager = SubAgentManager()
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test {i}: {scenario['name']}")
        print("-" * 50)
        
        # Create sub-agent
        sub_agent = await manager.create_sub_agent(scenario["patient"], scenario["context"])
        
        print(f"👤 Patient: {sub_agent.patient_data.name}")
        print(f"🏥 History: {', '.join(sub_agent.patient_data.medical_history)}")
        print(f"💊 Symptoms: {', '.join(sub_agent.patient_data.symptoms)}")
        print(f"🎯 Action: {sub_agent.master_context.action}")
        
        # Process communication
        print("📞 Processing communication...")
        result = await sub_agent.initiate_communication()
        
        # Show results
        print(f"\n📊 Results:")
        print(f"   Status: {result.status.value}")
        print(f"   Outcome: {result.outcome.value}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        print(f"   Data Points: {len(result.data_obtained)}")
        print(f"   Missing Data: {len(result.missing_data)}")
        
        # Show decision reasoning
        print(f"\n🧠 Decision Analysis:")
        if result.outcome == DecisionOutcome.CLOSE_LOOP:
            print("   ✅ All required information obtained")
            print("   ✅ High confidence in communication")
            print("   ✅ No urgent conditions detected")
        elif result.outcome == DecisionOutcome.ESCALATE_URGENT:
            print("   ⚠️  Urgent conditions detected")
            print("   🚨 Immediate doctor attention required")
            print("   📞 Patient safety priority")
        elif result.outcome == DecisionOutcome.FLAG_FOR_DOCTOR_REVIEW:
            print("   ⚠️  Missing critical information")
            print("   📋 Human review needed")
            print("   🔄 May require follow-up")
        
        # Check if outcome matches expectation
        expected_outcome = scenario["expected"]
        actual_outcome = result.outcome.value
        match = "✅" if actual_outcome == expected_outcome.lower() else "❌"
        
        print(f"\n{match} Expected: {expected_outcome}, Got: {actual_outcome.upper()}")
        
        results.append({
            "scenario": scenario["name"],
            "expected": expected_outcome,
            "actual": actual_outcome,
            "match": actual_outcome == expected_outcome.lower()
        })
        
        print("=" * 60)
    
    # Summary
    print(f"\n📈 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["match"])
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 Individual Results:")
    for result in results:
        status = "✅ PASS" if result["match"] else "❌ FAIL"
        print(f"   {status} {result['scenario']}")
    
    # System status
    system_status = manager.get_system_status()
    print(f"\n🤖 SYSTEM STATUS:")
    print(f"   Total Sub-Agents: {system_status['total_sub_agents']}")
    print(f"   Completed: {system_status['completed']}")
    print(f"   Flagged for Review: {system_status['flagged_for_review']}")
    print(f"   Failed: {system_status['failed']}")
    print(f"   Success Rate: {system_status['success_rate']:.1f}%")
    
    print(f"\n🎉 Phase 3 Decision Logic Test Complete!")


async def test_communication_flow():
    """Test the complete communication flow."""
    print("\n🔄 Communication Flow Test")
    print("=" * 40)
    
    # Create multiple patients
    patients = [
        PatientRecord(
            patient_id="FLOW001",
            name="Patient A",
            last_visit="2024-01-15",
            status="active",
            medical_history=["Diabetes"],
            current_medications=["Metformin"],
            symptoms=["fatigue"]
        ),
        PatientRecord(
            patient_id="FLOW002",
            name="Patient B",
            last_visit="2024-01-15",
            status="active",
            medical_history=["Hypertension"],
            current_medications=["Lisinopril"],
            symptoms=["headache"]
        )
    ]
    
    context = ParsedCriteria(
        action="follow_up",
        time_filter="today",
        patient_criteria={"status": "active"}
    )
    
    manager = SubAgentManager()
    
    # Create sub-agents
    sub_agents = []
    for patient in patients:
        sub_agent = await manager.create_sub_agent(patient, context)
        sub_agents.append(sub_agent)
        print(f"✅ Created sub-agent for {patient.name}")
    
    # Process all communications
    print(f"\n📞 Processing {len(sub_agents)} communications...")
    results = await manager.process_all_communications()
    
    print(f"\n📊 Communication Results:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result.patient_id}: {result.outcome.value} (Confidence: {result.confidence_score:.2f})")
    
    print(f"\n🎯 Communication Flow Test Complete!")


async def main():
    """Run all Phase 3 tests."""
    await test_all_decision_outcomes()
    await test_communication_flow()


if __name__ == "__main__":
    asyncio.run(main())

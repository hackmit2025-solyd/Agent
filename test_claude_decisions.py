"""
Test Claude's Decision Making
Shows Claude making all termination and flagging decisions.
"""
import asyncio
import os
from agents.sub_agent import SubAgent, SubAgentManager, FollowUpStatus, DecisionOutcome
from agents.master_agent import PatientRecord, ParsedCriteria
from services.llm_service import llm_service


async def test_claude_decision_making():
    """Test Claude making all the critical decisions."""
    print("🤖 Claude Decision Making Test")
    print("=" * 50)
    
    # Check if Claude is available
    if not llm_service.available:
        print("❌ Claude not available. Set ANTHROPIC_API_KEY to test real Claude decisions.")
        print("🔄 Testing with mock responses...")
    else:
        print("✅ Claude is available and ready to make decisions!")
    
    # Test scenarios with different patient conditions
    test_scenarios = [
        {
            "name": "Routine Diabetic Patient",
            "patient": PatientRecord(
                patient_id="CLAUDE001",
                name="Alice Johnson",
                last_visit="2024-01-15",
                status="active",
                medical_history=["Diabetes Type 2"],
                current_medications=["Metformin"],
                symptoms=["mild fatigue"]
            ),
            "expected": "Should be CLOSE_LOOP - routine follow-up"
        },
        {
            "name": "Urgent Cardiac Patient",
            "patient": PatientRecord(
                patient_id="CLAUDE002",
                name="Robert Smith",
                last_visit="2024-01-10",
                status="active",
                medical_history=["Heart Disease", "Hypertension"],
                current_medications=["Atorvastatin", "Aspirin"],
                symptoms=["chest pain", "shortness of breath", "dizziness"]
            ),
            "expected": "Should be ESCALATE_URGENT - cardiac symptoms"
        },
        {
            "name": "Complex Multi-Condition Patient",
            "patient": PatientRecord(
                patient_id="CLAUDE003",
                name="Maria Garcia",
                last_visit="2024-01-05",
                status="active",
                medical_history=["Diabetes Type 2", "Depression", "Hypertension"],
                current_medications=["Metformin", "Sertraline", "Lisinopril"],
                symptoms=["blurred vision", "mood changes", "fatigue"]
            ),
            "expected": "Should be FLAG_FOR_DOCTOR_REVIEW - complex case"
        },
        {
            "name": "Medication Safety Concern",
            "patient": PatientRecord(
                patient_id="CLAUDE004",
                name="James Wilson",
                last_visit="2024-01-12",
                status="active",
                medical_history=["Atrial Fibrillation"],
                current_medications=["Warfarin", "Digoxin"],
                symptoms=["unusual bruising", "nosebleeds", "gum bleeding"]
            ),
            "expected": "Should be ESCALATE_URGENT - bleeding on blood thinners"
        }
    ]
    
    manager = SubAgentManager()
    context = ParsedCriteria(
        action="follow_up",
        time_filter="today",
        patient_criteria={"status": "active"}
    )
    
    print(f"\n🧠 Testing Claude's Decision Making on {len(test_scenarios)} scenarios...")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['name']}")
        print(f"Patient: {scenario['patient'].name}")
        print(f"History: {', '.join(scenario['patient'].medical_history)}")
        print(f"Medications: {', '.join(scenario['patient'].current_medications)}")
        print(f"Symptoms: {', '.join(scenario['patient'].symptoms or [])}")
        print(f"Expected: {scenario['expected']}")
        print("-" * 40)
        
        # Create sub-agent
        sub_agent = await manager.create_sub_agent(scenario['patient'], context)
        print(f"🤖 Created sub-agent: {sub_agent.sub_agent_id}")
        
        # Let Claude process the communication and make decisions
        print("📞 Claude is processing communication and making decisions...")
        result = await sub_agent.initiate_communication()
        
        print(f"\n🎯 Claude's Decision:")
        print(f"   Outcome: {result.outcome.value.upper()}")
        print(f"   Status: {result.status.value}")
        print(f"   Confidence: {result.confidence_score:.2f}")
        
        print(f"\n💭 Claude's Reasoning:")
        print(f"   {result.notes}")
        
        # Check if Claude's decision matches expectation
        expected_outcome = scenario['expected'].split(' - ')[0].split()[-1].lower()
        if expected_outcome in result.outcome.value:
            print(f"✅ Claude's decision aligns with expectation!")
        else:
            print(f"⚠️  Claude's decision differs from expectation")
        
        print("=" * 60)
        await asyncio.sleep(1)  # Pause between scenarios
    
    # System summary
    status = manager.get_system_status()
    print(f"\n📊 Claude Decision Summary:")
    print(f"   Total Patients: {status['total_sub_agents']}")
    print(f"   Completed: {status['completed']}")
    print(f"   Flagged for Review: {status['flagged_for_review']}")
    print(f"   Success Rate: {status['success_rate']:.1f}%")
    
    print(f"\n🎉 Claude Decision Making Test Complete!")
    print("Claude is now making all critical healthcare decisions!")


async def test_claude_query_parsing():
    """Test Claude's intelligent query parsing."""
    print(f"\n🧠 Claude Query Parsing Test")
    print("=" * 40)
    
    complex_queries = [
        "Follow up with all diabetic patients from last week who have been experiencing vision problems and check if they're taking their Metformin properly",
        "URGENT: Find patients with heart disease who had chest pain in the past 3 days and are taking blood thinners",
        "Review all elderly patients over 70 with multiple medications to check for potential drug interactions",
        "Schedule follow-up appointments for patients with depression who haven't been seen in 2 months and are showing signs of worsening symptoms"
    ]
    
    for i, query in enumerate(complex_queries, 1):
        print(f"\n📝 Query {i}: {query}")
        print("-" * 30)
        
        # Parse with Claude
        parsed = await llm_service.parse_doctor_query(query)
        
        print(f"🎯 Claude Parsed:")
        print(f"   Action: {parsed.get('action', 'unknown')}")
        print(f"   Time Filter: {parsed.get('time_filter', 'none')}")
        print(f"   Condition Filter: {parsed.get('condition_filter', [])}")
        print(f"   Symptom Filter: {parsed.get('symptom_filter', [])}")
        print(f"   Patient Criteria: {parsed.get('patient_criteria', {})}")
        
        await asyncio.sleep(0.5)


async def main():
    """Run all Claude decision tests."""
    await test_claude_query_parsing()
    await test_claude_decision_making()


if __name__ == "__main__":
    asyncio.run(main())

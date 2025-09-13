"""
LLM-Powered Healthcare Agent System Demo
Shows the complete system with Claude integration for intelligent decision making.
"""
import asyncio
import json
from datetime import datetime
from agents.master_agent import MasterAgent, PatientRecord, ParsedCriteria
from agents.sub_agent import SubAgent, SubAgentManager, FollowUpStatus, DecisionOutcome
from services.llm_service import llm_service


class LLMHealthcareDemo:
    """Comprehensive demo of the LLM-powered healthcare agent system."""
    
    def __init__(self):
        self.master_agent = None
        self.sub_agent_manager = SubAgentManager()
    
    async def setup_system(self):
        """Initialize the master agent and system."""
        print("🤖 Initializing LLM-Powered Healthcare Agent System")
        print("=" * 60)
        
        # Initialize master agent
        self.master_agent = MasterAgent()
        print("✅ Master Agent initialized")
        
        # Check LLM availability
        if llm_service.available:
            print("✅ Claude LLM service available")
        else:
            print("⚠️  Claude LLM service not available (using mock responses)")
            print("   Set ANTHROPIC_API_KEY to enable real Claude responses")
        
        print("🚀 System ready for intelligent healthcare operations!")
    
    async def demo_intelligent_query_parsing(self):
        """Demonstrate intelligent query parsing with LLM."""
        print(f"\n🧠 INTELLIGENT QUERY PARSING DEMO")
        print("=" * 50)
        
        # Complex queries that show LLM intelligence
        complex_queries = [
            "Follow up with all diabetic patients from last week who have been experiencing vision problems and check if they're taking their Metformin properly",
            "Find patients with heart disease who had chest pain in the past 3 days and are taking blood thinners - this is urgent",
            "Review all elderly patients over 70 with multiple medications to check for potential drug interactions",
            "Schedule follow-up appointments for patients with depression who haven't been seen in 2 months and are showing signs of worsening symptoms"
        ]
        
        for i, query in enumerate(complex_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 40)
            
            # Parse with LLM
            parsed = await self.master_agent.parse_doctor_query(query)
            
            print(f"🎯 Parsed Action: {parsed.action}")
            print(f"⏰ Time Filter: {parsed.time_filter}")
            print(f"🏥 Condition Filter: {parsed.condition_filter}")
            print(f"💊 Symptom Filter: {parsed.symptom_filter}")
            print(f"👥 Patient Criteria: {parsed.patient_criteria}")
            
            await asyncio.sleep(1)  # Pause for readability
    
    async def demo_intelligent_communication(self):
        """Demonstrate intelligent communication generation."""
        print(f"\n💬 INTELLIGENT COMMUNICATION DEMO")
        print("=" * 50)
        
        # Create test patients with different scenarios
        test_patients = [
            {
                "patient_id": "DIABETIC001",
                "name": "Sarah Johnson",
                "medical_history": ["Diabetes Type 2", "Hypertension"],
                "current_medications": ["Metformin", "Lisinopril"],
                "symptoms": ["blurred vision", "fatigue", "frequent urination"]
            },
            {
                "patient_id": "CARDIAC001", 
                "name": "Robert Chen",
                "medical_history": ["Heart Disease", "High Cholesterol"],
                "current_medications": ["Atorvastatin", "Aspirin"],
                "symptoms": ["chest pain", "shortness of breath"]
            },
            {
                "patient_id": "ELDERLY001",
                "name": "Margaret Williams",
                "medical_history": ["Arthritis", "Osteoporosis", "Hypertension"],
                "current_medications": ["Ibuprofen", "Calcium", "Lisinopril", "Vitamin D"],
                "symptoms": ["joint pain", "mobility issues"]
            }
        ]
        
        for i, patient_data in enumerate(test_patients, 1):
            print(f"\n👤 Patient {i}: {patient_data['name']}")
            print(f"🏥 History: {', '.join(patient_data['medical_history'])}")
            print(f"💊 Medications: {', '.join(patient_data['current_medications'])}")
            print(f"🩺 Symptoms: {', '.join(patient_data['symptoms'])}")
            
            # Generate communication goals based on patient data
            if "diabetes" in [h.lower() for h in patient_data['medical_history']]:
                goals = [
                    "Check blood sugar control and recent readings",
                    "Assess vision problems and eye health",
                    "Review medication adherence and side effects",
                    "Discuss diet and lifestyle modifications"
                ]
            elif "heart" in [h.lower() for h in patient_data['medical_history']]:
                goals = [
                    "Assess chest pain severity and frequency",
                    "Check medication effectiveness and side effects",
                    "Review exercise tolerance and limitations",
                    "Discuss emergency action plan"
                ]
            else:
                goals = [
                    "General health status check",
                    "Medication review and adherence",
                    "Symptom assessment and management",
                    "Schedule next appointment"
                ]
            
            print(f"🎯 Communication Goals: {', '.join(goals)}")
            
            # Generate intelligent communication
            context = {"goals": goals}
            transcript = await llm_service.generate_communication_transcript(patient_data, context)
            
            print(f"\n📞 Generated Communication:")
            print(f"   Duration: {transcript.get('duration', 0):.1f} seconds")
            print(f"   Confidence: {transcript.get('confidence_score', 0.0):.2f}")
            print(f"   Quality: {transcript.get('conversation_quality', 'unknown')}")
            
            print(f"\n💬 Transcript Preview:")
            transcript_text = transcript.get('transcript', '')
            print(f"   {transcript_text[:300]}...")
            
            # Analyze outcome
            analysis = await llm_service.analyze_communication_outcome(transcript, patient_data)
            print(f"\n🧠 LLM Analysis:")
            print(f"   Outcome: {analysis.get('outcome', 'unknown').upper()}")
            print(f"   Reasoning: {analysis.get('reasoning', 'No reasoning provided')}")
            print(f"   Confidence: {analysis.get('confidence', 0.0):.2f}")
            
            if analysis.get('urgent_conditions'):
                print(f"   🚨 Urgent Conditions: {', '.join(analysis['urgent_conditions'])}")
            
            print("=" * 50)
            await asyncio.sleep(2)  # Pause between patients
    
    async def demo_sub_agent_workflow(self):
        """Demonstrate complete sub-agent workflow with LLM."""
        print(f"\n🤖 SUB-AGENT WORKFLOW DEMO")
        print("=" * 50)
        
        # Create master context
        context = ParsedCriteria(
            action="follow_up",
            time_filter="today",
            condition_filter="diabetes",
            patient_criteria={"status": "active"}
        )
        
        # Create test patients
        patients = [
            PatientRecord(
                patient_id="LLM001",
                name="Alice Thompson",
                last_visit="2024-01-15",
                status="active",
                medical_history=["Diabetes Type 2", "Diabetic Retinopathy"],
                current_medications=["Metformin", "Insulin"],
                symptoms=["blurred vision", "numbness in feet"]
            ),
            PatientRecord(
                patient_id="LLM002",
                name="David Rodriguez",
                last_visit="2024-01-10",
                status="active", 
                medical_history=["Diabetes Type 1", "Hypertension"],
                current_medications=["Insulin", "Lisinopril"],
                symptoms=["high blood sugar", "frequent urination"]
            )
        ]
        
        print(f"📋 Master Context: {context.action} - {context.condition_filter}")
        print(f"👥 Processing {len(patients)} patients...")
        
        # Create and process sub-agents
        for i, patient in enumerate(patients, 1):
            print(f"\n🤖 Sub-Agent {i}: {patient.name}")
            print("-" * 30)
            
            # Create sub-agent
            sub_agent = await self.sub_agent_manager.create_sub_agent(patient, context)
            print(f"✅ Created: {sub_agent.sub_agent_id}")
            
            # Process communication with LLM
            print("📞 Initiating LLM-powered communication...")
            result = await sub_agent.initiate_communication()
            
            print(f"📊 Results:")
            print(f"   Status: {result.status.value}")
            print(f"   Outcome: {result.outcome.value}")
            print(f"   Confidence: {result.confidence_score:.2f}")
            print(f"   Data Points: {len(result.data_obtained)}")
            print(f"   Missing Data: {len(result.missing_data)}")
            
            # Show decision reasoning
            print(f"🧠 Decision Reasoning:")
            print(f"   {result.notes}")
            
            await asyncio.sleep(1)
        
        # System summary
        status = self.sub_agent_manager.get_system_status()
        print(f"\n📈 System Summary:")
        print(f"   Total Sub-Agents: {status['total_sub_agents']}")
        print(f"   Completed: {status['completed']}")
        print(f"   Flagged for Review: {status['flagged_for_review']}")
        print(f"   Success Rate: {status['success_rate']:.1f}%")
    
    async def demo_advanced_scenarios(self):
        """Demonstrate advanced LLM scenarios."""
        print(f"\n🚀 ADVANCED LLM SCENARIOS DEMO")
        print("=" * 50)
        
        scenarios = [
            {
                "name": "Complex Multi-Condition Patient",
                "query": "Follow up with patients who have both diabetes and heart disease, are over 65, and have been experiencing new symptoms in the past week",
                "patient": {
                    "name": "Elena Petrov",
                    "medical_history": ["Diabetes Type 2", "Coronary Artery Disease", "Hypertension"],
                    "current_medications": ["Metformin", "Atorvastatin", "Aspirin", "Lisinopril"],
                    "symptoms": ["chest discomfort", "blurred vision", "fatigue"]
                }
            },
            {
                "name": "Urgent Medication Review",
                "query": "Urgently review all patients taking warfarin who have reported bleeding or bruising",
                "patient": {
                    "name": "James Wilson",
                    "medical_history": ["Atrial Fibrillation", "Deep Vein Thrombosis"],
                    "current_medications": ["Warfarin", "Digoxin"],
                    "symptoms": ["unusual bruising", "nosebleeds", "gum bleeding"]
                }
            }
        ]
        
        for scenario in scenarios:
            print(f"\n📋 Scenario: {scenario['name']}")
            print(f"Query: {scenario['query']}")
            print("-" * 40)
            
            # Parse complex query
            parsed = await self.master_agent.parse_doctor_query(scenario['query'])
            print(f"🎯 LLM Parsed: {parsed.action} - {parsed.condition_filter}")
            
            # Generate intelligent communication
            patient_data = scenario['patient']
            context = {"goals": ["Assess current condition", "Review medication safety", "Determine urgency"]}
            
            transcript = await llm_service.generate_communication_transcript(patient_data, context)
            print(f"💬 Generated {transcript.get('duration', 0):.1f}s conversation")
            
            # Analyze with LLM
            analysis = await llm_service.analyze_communication_outcome(transcript, patient_data)
            print(f"🧠 LLM Decision: {analysis.get('outcome', 'unknown').upper()}")
            print(f"💭 Reasoning: {analysis.get('reasoning', 'No reasoning')[:100]}...")
            
            # Generate patient summary
            summary = await llm_service.generate_patient_summary(patient_data, analysis)
            print(f"📄 LLM Summary Preview:")
            print(f"   {summary[:200]}...")
            
            print("=" * 50)
            await asyncio.sleep(2)
    
    async def run_complete_demo(self):
        """Run the complete LLM-powered demo."""
        try:
            await self.setup_system()
            await self.demo_intelligent_query_parsing()
            await self.demo_intelligent_communication()
            await self.demo_sub_agent_workflow()
            await self.demo_advanced_scenarios()
            
            print(f"\n🎉 LLM-POWERED HEALTHCARE AGENT DEMO COMPLETE!")
            print("=" * 60)
            print("✅ Intelligent query parsing with Claude")
            print("✅ Realistic communication generation")
            print("✅ Smart decision making and analysis")
            print("✅ Advanced medical scenario handling")
            print("✅ Comprehensive patient summaries")
            print("\n🚀 System ready for production deployment!")
            
        except Exception as e:
            print(f"\n❌ Demo error: {str(e)}")
            print("Please check your setup and try again.")


async def main():
    """Run the LLM healthcare demo."""
    demo = LLMHealthcareDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())

"""
Comprehensive demo of the uagents-based healthcare system.
Shows all agents working together with real examples.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from agents.uagents_master import master_agent
from agents.uagents_healthcare import healthcare_agent
from agents.uagents_sub import SubAgentManager, create_sub_agent
from agents.protocols import (
    DoctorQuery, VoiceData, PatientRecord, ParsedCriteria,
    FollowUpStatus, DecisionOutcome
)
from agents.uagents_wallet import UAgentsWalletManager
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)


class UAgentsHealthcareDemo:
    """Comprehensive demo of the uagents healthcare system."""
    
    def __init__(self):
        self.wallet_manager = UAgentsWalletManager()
        self.sub_agent_manager = SubAgentManager()
        self.demo_results = []
    
    async def run_complete_demo(self):
        """Run the complete healthcare system demo."""
        print("🏥 UAgents Healthcare System - Complete Demo")
        print("=" * 60)
        
        # Step 1: Initialize system
        await self.demo_system_initialization()
        
        # Step 2: Test doctor queries
        await self.demo_doctor_queries()
        
        # Step 3: Test voice processing
        await self.demo_voice_processing()
        
        # Step 4: Test sub-agent communication
        await self.demo_sub_agent_communication()
        
        # Step 5: Show system status
        await self.demo_system_status()
        
        # Step 6: Generate demo report
        self.generate_demo_report()
    
    async def demo_system_initialization(self):
        """Demo system initialization."""
        print("\n🔧 Step 1: System Initialization")
        print("-" * 40)
        
        try:
            # Create system agents
            agents = self.wallet_manager.create_system_agents()
            
            print(f"✅ Master Agent created: {agents['master']['address']}")
            print(f"✅ Healthcare Agent created: {agents['healthcare']['address']}")
            
            # Store results
            self.demo_results.append({
                "step": "initialization",
                "status": "success",
                "master_agent": agents['master']['address'],
                "healthcare_agent": agents['healthcare']['address'],
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ System initialization failed: {str(e)}")
            self.demo_results.append({
                "step": "initialization",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def demo_doctor_queries(self):
        """Demo doctor query processing."""
        print("\n👨‍⚕️ Step 2: Doctor Query Processing")
        print("-" * 40)
        
        test_queries = [
            "Follow up with all diabetic patients from last week",
            "Check status of patients with chest pain symptoms",
            "Review all patients over 65 with hypertension",
            "Get all patients who had medication changes in the past month"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📋 Test Query {i}: '{query}'")
            
            try:
                # Simulate query processing
                result = await self.simulate_doctor_query(query)
                
                print(f"   ✅ Action: {result['action']}")
                print(f"   ✅ Filters: {result['filters']}")
                print(f"   ✅ Patients found: {result['patients_found']}")
                
                self.demo_results.append({
                    "step": "doctor_query",
                    "query_number": i,
                    "query": query,
                    "status": "success",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"   ❌ Query failed: {str(e)}")
                self.demo_results.append({
                    "step": "doctor_query",
                    "query_number": i,
                    "query": query,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    async def demo_voice_processing(self):
        """Demo voice data processing."""
        print("\n🎤 Step 3: Voice Data Processing")
        print("-" * 40)
        
        test_voice_data = [
            {
                "session_id": "voice_001",
                "transcript": "Patient John Smith reports chest pain and shortness of breath",
                "scenario": "Urgent cardiac symptoms"
            },
            {
                "session_id": "voice_002", 
                "transcript": "Patient Mary Johnson says she's feeling better and taking her diabetes medication regularly",
                "scenario": "Routine follow-up"
            },
            {
                "session_id": "voice_003",
                "transcript": "Patient Robert Brown mentions he's been having headaches and dizziness",
                "scenario": "New symptoms reported"
            }
        ]
        
        for i, voice_data in enumerate(test_voice_data, 1):
            print(f"\n🎤 Voice Session {i}: {voice_data['scenario']}")
            print(f"   Transcript: '{voice_data['transcript']}'")
            
            try:
                # Simulate voice processing
                result = await self.simulate_voice_processing(voice_data)
                
                print(f"   ✅ Processing steps: {len(result['processing_steps'])}")
                print(f"   ✅ Recommendations: {len(result['recommendations'])}")
                print(f"   ✅ Priority: {result['highest_priority']}")
                
                self.demo_results.append({
                    "step": "voice_processing",
                    "session_number": i,
                    "session_id": voice_data['session_id'],
                    "scenario": voice_data['scenario'],
                    "status": "success",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"   ❌ Voice processing failed: {str(e)}")
                self.demo_results.append({
                    "step": "voice_processing",
                    "session_number": i,
                    "session_id": voice_data['session_id'],
                    "scenario": voice_data['scenario'],
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    async def demo_sub_agent_communication(self):
        """Demo sub-agent communication."""
        print("\n🤖 Step 4: Sub-Agent Communication")
        print("-" * 40)
        
        # Create test patients
        test_patients = [
            PatientRecord(
                patient_id="PAT001",
                name="John Smith",
                last_visit="2024-01-15",
                status="active",
                medical_history=["Diabetes Type 2", "Hypertension"],
                current_medications=["Metformin", "Lisinopril"],
                symptoms=["fatigue", "frequent urination"]
            ),
            PatientRecord(
                patient_id="PAT002",
                name="Mary Johnson",
                last_visit="2024-01-10",
                status="active",
                medical_history=["Heart Disease"],
                current_medications=["Aspirin", "Atorvastatin"],
                symptoms=["chest pain", "shortness of breath"]
            )
        ]
        
        context = ParsedCriteria(
            action="follow_up",
            time_filter="last_week",
            patient_criteria={"status": "active"}
        )
        
        for i, patient in enumerate(test_patients, 1):
            print(f"\n🤖 Sub-Agent {i}: {patient.name}")
            print(f"   Patient ID: {patient.patient_id}")
            print(f"   Conditions: {', '.join(patient.medical_history)}")
            
            try:
                # Create sub-agent
                sub_agent = await self.sub_agent_manager.create_sub_agent(patient, context)
                
                # Simulate communication
                result = await self.simulate_sub_agent_communication(sub_agent, patient)
                
                print(f"   ✅ Communication outcome: {result['outcome']}")
                print(f"   ✅ Confidence score: {result['confidence_score']:.2f}")
                print(f"   ✅ Data obtained: {len(result['data_obtained'])} items")
                
                self.demo_results.append({
                    "step": "sub_agent_communication",
                    "sub_agent_number": i,
                    "patient_id": patient.patient_id,
                    "patient_name": patient.name,
                    "status": "success",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"   ❌ Sub-agent communication failed: {str(e)}")
                self.demo_results.append({
                    "step": "sub_agent_communication",
                    "sub_agent_number": i,
                    "patient_id": patient.patient_id,
                    "patient_name": patient.name,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    async def demo_system_status(self):
        """Demo system status monitoring."""
        print("\n📊 Step 5: System Status Monitoring")
        print("-" * 40)
        
        try:
            # Get system status
            status = self.sub_agent_manager.get_system_status()
            
            print(f"✅ Total sub-agents: {status['total_sub_agents']}")
            print(f"✅ Completed: {status['completed']}")
            print(f"✅ Flagged for review: {status['flagged_for_review']}")
            print(f"✅ Failed: {status['failed']}")
            print(f"✅ Success rate: {status['success_rate']:.1f}%")
            
            self.demo_results.append({
                "step": "system_status",
                "status": "success",
                "result": status,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ System status check failed: {str(e)}")
            self.demo_results.append({
                "step": "system_status",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    async def simulate_doctor_query(self, query: str) -> Dict[str, Any]:
        """Simulate doctor query processing."""
        # Simple simulation - in real implementation, this would use the master agent
        action = "follow_up"
        if "check" in query.lower():
            action = "check_status"
        elif "review" in query.lower():
            action = "review"
        elif "get" in query.lower():
            action = "get_patients"
        
        filters = []
        if "diabetic" in query.lower():
            filters.append("diabetes")
        if "chest pain" in query.lower():
            filters.append("chest_pain")
        if "over 65" in query.lower():
            filters.append("age_65_plus")
        
        return {
            "action": action,
            "filters": filters,
            "patients_found": len(filters) * 2,  # Mock data
            "processing_time": "0.5s"
        }
    
    async def simulate_voice_processing(self, voice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate voice data processing."""
        transcript = voice_data['transcript'].lower()
        
        processing_steps = ["transcript_analysis", "patient_identification"]
        recommendations = []
        highest_priority = "low"
        
        if "chest pain" in transcript:
            recommendations.append({
                "type": "immediate_attention",
                "message": "Patient reports chest pain - requires immediate evaluation",
                "priority": "high"
            })
            highest_priority = "high"
            processing_steps.append("urgent_symptom_detection")
        
        if "diabetes" in transcript or "medication" in transcript:
            recommendations.append({
                "type": "medication_review",
                "message": "Review current medications and potential interactions",
                "priority": "medium"
            })
            if highest_priority == "low":
                highest_priority = "medium"
            processing_steps.append("medication_analysis")
        
        if "feeling better" in transcript:
            recommendations.append({
                "type": "routine_follow_up",
                "message": "Patient reports improvement - schedule routine follow-up",
                "priority": "low"
            })
            processing_steps.append("positive_outcome_detection")
        
        return {
            "processing_steps": processing_steps,
            "recommendations": recommendations,
            "highest_priority": highest_priority,
            "processing_time": "0.3s"
        }
    
    async def simulate_sub_agent_communication(self, sub_agent, patient: PatientRecord) -> Dict[str, Any]:
        """Simulate sub-agent communication."""
        # Simulate different outcomes based on patient data
        if "chest pain" in [s.lower() for s in (patient.symptoms or [])]:
            return {
                "outcome": "escalate_urgent",
                "confidence_score": 0.85,
                "data_obtained": {
                    "chest_pain_confirmed": True,
                    "patient_distressed": True,
                    "urgent_care_needed": True
                },
                "communication_quality": "good"
            }
        elif "diabetes" in [h.lower() for h in patient.medical_history]:
            return {
                "outcome": "flag_for_doctor_review",
                "confidence_score": 0.70,
                "data_obtained": {
                    "medication_adherence": True,
                    "symptom_improvement": True,
                    "follow_up_needed": True
                },
                "communication_quality": "fair"
            }
        else:
            return {
                "outcome": "close_loop",
                "confidence_score": 0.90,
                "data_obtained": {
                    "patient_well": True,
                    "no_concerns": True,
                    "routine_follow_up_scheduled": True
                },
                "communication_quality": "excellent"
            }
    
    def generate_demo_report(self):
        """Generate a comprehensive demo report."""
        print("\n📋 Demo Report")
        print("=" * 60)
        
        # Count successes and failures
        total_steps = len(self.demo_results)
        successful_steps = sum(1 for result in self.demo_results if result['status'] == 'success')
        failed_steps = total_steps - successful_steps
        
        print(f"Total demo steps: {total_steps}")
        print(f"Successful steps: {successful_steps}")
        print(f"Failed steps: {failed_steps}")
        print(f"Success rate: {(successful_steps/total_steps*100):.1f}%")
        
        # Group by step type
        step_types = {}
        for result in self.demo_results:
            step = result['step']
            if step not in step_types:
                step_types[step] = {'success': 0, 'failed': 0}
            step_types[step][result['status']] += 1
        
        print("\nStep-by-step results:")
        for step, counts in step_types.items():
            total = counts['success'] + counts['failed']
            success_rate = (counts['success'] / total * 100) if total > 0 else 0
            print(f"  {step}: {counts['success']}/{total} ({success_rate:.1f}%)")
        
        # Save detailed report
        report_data = {
            "demo_summary": {
                "total_steps": total_steps,
                "successful_steps": successful_steps,
                "failed_steps": failed_steps,
                "success_rate": successful_steps/total_steps*100,
                "timestamp": datetime.now().isoformat()
            },
            "step_results": step_types,
            "detailed_results": self.demo_results
        }
        
        with open("uagents_demo_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: uagents_demo_report.json")
        print("\n🎉 UAgents Healthcare System Demo Complete!")


async def main():
    """Main demo execution."""
    demo = UAgentsHealthcareDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())

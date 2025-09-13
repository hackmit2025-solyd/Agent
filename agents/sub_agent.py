"""
Phase 3: Sub-Agent Development
Handles external server communication, JSON data processing, and decision logic.
"""
import asyncio
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from agents.master_agent import PatientRecord, ParsedCriteria
from services.llm_service import llm_service
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)


class FollowUpStatus(Enum):
    """Status of follow-up communication."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    FLAGGED_FOR_REVIEW = "flagged_for_review"


class DecisionOutcome(Enum):
    """Decision outcomes for follow-up completion."""
    CLOSE_LOOP = "close_loop"
    FLAG_FOR_DOCTOR_REVIEW = "flag_for_doctor_review"
    RETRY_COMMUNICATION = "retry_communication"
    ESCALATE_URGENT = "escalate_urgent"


@dataclass
class CommunicationResult:
    """Result of a communication session."""
    session_id: str
    patient_id: str
    status: FollowUpStatus
    outcome: DecisionOutcome
    data_obtained: Dict[str, Any]
    missing_data: List[str]
    confidence_score: float
    timestamp: datetime
    notes: str


@dataclass
class LiveKitSessionData:
    """Data structure for LiveKit session information."""
    session_id: str
    patient_id: str
    room_id: str
    participant_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    transcript: Optional[str] = None
    audio_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SubAgent:
    """
    Phase 3 Sub-Agent with external server communication and decision logic.
    Each sub-agent handles communication for a specific patient.
    """
    
    def __init__(self, patient_data: PatientRecord, master_context: ParsedCriteria, sub_agent_id: str):
        self.sub_agent_id = sub_agent_id
        self.patient_data = patient_data
        self.master_context = master_context
        self.status = FollowUpStatus.PENDING
        self.created_at = datetime.utcnow()
        self.communication_results = []
        
        # External server configuration
        self.livekit_server_url = AgentConfig.LIVEKIT_SERVER_URL
        self.communication_timeout = 300  # 5 minutes
        
        logger.info(f"Sub-agent {sub_agent_id} created for patient {patient_data.patient_id}")
    
    async def initiate_communication(self) -> CommunicationResult:
        """
        Initiate communication with the external LiveKit server.
        
        Returns:
            CommunicationResult with the outcome of the communication
        """
        logger.info(f"Sub-agent {self.sub_agent_id} initiating communication for patient {self.patient_data.patient_id}")
        
        self.status = FollowUpStatus.IN_PROGRESS
        
        try:
            # Step 1: Create LiveKit session
            session_data = await self._create_livekit_session()
            
            # Step 2: Monitor communication
            communication_result = await self._monitor_communication(session_data)
            
            # Step 3: Process results and make decision
            decision_result = await self._process_communication_result(communication_result)
            
            # Step 4: Update status
            self.status = decision_result.status
            self.communication_results.append(decision_result)
            
            logger.info(f"Sub-agent {self.sub_agent_id} completed communication with outcome: {decision_result.outcome}")
            return decision_result
            
        except Exception as e:
            logger.error(f"Sub-agent {self.sub_agent_id} communication failed: {str(e)}")
            self.status = FollowUpStatus.FAILED
            
            # Create failure result
            failure_result = CommunicationResult(
                session_id=f"failed_{self.sub_agent_id}",
                patient_id=self.patient_data.patient_id,
                status=FollowUpStatus.FAILED,
                outcome=DecisionOutcome.FLAG_FOR_DOCTOR_REVIEW,
                data_obtained={},
                missing_data=self._get_required_data_fields(),
                confidence_score=0.0,
                timestamp=datetime.utcnow(),
                notes=f"Communication failed: {str(e)}"
            )
            
            self.communication_results.append(failure_result)
            return failure_result
    
    async def _create_livekit_session(self) -> LiveKitSessionData:
        """
        Create a LiveKit session for the patient.
        
        Returns:
            LiveKitSessionData with session information
        """
        logger.info(f"Creating LiveKit session for patient {self.patient_data.patient_id}")
        
        # Prepare session data
        session_id = f"session_{self.patient_data.patient_id}_{int(datetime.utcnow().timestamp())}"
        room_id = f"room_{self.patient_data.patient_id}"
        participant_id = f"agent_{self.sub_agent_id}"
        
        # Create session payload
        session_payload = {
            "session_id": session_id,
            "patient_id": self.patient_data.patient_id,
            "patient_name": self.patient_data.name,
            "room_id": room_id,
            "participant_id": participant_id,
            "agent_id": self.sub_agent_id,
            "master_context": {
                "action": self.master_context.action,
                "time_filter": self.master_context.time_filter,
                "condition_filter": self.master_context.condition_filter,
                "symptom_filter": self.master_context.symptom_filter
            },
            "patient_data": {
                "medical_history": self.patient_data.medical_history,
                "current_medications": self.patient_data.current_medications,
                "symptoms": self.patient_data.symptoms
            },
            "communication_goals": self._determine_communication_goals()
        }
        
        try:
            # Call external LiveKit server
            response = requests.post(
                f"{self.livekit_server_url}/api/sessions/create",
                json=session_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                session_response = response.json()
                logger.info(f"LiveKit session created successfully: {session_id}")
                
                return LiveKitSessionData(
                    session_id=session_id,
                    patient_id=self.patient_data.patient_id,
                    room_id=room_id,
                    participant_id=participant_id,
                    start_time=datetime.utcnow(),
                    metadata=session_response
                )
            else:
                logger.warning(f"LiveKit server unavailable, using mock session: {response.status_code}")
                return self._create_mock_session(session_id, room_id, participant_id)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"LiveKit server connection failed, using mock session: {str(e)}")
            return self._create_mock_session(session_id, room_id, participant_id)
    
    def _create_mock_session(self, session_id: str, room_id: str, participant_id: str) -> LiveKitSessionData:
        """Create a mock session for testing when LiveKit server is unavailable."""
        return LiveKitSessionData(
            session_id=session_id,
            patient_id=self.patient_data.patient_id,
            room_id=room_id,
            participant_id=participant_id,
            start_time=datetime.utcnow(),
            metadata={"mock": True, "reason": "LiveKit server unavailable"}
        )
    
    def _determine_communication_goals(self) -> List[str]:
        """Determine what information needs to be obtained from the communication."""
        goals = []
        
        if self.master_context.action == "follow_up":
            goals.extend([
                "Verify patient is feeling well",
                "Check medication adherence",
                "Assess any new symptoms",
                "Schedule next appointment if needed"
            ])
        elif self.master_context.action == "check_status":
            goals.extend([
                "Verify current health status",
                "Check medication effectiveness",
                "Assess any side effects",
                "Confirm treatment compliance"
            ])
        elif self.master_context.action == "review":
            goals.extend([
                "Review reported symptoms",
                "Assess symptom severity",
                "Determine if immediate care needed",
                "Provide symptom management advice"
            ])
        
        return goals
    
    async def _monitor_communication(self, session_data: LiveKitSessionData) -> Dict[str, Any]:
        """
        Monitor the communication session and collect results using Claude.
        
        Args:
            session_data: LiveKit session information
            
        Returns:
            Dictionary with communication results
        """
        logger.info(f"Monitoring communication session {session_data.session_id}")
        
        # Simulate communication monitoring
        await asyncio.sleep(2)  # Simulate communication duration
        
        # Use Claude to generate realistic communication results
        patient_data = {
            "name": self.patient_data.name,
            "medical_history": self.patient_data.medical_history,
            "current_medications": self.patient_data.current_medications,
            "symptoms": self.patient_data.symptoms or []
        }
        
        context = {
            "goals": self._determine_communication_goals(),
            "session_id": session_data.session_id,
            "patient_id": self.patient_data.patient_id
        }
        
        # Generate communication using Claude
        claude_results = await llm_service.generate_communication_transcript(patient_data, context)
        
        # Add session metadata
        claude_results["session_id"] = session_data.session_id
        claude_results["patient_id"] = self.patient_data.patient_id
        
        return claude_results
    
    def _create_mock_communication_results(self, session_data: LiveKitSessionData) -> Dict[str, Any]:
        """Create mock communication results for testing."""
        import random
        
        # Simulate different outcomes based on patient data and context
        patient_symptoms = [s.lower() for s in (self.patient_data.symptoms or [])]
        patient_history = [h.lower() for h in self.patient_data.medical_history]
        
        # Check for urgent conditions
        urgent_conditions = ["chest pain", "shortness of breath", "severe", "emergency"]
        has_urgent = any(condition in ' '.join(patient_symptoms) for condition in urgent_conditions)
        
        # Check for heart disease
        has_heart_disease = any(condition in ' '.join(patient_history) for condition in ["heart disease", "cardiac", "myocardial"])
        
        # Check for diabetes
        has_diabetes = any(condition in ' '.join(patient_history) for condition in ["diabetes", "diabetic"])
        
        # Determine scenario based on context and patient data
        if has_urgent and has_heart_disease:
            # Urgent cardiac patient - escalate
            return {
                "session_id": session_data.session_id,
                "patient_id": self.patient_data.patient_id,
                "duration": 300.0,  # 5 minutes
                "transcript": f"Patient {self.patient_data.name} reports persistent chest pain and shortness of breath. Blood pressure elevated at 160/95. Patient appears distressed and concerned. Pain rating 7/10.",
                "data_obtained": {
                    "chest_pain_persistent": True,
                    "shortness_of_breath": True,
                    "blood_pressure_elevated": True,
                    "patient_distressed": True,
                    "pain_severe": True
                },
                "missing_data": ["detailed_pain_description", "exact_location", "radiation_pattern"],
                "confidence_score": 0.60,
                "conversation_quality": "poor",
                "patient_cooperation": "fair"
            }
        elif has_diabetes and self.master_context.action == "check_status":
            # Diabetic patient status check - may need review
            return {
                "session_id": session_data.session_id,
                "patient_id": self.patient_data.patient_id,
                "duration": 200.0,  # 3.3 minutes
                "transcript": f"Patient {self.patient_data.name} reports blood sugar levels fluctuating between 180-220. Taking Metformin but sometimes forgets evening dose. Experiencing increased fatigue and blurred vision.",
                "data_obtained": {
                    "blood_sugar_high": True,
                    "medication_inconsistent": True,
                    "fatigue_increased": True,
                    "blurred_vision": True
                },
                "missing_data": ["exact_blood_sugar_readings", "medication_schedule", "diet_compliance"],
                "confidence_score": 0.65,
                "conversation_quality": "fair",
                "patient_cooperation": "good"
            }
        elif self.master_context.action == "review" and patient_symptoms:
            # Symptom review - may need doctor attention
            return {
                "session_id": session_data.session_id,
                "patient_id": self.patient_data.patient_id,
                "duration": 150.0,  # 2.5 minutes
                "transcript": f"Patient {self.patient_data.name} reports symptoms are persisting. Difficulty describing exact nature of symptoms. Some confusion about medication timing.",
                "data_obtained": {
                    "symptoms_persisting": True,
                    "medication_confusion": True
                },
                "missing_data": ["symptom_severity", "symptom_duration", "medication_effectiveness", "side_effects"],
                "confidence_score": 0.55,
                "conversation_quality": "poor",
                "patient_cooperation": "fair"
            }
        else:
            # Routine follow-up - successful
            return {
                "session_id": session_data.session_id,
                "patient_id": self.patient_data.patient_id,
                "duration": 120.0,  # 2 minutes
                "transcript": f"Patient {self.patient_data.name} reports feeling well. No new symptoms. Taking medications as prescribed. No concerns reported. Next appointment scheduled.",
                "data_obtained": {
                    "feeling_well": True,
                    "no_new_symptoms": True,
                    "medication_adherence": True,
                    "no_concerns": True,
                    "next_appointment_scheduled": True
                },
                "missing_data": [],
                "confidence_score": 0.90,
                "conversation_quality": "excellent",
                "patient_cooperation": "excellent"
            }
    
    async def _process_communication_result(self, communication_data: Dict[str, Any]) -> CommunicationResult:
        """
        Process the communication results using Claude's intelligent decision making.
        
        Args:
            communication_data: Raw communication data from LiveKit
            
        Returns:
            CommunicationResult with decision outcome
        """
        logger.info(f"Processing communication results for session {communication_data['session_id']}")
        
        # Use Claude to analyze the communication and make decisions
        patient_data = {
            "name": self.patient_data.name,
            "medical_history": self.patient_data.medical_history,
            "current_medications": self.patient_data.current_medications,
            "symptoms": self.patient_data.symptoms or []
        }
        
        # Let Claude make the decision
        claude_analysis = await llm_service.analyze_communication_outcome(communication_data, patient_data)
        
        # Extract Claude's decision
        outcome_str = claude_analysis.get("outcome", "close_loop").lower()
        decision_outcome = DecisionOutcome(outcome_str) if outcome_str in [o.value for o in DecisionOutcome] else DecisionOutcome.CLOSE_LOOP
        
        # Determine status based on Claude's decision
        if decision_outcome == DecisionOutcome.CLOSE_LOOP:
            status = FollowUpStatus.COMPLETED
        elif decision_outcome == DecisionOutcome.FLAG_FOR_DOCTOR_REVIEW:
            status = FollowUpStatus.FLAGGED_FOR_REVIEW
        elif decision_outcome == DecisionOutcome.ESCALATE_URGENT:
            status = FollowUpStatus.FLAGGED_FOR_REVIEW
        else:
            status = FollowUpStatus.FAILED
        
        # Create result with Claude's analysis
        result = CommunicationResult(
            session_id=communication_data["session_id"],
            patient_id=self.patient_data.patient_id,
            status=status,
            outcome=decision_outcome,
            data_obtained=communication_data.get("data_obtained", {}),
            missing_data=communication_data.get("missing_data", []),
            confidence_score=claude_analysis.get("confidence", 0.0),
            timestamp=datetime.utcnow(),
            notes=f"Claude Analysis: {claude_analysis.get('reasoning', 'No reasoning provided')}\n\nUrgent Conditions: {claude_analysis.get('urgent_conditions', [])}\nNext Steps: {claude_analysis.get('next_steps', [])}\nTermination Reason: {claude_analysis.get('termination_reason', 'Standard completion')}"
        )
        
        logger.info(f"Claude decision: {decision_outcome.value} for patient {self.patient_data.patient_id}")
        logger.info(f"Claude reasoning: {claude_analysis.get('reasoning', 'No reasoning')[:100]}...")
        
        return result
    
    def _analyze_communication_success(self, data_obtained: Dict[str, Any], missing_data: List[str], 
                                     confidence_score: float, conversation_quality: str) -> DecisionOutcome:
        """
        Analyze communication success and determine outcome.
        
        Args:
            data_obtained: Data successfully obtained
            missing_data: Data that was not obtained
            confidence_score: Confidence in the communication
            conversation_quality: Quality of the conversation
            
        Returns:
            DecisionOutcome based on analysis
        """
        # High confidence and good quality = close loop
        if confidence_score >= 0.8 and conversation_quality in ["excellent", "good"] and not missing_data:
            return DecisionOutcome.CLOSE_LOOP
        
        # Check for urgent conditions that need doctor review
        urgent_conditions = [
            "blood_pressure_elevated",
            "chest_pain_persistent",
            "pain_severe",
            "patient_distressed",
            "shortness_of_breath"
        ]
        
        if any(condition in data_obtained for condition in urgent_conditions):
            return DecisionOutcome.ESCALATE_URGENT
        
        # Missing critical data or low confidence = flag for review
        if missing_data or confidence_score < 0.6:
            return DecisionOutcome.FLAG_FOR_DOCTOR_REVIEW
        
        # Medium confidence = retry or flag based on context
        if confidence_score >= 0.6:
            return DecisionOutcome.CLOSE_LOOP
        else:
            return DecisionOutcome.FLAG_FOR_DOCTOR_REVIEW
    
    def _get_required_data_fields(self) -> List[str]:
        """Get list of required data fields based on master context."""
        required_fields = []
        
        if self.master_context.action == "follow_up":
            required_fields = ["medication_adherence", "symptom_status", "next_appointment"]
        elif self.master_context.action == "check_status":
            required_fields = ["current_health_status", "medication_effectiveness", "side_effects"]
        elif self.master_context.action == "review":
            required_fields = ["symptom_description", "symptom_severity", "immediate_care_needed"]
        
        return required_fields
    
    def _generate_decision_notes(self, outcome: DecisionOutcome, communication_data: Dict[str, Any]) -> str:
        """Generate notes explaining the decision."""
        notes = f"Decision: {outcome.value}\n"
        notes += f"Confidence: {communication_data.get('confidence_score', 0.0):.2f}\n"
        notes += f"Conversation Quality: {communication_data.get('conversation_quality', 'unknown')}\n"
        
        if outcome == DecisionOutcome.CLOSE_LOOP:
            notes += "All required information obtained successfully."
        elif outcome == DecisionOutcome.FLAG_FOR_DOCTOR_REVIEW:
            notes += "Missing critical information or low confidence. Doctor review required."
        elif outcome == DecisionOutcome.ESCALATE_URGENT:
            notes += "Urgent conditions detected. Immediate doctor attention required."
        
        return notes
    
    async def get_status_report(self) -> Dict[str, Any]:
        """Get current status report for the sub-agent."""
        return {
            "sub_agent_id": self.sub_agent_id,
            "patient_id": self.patient_data.patient_id,
            "patient_name": self.patient_data.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "communication_count": len(self.communication_results),
            "latest_outcome": self.communication_results[-1].outcome.value if self.communication_results else None,
            "latest_confidence": self.communication_results[-1].confidence_score if self.communication_results else None
        }


class SubAgentManager:
    """Manages multiple sub-agents and their communication."""
    
    def __init__(self):
        self.sub_agents = {}
        self.active_sessions = {}
    
    async def create_sub_agent(self, patient_data: PatientRecord, master_context: ParsedCriteria) -> SubAgent:
        """Create a new sub-agent for a patient."""
        sub_agent_id = f"sub_agent_{patient_data.patient_id}_{int(datetime.utcnow().timestamp())}"
        sub_agent = SubAgent(patient_data, master_context, sub_agent_id)
        self.sub_agents[sub_agent_id] = sub_agent
        return sub_agent
    
    async def process_all_communications(self) -> List[CommunicationResult]:
        """Process communications for all sub-agents."""
        results = []
        
        for sub_agent in self.sub_agents.values():
            if sub_agent.status == FollowUpStatus.PENDING:
                result = await sub_agent.initiate_communication()
                results.append(result)
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        total_agents = len(self.sub_agents)
        completed = sum(1 for agent in self.sub_agents.values() if agent.status == FollowUpStatus.COMPLETED)
        flagged = sum(1 for agent in self.sub_agents.values() if agent.status == FollowUpStatus.FLAGGED_FOR_REVIEW)
        failed = sum(1 for agent in self.sub_agents.values() if agent.status == FollowUpStatus.FAILED)
        
        return {
            "total_sub_agents": total_agents,
            "completed": completed,
            "flagged_for_review": flagged,
            "failed": failed,
            "success_rate": (completed / total_agents * 100) if total_agents > 0 else 0
        }


async def main():
    """Test the Sub-Agent system."""
    print("🤖 Phase 3: Sub-Agent Development Test")
    print("=" * 50)
    
    # Create test patient and context
    from agents.master_agent import PatientRecord, ParsedCriteria
    
    patient = PatientRecord(
        patient_id="TEST001",
        name="John Smith",
        last_visit="2024-01-15",
        status="active",
        medical_history=["Diabetes Type 2", "Hypertension"],
        current_medications=["Metformin", "Lisinopril"],
        symptoms=["fatigue", "frequent urination"]
    )
    
    context = ParsedCriteria(
        action="follow_up",
        time_filter="today",
        patient_criteria={"status": "active"}
    )
    
    # Create and test sub-agent
    manager = SubAgentManager()
    sub_agent = await manager.create_sub_agent(patient, context)
    
    print(f"Created sub-agent: {sub_agent.sub_agent_id}")
    print(f"Patient: {sub_agent.patient_data.name}")
    print(f"Context: {sub_agent.master_context.action}")
    
    # Test communication
    print("\nInitiating communication...")
    result = await sub_agent.initiate_communication()
    
    print(f"\nCommunication Result:")
    print(f"  Status: {result.status.value}")
    print(f"  Outcome: {result.outcome.value}")
    print(f"  Confidence: {result.confidence_score}")
    print(f"  Data Obtained: {len(result.data_obtained)} items")
    print(f"  Missing Data: {len(result.missing_data)} items")
    print(f"  Notes: {result.notes}")


if __name__ == "__main__":
    asyncio.run(main())

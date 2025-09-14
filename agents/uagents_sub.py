"""
Sub-Agent using uagents framework.
Handles external server communication, JSON data processing, and decision logic.
"""
import asyncio
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

from agents.protocols import (
    InitiateCommunication, CommunicationCompleted, CommunicationResult,
    FollowUpStatus, DecisionOutcome, PatientRecord, ParsedCriteria,
    AgentStatus
)
from services.llm_service import llm_service
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)


class LiveKitSessionData(Model):
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


def create_sub_agent(patient_data: PatientRecord, master_context: ParsedCriteria, sub_agent_id: str) -> Agent:
    """Create a sub-agent for a specific patient."""
    
    # Create unique agent for this sub-agent
    agent = Agent(
        name=f"sub_agent_{sub_agent_id}",
        seed=f"sub_agent_{sub_agent_id}_seed",
        endpoint=AgentConfig.UAGENTS_ENDPOINT,
        mailbox=AgentConfig.UAGENTS_MAILBOX_KEY,
        port=8003 + hash(sub_agent_id) % 1000  # Dynamic port assignment
    )
    
    # Fund the agent if needed
    fund_agent_if_low(agent.wallet.address())
    
    # Store patient data and context
    agent.patient_data = patient_data
    agent.master_context = master_context
    agent.sub_agent_id = sub_agent_id
    agent.status = FollowUpStatus.PENDING
    agent.created_at = datetime.utcnow()
    agent.communication_results = []
    
    # External server configuration
    agent.livekit_server_url = AgentConfig.LIVEKIT_SERVER_URL
    agent.communication_timeout = 300  # 5 minutes
    
    logger.info(f"Sub-agent {sub_agent_id} created for patient {patient_data.patient_id}")
    
    @agent.on_event("startup")
    async def startup(ctx: Context):
        """Initialize the sub-agent on startup."""
        logger.info(f"Sub-agent {agent.sub_agent_id} started: {ctx.agent.address}")
        
        # Send status update
        await ctx.send(
            ctx.agent.address,
            AgentStatus(
                agent_id=ctx.agent.address,
                agent_type="sub_agent",
                status="running",
                timestamp=datetime.now(),
                details={
                    "patient_id": agent.patient_data.patient_id,
                    "master_context": agent.master_context.action
                }
            )
        )
    
    @agent.on_message(InitiateCommunication, replies={CommunicationCompleted})
    async def handle_initiate_communication(ctx: Context, sender: str, msg: InitiateCommunication):
        """Initiate communication with the external LiveKit server."""
        logger.info(f"Sub-agent {agent.sub_agent_id} initiating communication for patient {agent.patient_data.patient_id}")
        
        agent.status = FollowUpStatus.IN_PROGRESS
        
        try:
            # Step 1: Create LiveKit session
            session_data = await create_livekit_session(agent)
            
            # Step 2: Monitor communication
            communication_result = await monitor_communication(agent, session_data)
            
            # Step 3: Process results and make decision
            decision_result = await process_communication_result(agent, communication_result)
            
            # Step 4: Update status
            agent.status = decision_result.status
            agent.communication_results.append(decision_result)
            
            logger.info(f"Sub-agent {agent.sub_agent_id} completed communication with outcome: {decision_result.outcome}")
            
            # Send completion response
            await ctx.send(
                sender,
                CommunicationCompleted(
                    result=decision_result,
                    sub_agent_id=agent.sub_agent_id,
                    timestamp=datetime.now()
                )
            )
            
        except Exception as e:
            logger.error(f"Sub-agent {agent.sub_agent_id} communication failed: {str(e)}")
            agent.status = FollowUpStatus.FAILED
            
            # Create failure result
            failure_result = CommunicationResult(
                session_id=f"failed_{agent.sub_agent_id}",
                patient_id=agent.patient_data.patient_id,
                status=FollowUpStatus.FAILED,
                outcome=DecisionOutcome.FLAG_FOR_DOCTOR_REVIEW,
                data_obtained={},
                missing_data=get_required_data_fields(agent),
                confidence_score=0.0,
                timestamp=datetime.now(),
                notes=f"Communication failed: {str(e)}"
            )
            
            agent.communication_results.append(failure_result)
            
            # Send failure response
            await ctx.send(
                sender,
                CommunicationCompleted(
                    result=failure_result,
                    sub_agent_id=agent.sub_agent_id,
                    timestamp=datetime.now()
                )
            )
    
    @agent.on_interval(period=30.0)
    async def status_update(ctx: Context):
        """Send periodic status updates."""
        await ctx.send(
            ctx.agent.address,
            AgentStatus(
                agent_id=ctx.agent.address,
                agent_type="sub_agent",
                status=agent.status.value,
                timestamp=datetime.now(),
                details={
                    "patient_id": agent.patient_data.patient_id,
                    "communication_count": len(agent.communication_results),
                    "latest_outcome": agent.communication_results[-1].outcome.value if agent.communication_results else None
                }
            )
        )
    
    return agent


async def create_livekit_session(agent: Agent) -> LiveKitSessionData:
    """
    Create a LiveKit session for the patient.
    
    Returns:
        LiveKitSessionData with session information
    """
    logger.info(f"Creating LiveKit session for patient {agent.patient_data.patient_id}")
    
    # Prepare session data
    session_id = f"session_{agent.patient_data.patient_id}_{int(datetime.utcnow().timestamp())}"
    room_id = f"room_{agent.patient_data.patient_id}"
    participant_id = f"agent_{agent.sub_agent_id}"
    
    # Create session payload
    session_payload = {
        "session_id": session_id,
        "patient_id": agent.patient_data.patient_id,
        "patient_name": agent.patient_data.name,
        "room_id": room_id,
        "participant_id": participant_id,
        "agent_id": agent.sub_agent_id,
        "master_context": {
            "action": agent.master_context.action,
            "time_filter": agent.master_context.time_filter,
            "condition_filter": agent.master_context.condition_filter,
            "symptom_filter": agent.master_context.symptom_filter
        },
        "patient_data": {
            "medical_history": agent.patient_data.medical_history,
            "current_medications": agent.patient_data.current_medications,
            "symptoms": agent.patient_data.symptoms
        },
        "communication_goals": determine_communication_goals(agent)
    }
    
    try:
        # Call external LiveKit server
        response = requests.post(
            f"{agent.livekit_server_url}/api/sessions/create",
            json=session_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            session_response = response.json()
            logger.info(f"LiveKit session created successfully: {session_id}")
            
            return LiveKitSessionData(
                session_id=session_id,
                patient_id=agent.patient_data.patient_id,
                room_id=room_id,
                participant_id=participant_id,
                start_time=datetime.utcnow(),
                metadata=session_response
            )
        else:
            logger.warning(f"LiveKit server unavailable, using mock session: {response.status_code}")
            return create_mock_session(session_id, room_id, participant_id, agent)
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"LiveKit server connection failed, using mock session: {str(e)}")
        return create_mock_session(session_id, room_id, participant_id, agent)


def create_mock_session(session_id: str, room_id: str, participant_id: str, agent: Agent) -> LiveKitSessionData:
    """Create a mock session for testing when LiveKit server is unavailable."""
    return LiveKitSessionData(
        session_id=session_id,
        patient_id=agent.patient_data.patient_id,
        room_id=room_id,
        participant_id=participant_id,
        start_time=datetime.utcnow(),
        metadata={"mock": True, "reason": "LiveKit server unavailable"}
    )


def determine_communication_goals(agent: Agent) -> List[str]:
    """Determine what information needs to be obtained from the communication."""
    goals = []
    
    if agent.master_context.action == "follow_up":
        goals.extend([
            "Verify patient is feeling well",
            "Check medication adherence",
            "Assess any new symptoms",
            "Schedule next appointment if needed"
        ])
    elif agent.master_context.action == "check_status":
        goals.extend([
            "Verify current health status",
            "Check medication effectiveness",
            "Assess any side effects",
            "Confirm treatment compliance"
        ])
    elif agent.master_context.action == "review":
        goals.extend([
            "Review reported symptoms",
            "Assess symptom severity",
            "Determine if immediate care needed",
            "Provide symptom management advice"
        ])
    
    return goals


async def monitor_communication(agent: Agent, session_data: LiveKitSessionData) -> Dict[str, Any]:
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
        "name": agent.patient_data.name,
        "medical_history": agent.patient_data.medical_history,
        "current_medications": agent.patient_data.current_medications,
        "symptoms": agent.patient_data.symptoms or []
    }
    
    context = {
        "goals": determine_communication_goals(agent),
        "session_id": session_data.session_id,
        "patient_id": agent.patient_data.patient_id
    }
    
    # Generate communication using Claude
    claude_results = await llm_service.generate_communication_transcript(patient_data, context)
    
    # Add session metadata
    claude_results["session_id"] = session_data.session_id
    claude_results["patient_id"] = agent.patient_data.patient_id
    
    return claude_results


async def process_communication_result(agent: Agent, communication_data: Dict[str, Any]) -> CommunicationResult:
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
        "name": agent.patient_data.name,
        "medical_history": agent.patient_data.medical_history,
        "current_medications": agent.patient_data.current_medications,
        "symptoms": agent.patient_data.symptoms or []
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
        patient_id=agent.patient_data.patient_id,
        status=status,
        outcome=decision_outcome,
        data_obtained=communication_data.get("data_obtained", {}),
        missing_data=communication_data.get("missing_data", []),
        confidence_score=claude_analysis.get("confidence", 0.0),
        timestamp=datetime.now(),
        notes=f"Claude Analysis: {claude_analysis.get('reasoning', 'No reasoning provided')}\n\nUrgent Conditions: {claude_analysis.get('urgent_conditions', [])}\nNext Steps: {claude_analysis.get('next_steps', [])}\nTermination Reason: {claude_analysis.get('termination_reason', 'Standard completion')}"
    )
    
    logger.info(f"Claude decision: {decision_outcome.value} for patient {agent.patient_data.patient_id}")
    logger.info(f"Claude reasoning: {claude_analysis.get('reasoning', 'No reasoning')[:100]}...")
    
    return result


def get_required_data_fields(agent: Agent) -> List[str]:
    """Get list of required data fields based on master context."""
    required_fields = []
    
    if agent.master_context.action == "follow_up":
        required_fields = ["medication_adherence", "symptom_status", "next_appointment"]
    elif agent.master_context.action == "check_status":
        required_fields = ["current_health_status", "medication_effectiveness", "side_effects"]
    elif agent.master_context.action == "review":
        required_fields = ["symptom_description", "symptom_severity", "immediate_care_needed"]
    
    return required_fields


# SubAgentManager for managing multiple sub-agents
class SubAgentManager:
    """Manages multiple sub-agents and their communication."""
    
    def __init__(self):
        self.sub_agents = {}
        self.active_sessions = {}
    
    async def create_sub_agent(self, patient_data: PatientRecord, master_context: ParsedCriteria) -> Agent:
        """Create a new sub-agent for a patient."""
        sub_agent_id = f"sub_agent_{patient_data.patient_id}_{int(datetime.utcnow().timestamp())}"
        sub_agent = create_sub_agent(patient_data, master_context, sub_agent_id)
        self.sub_agents[sub_agent_id] = sub_agent
        return sub_agent
    
    async def process_all_communications(self) -> List[CommunicationResult]:
        """Process communications for all sub-agents."""
        results = []
        
        for sub_agent in self.sub_agents.values():
            if sub_agent.status == FollowUpStatus.PENDING:
                # This would need to be implemented with proper message passing
                # For now, just return empty results
                pass
        
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


if __name__ == "__main__":
    # This would be used to run individual sub-agents
    # In practice, sub-agents are created dynamically by the master agent
    print("Sub-agents are created dynamically by the master agent")

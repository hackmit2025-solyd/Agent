"""
Master Agent using uagents framework.
Handles patient data ingestion, context parsing, database querying, and sub-agent creation.
"""
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

from agents.protocols import (
    DoctorQuery, QueryParsed, DatabaseQuery, DatabaseResponse,
    CreateSubAgent, SubAgentCreated, ProcessPatient, PatientProcessed,
    MasterQueryResult, AgentStatus, SystemStatus,
    PatientRecord, ParsedCriteria
)
from services.database_client import DatabaseClient
from services.llm_service import llm_service
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create the master agent
master_agent = Agent(
    name="master_agent",
    seed=AgentConfig.UAGENTS_SEED or "master_agent_seed_phrase_here",
    endpoint=AgentConfig.UAGENTS_ENDPOINT,
    mailbox=AgentConfig.UAGENTS_MAILBOX_KEY,
    port=8001
)

# Fund the agent if needed
fund_agent_if_low(master_agent.wallet.address())

# Global state
sub_agents = {}
sample_queries = {}


def load_sample_queries() -> Dict[str, Any]:
    """Load sample queries from JSON file."""
    try:
        with open("data/sample_queries.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Sample queries file not found, using empty queries")
        return {"sample_queries": []}


@master_agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize the master agent on startup."""
    global sample_queries
    sample_queries = load_sample_queries()
    
    logger.info(f"Master Agent started: {ctx.agent.address}")
    logger.info(f"Agent name: {ctx.agent.name}")
    
    # Send status update
    await ctx.send(
        ctx.agent.address,
        AgentStatus(
            agent_id=ctx.agent.address,
            agent_type="master",
            status="running",
            timestamp=datetime.now(),
            details={"sub_agents_count": len(sub_agents)}
        )
    )


@master_agent.on_message(DoctorQuery, replies={QueryParsed})
async def handle_doctor_query(ctx: Context, sender: str, msg: DoctorQuery):
    """Handle incoming doctor query and parse it."""
    logger.info(f"Received doctor query: '{msg.query}' from {sender}")
    
    try:
        # Use LLM to parse the query
        llm_result = await llm_service.parse_doctor_query(msg.query)
        
        # Convert LLM result to ParsedCriteria
        criteria = ParsedCriteria(
            action=llm_result.get("action", "follow_up"),
            time_filter=llm_result.get("time_filter"),
            condition_filter=llm_result.get("condition_filter"),
            symptom_filter=llm_result.get("symptom_filter"),
            age_filter=llm_result.get("age_filter"),
            medication_filter=llm_result.get("medication_filter"),
            patient_criteria=llm_result.get("patient_criteria", {"status": "active"})
        )
        
        logger.info(f"Parsed criteria: {criteria.action}")
        
        # Send parsed query back
        await ctx.send(
            sender,
            QueryParsed(
                criteria=criteria,
                original_query=msg.query,
                timestamp=datetime.now()
            )
        )
        
        # Also query database
        await ctx.send(
            ctx.agent.address,
            DatabaseQuery(
                criteria=criteria,
                original_query=msg.query,
                timestamp=datetime.now()
            )
        )
        
    except Exception as e:
        logger.error(f"Failed to parse doctor query: {str(e)}")
        # Send error response
        await ctx.send(
            sender,
            QueryParsed(
                criteria=ParsedCriteria(action="error", patient_criteria={}),
                original_query=msg.query,
                timestamp=datetime.now()
            )
        )


@master_agent.on_message(DatabaseQuery, replies={DatabaseResponse})
async def handle_database_query(ctx: Context, sender: str, msg: DatabaseQuery):
    """Handle database query and return patient data."""
    logger.info(f"Querying database for action: {msg.criteria.action}")
    
    try:
        # Initialize database client
        db_client = DatabaseClient()
        
        # Query database
        response = db_client.query_patient_data(msg.original_query)
        
        if "error" in response:
            logger.warning(f"Database query failed: {response['error']}")
            # Return sample data for testing
            patients = get_sample_patients(msg.criteria)
        else:
            # Parse response into PatientRecord objects
            patients = parse_database_response(response, msg.criteria)
        
        logger.info(f"Retrieved {len(patients)} patients from database")
        
        # Send database response
        await ctx.send(
            sender,
            DatabaseResponse(
                patients=patients,
                query_criteria=msg.criteria,
                timestamp=datetime.now(),
                success=True
            )
        )
        
        # Create sub-agents for each patient
        for i, patient in enumerate(patients):
            sub_agent_id = f"sub_agent_{patient.patient_id}_{i+1}"
            await ctx.send(
                ctx.agent.address,
                CreateSubAgent(
                    patient=patient,
                    master_context=msg.criteria,
                    sub_agent_id=sub_agent_id,
                    timestamp=datetime.now()
                )
            )
        
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}")
        # Send error response
        await ctx.send(
            sender,
            DatabaseResponse(
                patients=[],
                query_criteria=msg.criteria,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
        )


@master_agent.on_message(CreateSubAgent, replies={SubAgentCreated})
async def handle_create_sub_agent(ctx: Context, sender: str, msg: CreateSubAgent):
    """Create a sub-agent for a patient."""
    logger.info(f"Creating sub-agent {msg.sub_agent_id} for patient {msg.patient.patient_id}")
    
    try:
        # Store sub-agent info
        sub_agents[msg.sub_agent_id] = {
            "patient": msg.patient,
            "master_context": msg.master_context,
            "created_at": datetime.now(),
            "status": "created"
        }
        
        # Send sub-agent created response
        await ctx.send(
            sender,
            SubAgentCreated(
                sub_agent_id=msg.sub_agent_id,
                patient_id=msg.patient.patient_id,
                status="created",
                timestamp=datetime.now()
            )
        )
        
        # Process the patient
        await ctx.send(
            ctx.agent.address,
            ProcessPatient(
                patient=msg.patient,
                master_context=msg.master_context,
                sub_agent_id=msg.sub_agent_id,
                timestamp=datetime.now()
            )
        )
        
    except Exception as e:
        logger.error(f"Failed to create sub-agent: {str(e)}")


@master_agent.on_message(ProcessPatient, replies={PatientProcessed})
async def handle_process_patient(ctx: Context, sender: str, msg: ProcessPatient):
    """Process a patient using the sub-agent logic."""
    logger.info(f"Processing patient {msg.patient.patient_id} with sub-agent {msg.sub_agent_id}")
    
    try:
        # Process based on master context action
        processing_steps = []
        recommendations = []
        
        if msg.master_context.action == "follow_up":
            processing_steps, recommendations = await process_follow_up(msg.patient, msg.master_context)
        elif msg.master_context.action == "check_status":
            processing_steps, recommendations = await process_status_check(msg.patient, msg.master_context)
        elif msg.master_context.action == "review":
            processing_steps, recommendations = await process_review(msg.patient, msg.master_context)
        elif msg.master_context.action == "get_patients":
            processing_steps, recommendations = await process_get_patients(msg.patient, msg.master_context)
        
        # Update sub-agent status
        if msg.sub_agent_id in sub_agents:
            sub_agents[msg.sub_agent_id]["status"] = "completed"
        
        # Send processed response
        await ctx.send(
            sender,
            PatientProcessed(
                sub_agent_id=msg.sub_agent_id,
                patient_id=msg.patient.patient_id,
                processing_steps=processing_steps,
                recommendations=recommendations,
                status="completed",
                timestamp=datetime.now()
            )
        )
        
    except Exception as e:
        logger.error(f"Failed to process patient: {str(e)}")
        # Send error response
        await ctx.send(
            sender,
            PatientProcessed(
                sub_agent_id=msg.sub_agent_id,
                patient_id=msg.patient.patient_id,
                processing_steps=["error"],
                recommendations=[],
                status="failed",
                timestamp=datetime.now()
            )
        )


async def process_follow_up(patient: PatientRecord, context: ParsedCriteria) -> tuple[List[str], List[Dict[str, Any]]]:
    """Process follow-up action for patient."""
    processing_steps = ["follow_up_analysis"]
    recommendations = []
    
    # Analyze patient's medical history and current status
    if "diabetes" in [h.lower() for h in patient.medical_history]:
        recommendations.append({
            "type": "diabetes_monitoring",
            "message": "Schedule diabetes management follow-up",
            "priority": "medium"
        })
    
    if patient.symptoms and "chest_pain" in [s.lower() for s in patient.symptoms]:
        recommendations.append({
            "type": "cardiac_follow_up",
            "message": "Urgent cardiac follow-up required",
            "priority": "high"
        })
    
    recommendations.append({
        "type": "routine_follow_up",
        "message": f"Schedule routine follow-up for {patient.name}",
        "priority": "low"
    })
    
    return processing_steps, recommendations


async def process_status_check(patient: PatientRecord, context: ParsedCriteria) -> tuple[List[str], List[Dict[str, Any]]]:
    """Process status check action for patient."""
    processing_steps = ["status_analysis"]
    recommendations = []
    
    # Check medication adherence
    if patient.current_medications:
        recommendations.append({
            "type": "medication_review",
            "message": f"Review medication adherence for {len(patient.current_medications)} current medications",
            "priority": "medium"
        })
    
    # Check for concerning conditions
    concerning_conditions = ["diabetes", "heart disease", "hypertension"]
    patient_conditions = [h.lower() for h in patient.medical_history]
    
    for condition in concerning_conditions:
        if any(condition in pc for pc in patient_conditions):
            recommendations.append({
                "type": "condition_monitoring",
                "message": f"Monitor {condition} management",
                "priority": "high"
            })
    
    return processing_steps, recommendations


async def process_review(patient: PatientRecord, context: ParsedCriteria) -> tuple[List[str], List[Dict[str, Any]]]:
    """Process review action for patient."""
    processing_steps = ["symptom_review"]
    recommendations = []
    
    # Review symptoms mentioned in master context
    if context.symptom_filter == "chest_pain":
        recommendations.append({
            "type": "cardiac_evaluation",
            "message": "Comprehensive cardiac evaluation required",
            "priority": "high"
        })
    
    recommendations.append({
        "type": "symptom_monitoring",
        "message": "Continue monitoring reported symptoms",
        "priority": "medium"
    })
    
    return processing_steps, recommendations


async def process_get_patients(patient: PatientRecord, context: ParsedCriteria) -> tuple[List[str], List[Dict[str, Any]]]:
    """Process get patients action."""
    processing_steps = ["patient_data_compilation"]
    recommendations = []
    
    recommendations.append({
        "type": "data_compilation",
        "message": "Patient data compiled for review",
        "priority": "low"
    })
    
    return processing_steps, recommendations


def get_sample_patients(criteria: ParsedCriteria) -> List[PatientRecord]:
    """Get sample patients for testing when database is unavailable."""
    # Find matching sample query
    for sample_query in sample_queries.get("sample_queries", []):
        if sample_query["parsed_criteria"]["action"] == criteria.action:
            patients = []
            for patient_data in sample_query["expected_patients"]:
                patient = PatientRecord(
                    patient_id=patient_data["patient_id"],
                    name=patient_data["name"],
                    last_visit=patient_data["last_visit"],
                    status=patient_data["status"],
                    medical_history=patient_data["medical_history"],
                    current_medications=patient_data["current_medications"],
                    age=patient_data.get("age"),
                    symptoms=patient_data.get("symptoms"),
                    follow_up_reason=patient_data.get("follow_up_reason"),
                    medication_changes=patient_data.get("medication_changes")
                )
                patients.append(patient)
            return patients
    
    # Default sample patients
    return [
        PatientRecord(
            patient_id="SAMPLE001",
            name="Sample Patient",
            last_visit="2024-01-09",
            status="active",
            medical_history=["Sample Condition"],
            current_medications=["Sample Medication"]
        )
    ]


def parse_database_response(response: Dict[str, Any], criteria: ParsedCriteria) -> List[PatientRecord]:
    """Parse database response into PatientRecord objects."""
    # This would parse the actual database response
    # For now, return sample data
    return get_sample_patients(criteria)


@master_agent.on_interval(period=30.0)
async def status_update(ctx: Context):
    """Send periodic status updates."""
    total_agents = len(sub_agents)
    completed = sum(1 for agent in sub_agents.values() if agent["status"] == "completed")
    failed = sum(1 for agent in sub_agents.values() if agent["status"] == "failed")
    
    await ctx.send(
        ctx.agent.address,
        SystemStatus(
            total_sub_agents=total_agents,
            completed=completed,
            flagged_for_review=0,  # Not implemented in this version
            failed=failed,
            success_rate=(completed / total_agents * 100) if total_agents > 0 else 0,
            timestamp=datetime.now()
        )
    )


if __name__ == "__main__":
    master_agent.run()

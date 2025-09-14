"""
Healthcare Agent using uagents framework.
Processes voice data and queries patient information.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

from agents.protocols import (
    VoiceData, VoiceProcessed, AgentStatus
)
from services.database_client import DatabaseClient
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create the healthcare agent
healthcare_agent = Agent(
    name="healthcare_agent",
    seed=AgentConfig.UAGENTS_SEED or "healthcare_agent_seed_phrase_here",
    # endpoint=AgentConfig.UAGENTS_ENDPOINT,
    mailbox=True,
    port=8002
)

# Fund the agent if needed
fund_agent_if_low(healthcare_agent.wallet.address())

# Global state
database_client = None


@healthcare_agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize the healthcare agent on startup."""
    global database_client
    
    logger.info(f"Healthcare Agent started: {ctx.agent.address}")
    logger.info(f"Agent name: {ctx.agent.name}")
    
    # Initialize database client
    try:
        database_client = DatabaseClient()
        connection_test = database_client.test_connection()
        if connection_test["status"] == "success":
            logger.info("Database service connection verified")
        else:
            logger.warning("Database service connection failed - will continue without it")
    except Exception as e:
        logger.warning(f"Database service test failed: {str(e)}")
    
    # Send status update
    await ctx.send(
        ctx.agent.address,
        AgentStatus(
            agent_id=ctx.agent.address,
            agent_type="healthcare",
            status="running",
            timestamp=datetime.now(),
            details={"database_connected": database_client is not None}
        )
    )


@healthcare_agent.on_message(VoiceData, replies={VoiceProcessed})
async def handle_voice_data(ctx: Context, sender: str, msg: VoiceData):
    """Process incoming voice data from webhook."""
    logger.info(f"Processing voice data for session: {msg.session_id}")
    
    try:
        result = {
            "session_id": msg.session_id,
            "agent_address": ctx.agent.address,
            "processing_steps": [],
            "patient_data": None,
            "recommendations": []
        }
        
        # Extract information from transcript
        if msg.transcript:
            result["processing_steps"].append("transcript_analysis")
            
            # Extract patient information
            patient_info = await extract_patient_info(msg.transcript)
            if patient_info:
                result["processing_steps"].append("patient_identification")
                
                # Query database for patient information
                patient_data = await get_patient_data(patient_info)
                if patient_data and "error" not in patient_data:
                    result["processing_steps"].append("database_lookup")
                    result["patient_data"] = patient_data
                    
                    # Generate recommendations based on data
                    recommendations = await generate_recommendations(msg.transcript, patient_data)
                    result["recommendations"] = recommendations
                    result["processing_steps"].append("recommendation_generation")
        
        logger.info(f"Voice data processing completed: {len(result['processing_steps'])} steps")
        
        # Send processed response
        await ctx.send(
            sender,
            VoiceProcessed(
                session_id=msg.session_id,
                patient_data=result["patient_data"],
                recommendations=result["recommendations"],
                processing_steps=result["processing_steps"],
                timestamp=datetime.now()
            )
        )
        
    except Exception as e:
        logger.error(f"Failed to process voice data: {str(e)}")
        # Send error response
        await ctx.send(
            sender,
            VoiceProcessed(
                session_id=msg.session_id,
                patient_data=None,
                recommendations=[],
                processing_steps=["error"],
                timestamp=datetime.now()
            )
        )


async def extract_patient_info(transcript: str) -> Optional[Dict[str, Any]]:
    """
    Extract patient information from transcript.
    This is a simplified implementation - in production, use proper NLP.
    
    Args:
        transcript: The voice transcript
        
    Returns:
        Extracted patient information
    """
    # Simple keyword-based extraction (replace with proper NLP)
    transcript_lower = transcript.lower()
    
    patient_info = {}
    
    # Look for common patterns
    if "patient" in transcript_lower:
        # This is a very basic implementation
        words = transcript.split()
        for i, word in enumerate(words):
            if word.lower() == "patient" and i + 1 < len(words):
                potential_name = words[i + 1]
                if potential_name.isalpha():
                    patient_info["name"] = potential_name
                    break
    
    # Look for patient ID patterns
    import re
    id_pattern = r'(?:patient\s+)?(?:id\s+)?([A-Z]{2,3}-?\d{3,6})'
    id_match = re.search(id_pattern, transcript, re.IGNORECASE)
    if id_match:
        patient_info["id"] = id_match.group(1)
    
    return patient_info if patient_info else None


async def get_patient_data(patient_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query database for patient data.
    
    Args:
        patient_info: Extracted patient information
        
    Returns:
        Patient data from database
    """
    try:
        if not database_client:
            return {"error": "database_not_available"}
            
        if "id" in patient_info:
            return database_client.search_patient_by_id(patient_info["id"])
        elif "name" in patient_info:
            return database_client.search_patient_by_name(patient_info["name"])
        else:
            return {"error": "no_patient_identifier"}
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}")
        return {"error": "database_query_failed", "message": str(e)}


async def generate_recommendations(transcript: str, patient_data: Dict[str, Any]) -> list:
    """
    Generate recommendations based on transcript and patient data.
    
    Args:
        transcript: The voice transcript
        patient_data: Patient information from database
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Basic symptom detection and recommendations
    transcript_lower = transcript.lower()
    
    if "chest pain" in transcript_lower:
        recommendations.append({
            "type": "immediate_attention",
            "message": "Patient reports chest pain - requires immediate evaluation",
            "priority": "high"
        })
    
    if "shortness of breath" in transcript_lower:
        recommendations.append({
            "type": "respiratory_check",
            "message": "Patient reports breathing difficulties - check vitals",
            "priority": "medium"
        })
    
    if "medication" in transcript_lower:
        recommendations.append({
            "type": "medication_review",
            "message": "Review current medications and potential interactions",
            "priority": "medium"
        })
    
    # Add patient history considerations
    if patient_data and isinstance(patient_data, dict):
        recommendations.append({
            "type": "history_review",
            "message": "Review patient medical history for relevant conditions",
            "priority": "low"
        })
    
    return recommendations


@healthcare_agent.on_interval(period=60.0)
async def status_update(ctx: Context):
    """Send periodic status updates."""
    await ctx.send(
        ctx.agent.address,
        AgentStatus(
            agent_id=ctx.agent.address,
            agent_type="healthcare",
            status="running",
            timestamp=datetime.now(),
            details={
                "database_connected": database_client is not None,
                "uptime": "active"
            }
        )
    )


if __name__ == "__main__":
    healthcare_agent.run()

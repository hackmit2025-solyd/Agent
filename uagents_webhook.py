"""
Webhook receiver for uagents-based healthcare system.
Handles incoming voice data and routes it to appropriate agents.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify
from uagents import Agent, Context

from agents.uagents_healthcare import healthcare_agent
from agents.protocols import VoiceData, VoiceProcessed
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global state
healthcare_agent_instance = None
pending_requests = {}


def run_async(coro):
    """Run async function in sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def process_voice_data_async(session_id: str, transcript: str, audio_url: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process voice data asynchronously."""
    logger.info(f"Processing voice data for session: {session_id}")
    
    try:
        # Create voice data message
        voice_data = VoiceData(
            session_id=session_id,
            transcript=transcript,
            audio_url=audio_url,
            metadata=metadata,
            timestamp=datetime.now()
        )
        
        # In a real implementation, this would send the message to the healthcare agent
        # For now, we'll simulate the processing
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Generate mock response
        result = {
            "session_id": session_id,
            "patient_data": {
                "patient_id": "MOCK001",
                "name": "Mock Patient",
                "status": "active"
            },
            "recommendations": [
                {
                    "type": "immediate_attention",
                    "message": "Patient reports chest pain - requires immediate evaluation",
                    "priority": "high"
                }
            ],
            "processing_steps": [
                "transcript_analysis",
                "patient_identification",
                "recommendation_generation"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Voice data processed successfully for session: {session_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process voice data: {str(e)}")
        return {
            "session_id": session_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.route('/webhook/voice-data', methods=['POST'])
def webhook_voice_data():
    """Handle incoming voice data webhook."""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract required fields
        session_id = data.get('session_id')
        transcript = data.get('transcript', '')
        audio_url = data.get('audio_url')
        metadata = data.get('metadata', {})
        
        if not session_id:
            return jsonify({"error": "session_id is required"}), 400
        
        logger.info(f"Received voice data webhook for session: {session_id}")
        
        # Process voice data asynchronously
        result = run_async(process_voice_data_async(session_id, transcript, audio_url, metadata))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/doctor-query', methods=['POST'])
def webhook_doctor_query():
    """Handle incoming doctor query webhook."""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract required fields
        query = data.get('query')
        doctor_id = data.get('doctor_id')
        
        if not query:
            return jsonify({"error": "query is required"}), 400
        
        logger.info(f"Received doctor query webhook: '{query}'")
        
        # In a real implementation, this would send the query to the master agent
        # For now, we'll simulate the processing
        
        result = {
            "master_agent_id": "mock_master_agent",
            "original_query": query,
            "parsed_criteria": {
                "action": "follow_up",
                "time_filter": None,
                "condition_filter": None,
                "symptom_filter": None,
                "age_filter": None,
                "medication_filter": None
            },
            "patients_found": 0,
            "sub_agents_created": 0,
            "processing_results": [],
            "summary": {
                "total_patients": 0,
                "total_recommendations": 0,
                "high_priority_recommendations": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Doctor query webhook processing failed: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "healthcare_agent": "running" if healthcare_agent_instance else "not_initialized"
        }
    })


@app.route('/status', methods=['GET'])
def system_status():
    """Get system status."""
    return jsonify({
        "system": "uagents_healthcare",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "voice_data": "/webhook/voice-data",
            "doctor_query": "/webhook/doctor-query",
            "health": "/health",
            "status": "/status"
        }
    })


async def initialize_agents():
    """Initialize uagents agents."""
    global healthcare_agent_instance
    
    try:
        # Initialize healthcare agent
        healthcare_agent_instance = healthcare_agent
        logger.info("Healthcare agent initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {str(e)}")
        raise


def main():
    """Main execution function."""
    print("🌐 Starting Healthcare Webhook Server with uagents")
    print("=" * 50)
    
    # Initialize agents
    run_async(initialize_agents())
    
    print("✅ Webhook server initialized")
    print(f"   Voice data endpoint: http://{AgentConfig.WEBHOOK_HOST}:{AgentConfig.WEBHOOK_PORT}/webhook/voice-data")
    print(f"   Doctor query endpoint: http://{AgentConfig.WEBHOOK_HOST}:{AgentConfig.WEBHOOK_PORT}/webhook/doctor-query")
    print(f"   Health check: http://{AgentConfig.WEBHOOK_HOST}:{AgentConfig.WEBHOOK_PORT}/health")
    print()
    
    # Start Flask app
    app.run(
        host=AgentConfig.WEBHOOK_HOST,
        port=AgentConfig.WEBHOOK_PORT,
        debug=True
    )


if __name__ == "__main__":
    main()

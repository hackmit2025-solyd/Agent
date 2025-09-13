"""
Webhook receiver for processing voice data from LiveKit server.
This service receives POST requests containing voice recordings or transcripts.
"""
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = FastAPI(title="Healthcare Voice Processing Webhook")


class VoiceData(BaseModel):
    """Model for voice data received from LiveKit server."""
    session_id: str
    timestamp: str
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    participant_id: str
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class WebhookReceiver:
    """Handles incoming webhooks from LiveKit server."""
    
    def __init__(self):
        self.processed_sessions = []
        
    def process_voice_data(self, voice_data: VoiceData) -> Dict[str, Any]:
        """
        Process incoming voice data from LiveKit.
        
        Args:
            voice_data: The voice data payload
            
        Returns:
            Processing result
        """
        logger.info(f"Processing voice data for session: {voice_data.session_id}")
        
        # Store session for tracking
        self.processed_sessions.append({
            "session_id": voice_data.session_id,
            "timestamp": voice_data.timestamp,
            "processed": True
        })
        
        result = {
            "status": "success",
            "session_id": voice_data.session_id,
            "message": "Voice data received and queued for processing",
            "next_steps": []
        }
        
        # Determine processing pipeline based on data type
        if voice_data.transcript:
            result["next_steps"].append("text_analysis")
            logger.info(f"Transcript received: {voice_data.transcript[:100]}...")
        
        if voice_data.audio_url:
            result["next_steps"].append("audio_transcription")
            logger.info(f"Audio URL received: {voice_data.audio_url}")
        
        return result


# Global receiver instance
receiver = WebhookReceiver()


@app.post("/webhook/voice-data")
async def receive_voice_data(voice_data: VoiceData):
    """
    Endpoint to receive voice data from LiveKit server.
    """
    try:
        result = receiver.process_voice_data(voice_data)
        logger.info(f"Successfully processed voice data: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing voice data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/raw")
async def receive_raw_data(request: Request):
    """
    Endpoint to receive raw webhook data for testing.
    """
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        logger.info(f"Raw webhook received:")
        logger.info(f"Headers: {headers}")
        logger.info(f"Body: {body.decode('utf-8')[:500]}...")
        
        return {
            "status": "success",
            "message": "Raw webhook data received",
            "body_length": len(body),
            "content_type": headers.get("content-type", "unknown")
        }
    except Exception as e:
        logger.error(f"Error processing raw webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "webhook_receiver",
        "sessions_processed": len(receiver.processed_sessions)
    }


@app.get("/sessions")
async def get_processed_sessions():
    """Get list of processed sessions."""
    return {
        "sessions": receiver.processed_sessions,
        "total_count": len(receiver.processed_sessions)
    }


@app.get("/webhook/patient-summary")
async def receive_patient_summary(data: str = None):
    """
    Endpoint to receive patient summary via GET request with query parameter.
    This is the specific test case: ?data={"patient_id": "123", "summary": "Patient reports feeling better."}
    """
    try:
        if not data:
            raise HTTPException(status_code=400, detail="Missing 'data' query parameter")
        
        # Parse the JSON data from query parameter
        try:
            patient_data = json.loads(data)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in data parameter: {str(e)}")
        
        # Extract patient_id and summary as specified in the test
        patient_id = patient_data.get("patient_id")
        summary = patient_data.get("summary")
        
        if not patient_id or not summary:
            raise HTTPException(status_code=400, detail="Missing required fields: patient_id and summary")
        
        # Log the data as specified in the test requirements
        logger.info(f"Received patient summary - Patient ID: {patient_id}")
        logger.info(f"Received patient summary - Summary: {summary}")
        
        # Store the processed data
        receiver.processed_sessions.append({
            "session_id": f"patient_summary_{patient_id}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "patient_id": patient_id,
            "summary": summary,
            "processed": True
        })
        
        # Return success response
        result = {
            "status": "success",
            "message": "Patient summary received and logged successfully",
            "patient_id": patient_id,
            "summary": summary,
            "logged_at": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(f"Patient summary processing completed: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing patient summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting webhook receiver on {AgentConfig.WEBHOOK_HOST}:{AgentConfig.WEBHOOK_PORT}")
    print(f"Webhook endpoint: http://{AgentConfig.WEBHOOK_HOST}:{AgentConfig.WEBHOOK_PORT}{AgentConfig.WEBHOOK_ENDPOINT}")
    
    uvicorn.run(
        app,
        host=AgentConfig.WEBHOOK_HOST,
        port=AgentConfig.WEBHOOK_PORT,
        log_level=AgentConfig.LOG_LEVEL.lower()
    )

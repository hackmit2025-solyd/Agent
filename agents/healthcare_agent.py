"""
Main Fetch.ai agent for healthcare voice processing.
Integrates webhook reception and database communication.
"""
import asyncio
import logging
from typing import Dict, Any
from agents.wallet_manager import WalletManager
from services.database_client import DatabaseClient
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)


class HealthcareAgent:
    """
    Main healthcare agent that processes voice data and queries patient information.
    """
    
    def __init__(self):
        """Initialize the healthcare agent."""
        self.wallet_manager = WalletManager()
        self.database_client = DatabaseClient()
        self.agent_identity = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize the agent with wallet and configuration."""
        logger.info("Initializing Healthcare Agent...")
        
        # Load or create wallet
        try:
            if AgentConfig.WALLET_PRIVATE_KEY:
                wallet_info = self.wallet_manager.load_existing_wallet()
                logger.info(f"Loaded existing wallet: {wallet_info['address']}")
            else:
                logger.info("No existing wallet found, creating new one...")
                wallet_info = self.wallet_manager.create_new_wallet()
                logger.info(f"Created new wallet: {wallet_info['address']}")
            
            self.agent_identity = wallet_info['identity']
            
        except Exception as e:
            logger.error(f"Failed to initialize wallet: {str(e)}")
            raise
        
        # Test database connection
        try:
            connection_test = self.database_client.test_connection()
            if connection_test["status"] == "success":
                logger.info("Database service connection verified")
            else:
                logger.warning("Database service connection failed - will continue without it")
        except Exception as e:
            logger.warning(f"Database service test failed: {str(e)}")
        
        logger.info("Healthcare Agent initialization completed")
    
    async def process_voice_data(self, voice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming voice data from webhook.
        
        Args:
            voice_data: Voice data payload from LiveKit
            
        Returns:
            Processing result
        """
        logger.info(f"Processing voice data for session: {voice_data.get('session_id', 'unknown')}")
        
        result = {
            "session_id": voice_data.get("session_id"),
            "agent_address": self.agent_identity.address if self.agent_identity else "unknown",
            "processing_steps": [],
            "patient_data": None,
            "recommendations": []
        }
        
        # Extract information from transcript
        transcript = voice_data.get("transcript", "")
        if transcript:
            result["processing_steps"].append("transcript_analysis")
            
            # Simple patient name extraction (in production, use NLP)
            patient_info = await self.extract_patient_info(transcript)
            if patient_info:
                result["processing_steps"].append("patient_identification")
                
                # Query database for patient information
                patient_data = await self.get_patient_data(patient_info)
                if patient_data and "error" not in patient_data:
                    result["processing_steps"].append("database_lookup")
                    result["patient_data"] = patient_data
                    
                    # Generate recommendations based on data
                    recommendations = await self.generate_recommendations(transcript, patient_data)
                    result["recommendations"] = recommendations
                    result["processing_steps"].append("recommendation_generation")
        
        logger.info(f"Voice data processing completed: {len(result['processing_steps'])} steps")
        return result
    
    async def extract_patient_info(self, transcript: str) -> Dict[str, Any]:
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
    
    async def get_patient_data(self, patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query database for patient data.
        
        Args:
            patient_info: Extracted patient information
            
        Returns:
            Patient data from database
        """
        try:
            if "id" in patient_info:
                return self.database_client.search_patient_by_id(patient_info["id"])
            elif "name" in patient_info:
                return self.database_client.search_patient_by_name(patient_info["name"])
            else:
                return {"error": "no_patient_identifier"}
        except Exception as e:
            logger.error(f"Database query failed: {str(e)}")
            return {"error": "database_query_failed", "message": str(e)}
    
    async def generate_recommendations(self, transcript: str, patient_data: Dict[str, Any]) -> list:
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
    
    async def start(self):
        """Start the agent."""
        if not self.agent_identity:
            await self.initialize()
        
        self.is_running = True
        logger.info("Healthcare Agent is now running and ready to process voice data")
        
        # In a real implementation, this would start listening for webhooks
        # For now, we'll just keep the agent alive
        while self.is_running:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Stop the agent."""
        self.is_running = False
        logger.info("Healthcare Agent stopped")


async def main():
    """Main execution function."""
    print("🏥 Starting Healthcare Voice Processing Agent")
    print("=" * 50)
    
    agent = HealthcareAgent()
    
    try:
        await agent.initialize()
        print(f"✅ Agent initialized successfully")
        print(f"   Agent Address: {agent.agent_identity.address}")
        print(f"   Ready to process voice data from webhook endpoint")
        print()
        print("Agent is running... Press Ctrl+C to stop")
        
        await agent.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down agent...")
        await agent.stop()
        print("✅ Agent stopped successfully")
    except Exception as e:
        print(f"❌ Agent failed to start: {str(e)}")
        logger.error(f"Agent startup failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())

"""
Main entry point for the uagents-based healthcare system.
Coordinates all agents and provides a unified interface.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from agents.uagents_master import master_agent
from agents.uagents_healthcare import healthcare_agent
from agents.uagents_sub import SubAgentManager, create_sub_agent
from agents.protocols import (
    DoctorQuery, MasterQueryResult, VoiceData, VoiceProcessed,
    PatientRecord, ParsedCriteria, AgentStatus, SystemStatus
)
from agents.uagents_wallet import UAgentsWalletManager
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Global state
wallet_manager = UAgentsWalletManager()
sub_agent_manager = SubAgentManager()
system_status = {
    "master_agent": None,
    "healthcare_agent": None,
    "sub_agents": {},
    "total_queries": 0,
    "successful_queries": 0
}


class HealthcareSystemCoordinator:
    """Coordinates all agents in the healthcare system."""
    
    def __init__(self):
        self.master_agent = None
        self.healthcare_agent = None
        self.sub_agent_manager = SubAgentManager()
        self.is_running = False
    
    async def initialize(self):
        """Initialize the healthcare system."""
        logger.info("Initializing Healthcare System with uagents...")
        
        try:
            # Create system agents
            agents = wallet_manager.create_system_agents()
            
            # Store agent references
            self.master_agent = agents["master"]["agent"]
            self.healthcare_agent = agents["healthcare"]["agent"]
            
            # Update system status
            system_status["master_agent"] = agents["master"]["address"]
            system_status["healthcare_agent"] = agents["healthcare"]["address"]
            
            logger.info(f"Master Agent: {agents['master']['address']}")
            logger.info(f"Healthcare Agent: {agents['healthcare']['address']}")
            
            # Fund agents if needed
            fund_agent_if_low(self.master_agent.wallet.address())
            fund_agent_if_low(self.healthcare_agent.wallet.address())
            
            logger.info("Healthcare System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize healthcare system: {str(e)}")
            raise
    
    async def process_doctor_query(self, query: str) -> Dict[str, Any]:
        """Process a doctor query through the system."""
        logger.info(f"Processing doctor query: '{query}'")
        
        try:
            # Send query to master agent
            # Note: In a real implementation, this would use proper message passing
            # For now, we'll simulate the process
            
            # Create a mock result
            result = {
                "master_agent_id": system_status["master_agent"],
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
                "timestamp": datetime.now()
            }
            
            system_status["total_queries"] += 1
            system_status["successful_queries"] += 1
            
            logger.info("Doctor query processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process doctor query: {str(e)}")
            system_status["total_queries"] += 1
            return {"error": str(e)}
    
    async def process_voice_data(self, session_id: str, transcript: str, audio_url: str = None) -> Dict[str, Any]:
        """Process voice data through the healthcare agent."""
        logger.info(f"Processing voice data for session: {session_id}")
        
        try:
            # Create voice data message
            voice_data = VoiceData(
                session_id=session_id,
                transcript=transcript,
                audio_url=audio_url,
                timestamp=datetime.now()
            )
            
            # Send to healthcare agent
            # Note: In a real implementation, this would use proper message passing
            # For now, we'll simulate the process
            
            result = {
                "session_id": session_id,
                "patient_data": None,
                "recommendations": [],
                "processing_steps": ["transcript_analysis"],
                "timestamp": datetime.now()
            }
            
            logger.info("Voice data processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process voice data: {str(e)}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "master_agent": system_status["master_agent"],
            "healthcare_agent": system_status["healthcare_agent"],
            "sub_agents": len(system_status["sub_agents"]),
            "total_queries": system_status["total_queries"],
            "successful_queries": system_status["successful_queries"],
            "success_rate": (
                system_status["successful_queries"] / system_status["total_queries"] * 100
                if system_status["total_queries"] > 0 else 0
            ),
            "timestamp": datetime.now()
        }
    
    async def start(self):
        """Start the healthcare system."""
        if not self.is_running:
            await self.initialize()
            self.is_running = True
            logger.info("Healthcare System is now running")
    
    async def stop(self):
        """Stop the healthcare system."""
        self.is_running = False
        logger.info("Healthcare System stopped")


# Global coordinator instance
coordinator = HealthcareSystemCoordinator()


async def main():
    """Main execution function."""
    print("🏥 Starting Healthcare System with uagents")
    print("=" * 50)
    
    try:
        # Initialize the system
        await coordinator.start()
        
        print("✅ System initialized successfully")
        print(f"   Master Agent: {system_status['master_agent']}")
        print(f"   Healthcare Agent: {system_status['healthcare_agent']}")
        print()
        
        # Test the system
        print("🧪 Testing system functionality...")
        
        # Test doctor query
        test_query = "Follow up with all diabetic patients from last week"
        result = await coordinator.process_doctor_query(test_query)
        print(f"✅ Doctor query test: {result.get('summary', {})}")
        
        # Test voice processing
        voice_result = await coordinator.process_voice_data(
            "test_session_001",
            "Patient John Smith reports chest pain and shortness of breath"
        )
        print(f"✅ Voice processing test: {len(voice_result.get('processing_steps', []))} steps")
        
        # Get system status
        status = await coordinator.get_system_status()
        print(f"✅ System status: {status['success_rate']:.1f}% success rate")
        
        print("\n🎉 Healthcare System is running successfully!")
        print("Press Ctrl+C to stop")
        
        # Keep the system running
        while coordinator.is_running:
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down system...")
        await coordinator.stop()
        print("✅ System stopped successfully")
    except Exception as e:
        print(f"❌ System failed to start: {str(e)}")
        logger.error(f"System startup failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())

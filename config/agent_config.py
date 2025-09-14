"""
Agent configuration for the HackMIT Healthcare Voice Processing System.
Updated for uagents framework.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class AgentConfig:
    """Configuration class for the uagents-based healthcare system."""
    
    # Agent identity
    AGENT_NAME = "healthcare_voice_agent"
    AGENT_VERSION = "0.1.0"
    
    # uAgents settings
    UAGENTS_SEED = os.getenv("UAGENTS_SEED", None)
    UAGENTS_ENDPOINT = os.getenv("UAGENTS_ENDPOINT", None)
    UAGENTS_MAILBOX_KEY = os.getenv("UAGENTS_MAILBOX_KEY", None)
    
    # Agentverse settings for online connectivity
    AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY", None)
    AGENTVERSE_ENDPOINT = os.getenv("AGENTVERSE_ENDPOINT", "https://agentverse.ai")
    AGENTVERSE_MAILBOX_URL = os.getenv("AGENTVERSE_MAILBOX_URL", None)
    
    # Agent addresses (will be generated)
    MASTER_AGENT_ADDRESS = os.getenv("MASTER_AGENT_ADDRESS", None)
    HEALTHCARE_AGENT_ADDRESS = os.getenv("HEALTHCARE_AGENT_ADDRESS", None)
    
    # Webhook server settings
    WEBHOOK_HOST = "localhost"
    WEBHOOK_PORT = 8000
    WEBHOOK_ENDPOINT = "/webhook/voice-data"
    
    # Database service settings
    DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://localhost:3000/api/query")
    DATABASE_SERVICE_API_KEY = os.getenv("DATABASE_SERVICE_API_KEY", "your-api-key-here")
    
    # LiveKit server settings
    LIVEKIT_SERVER_URL = os.getenv("LIVEKIT_SERVER_URL", "http://localhost:7880")
    
    # Legacy wallet settings (for compatibility)
    WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY", None)
    WALLET_SEED_PHRASE = os.getenv("WALLET_SEED_PHRASE", None)
    
    # Logging
    LOG_LEVEL = "INFO"
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        required_env_vars = []
        
        if not cls.DATABASE_SERVICE_URL.startswith("http"):
            required_env_vars.append("DATABASE_SERVICE_URL")
        
        if cls.DATABASE_SERVICE_API_KEY == "your-api-key-here":
            required_env_vars.append("DATABASE_SERVICE_API_KEY")
        
        if required_env_vars:
            print(f"Warning: Missing environment variables: {', '.join(required_env_vars)}")
            print("Please create a .env file with the required variables.")
        
        return len(required_env_vars) == 0

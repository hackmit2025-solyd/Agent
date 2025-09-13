"""
Fetch.ai Master Agent using AEA Framework
"""
import asyncio
import logging
from typing import Optional

from aea.agent import Agent
from aea.configurations.base import ConnectionConfig, PublicId
from aea.connections.base import Connection
from aea.context.base import AgentContext
from aea.protocols.base import Message
from aea.skills.base import Skill

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MasterAgent(Agent):
    """A simple Fetch.ai agent that responds to messages."""
    
    def __init__(self, name: str = "master_agent", **kwargs):
        super().__init__(name, **kwargs)
        self.logger = logger
        
    async def setup(self) -> None:
        """Set up the agent."""
        self.logger.info(f"Setting up {self.name}")
        
    async def act(self) -> None:
        """Perform agent actions."""
        # This is where the agent would perform its main logic
        pass
        
    async def teardown(self) -> None:
        """Tear down the agent."""
        self.logger.info(f"Tearing down {self.name}")

class QueryMessage(Message):
    """Message for queries."""
    protocol_id = PublicId.from_str("fetchai/query/1.0.0")
    
    def __init__(self, text: str, **kwargs):
        super().__init__(**kwargs)
        self.text = text

class ResponseMessage(Message):
    """Message for responses."""
    protocol_id = PublicId.from_str("fetchai/response/1.0.0")
    
    def __init__(self, result: str, **kwargs):
        super().__init__(**kwargs)
        self.result = result

async def main():
    """Main function to run the agent."""
    agent = MasterAgent()
    
    try:
        await agent.setup()
        logger.info(f"Agent {agent.name} is running...")
        logger.info("Press Ctrl+C to stop the agent")
        
        # Keep the agent running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down agent...")
    finally:
        await agent.teardown()

if __name__ == "__main__":
    asyncio.run(main())

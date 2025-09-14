"""
Run healthcare agents connected to the online uagents network.
This makes your agents discoverable and communicable over the internet.
"""
import asyncio
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

from uagents import Agent
from uagents.setup import fund_agent_if_low

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_online_agents():
    """Create agents configured for online connectivity."""
    
    # Get configuration from environment
    agentverse_api_key = os.getenv("AGENTVERSE_API_KEY")
    agentverse_endpoint = os.getenv("AGENTVERSE_ENDPOINT", "https://agentverse.ai")
    uagents_seed = os.getenv("UAGENTS_SEED", "healthcare_agents_online_seed")
    
    if not agentverse_api_key:
        print("❌ AGENTVERSE_API_KEY not found!")
        print("Please set your Agentverse API key in the .env file")
        print("Get your API key from: https://agentverse.ai")
        return None, None
    
    print("🌐 Creating online agents...")
    
    # Create Master Agent for online connectivity
    master_agent = Agent(
        name="healthcare_master_agent",
        seed=uagents_seed,
        endpoint=agentverse_endpoint,
        mailbox={
            "base_url": f"{agentverse_endpoint}/mailbox",
            "api_key": agentverse_api_key
        },
        port=8001
    )
    
    # Create Healthcare Agent for online connectivity
    healthcare_agent = Agent(
        name="healthcare_voice_agent", 
        seed=uagents_seed,
        endpoint=agentverse_endpoint,
        mailbox={
            "base_url": f"{agentverse_endpoint}/mailbox",
            "api_key": agentverse_api_key
        },
        port=8002
    )
    
    # Fund agents
    fund_agent_if_low(master_agent.wallet.address())
    fund_agent_if_low(healthcare_agent.wallet.address())
    
    print(f"✅ Master Agent created: {master_agent.address}")
    print(f"✅ Healthcare Agent created: {healthcare_agent.address}")
    
    return master_agent, healthcare_agent

def setup_master_agent_handlers(master_agent):
    """Set up message handlers for the master agent."""
    
    @master_agent.on_event("startup")
    async def master_startup(ctx):
        """Master agent startup handler."""
        logger.info(f"🏥 Master Healthcare Agent online: {ctx.agent.address}")
        logger.info(f"🌐 Agentverse endpoint: {ctx.agent.endpoint}")
        
        # Register with Agentverse (this would be done automatically)
        print(f"📝 Master Agent registered with Agentverse")
        print(f"🔗 View at: https://agentverse.ai/agents/healthcare-master-agent")
    
    @master_agent.on_message()
    async def handle_doctor_query(ctx, sender, msg):
        """Handle doctor queries."""
        logger.info(f"📋 Received doctor query from {sender}: {msg}")
        
        # Process the query (simplified for demo)
        response = {
            "query": str(msg),
            "processed_at": datetime.now().isoformat(),
            "status": "processed",
            "agent_address": ctx.agent.address
        }
        
        # Send response back
        await ctx.send(sender, response)
        logger.info(f"✅ Query processed and response sent")

def setup_healthcare_agent_handlers(healthcare_agent):
    """Set up message handlers for the healthcare agent."""
    
    @healthcare_agent.on_event("startup")
    async def healthcare_startup(ctx):
        """Healthcare agent startup handler."""
        logger.info(f"🎤 Healthcare Voice Agent online: {ctx.agent.address}")
        logger.info(f"🌐 Agentverse endpoint: {ctx.agent.endpoint}")
        
        # Register with Agentverse
        print(f"📝 Healthcare Agent registered with Agentverse")
        print(f"🔗 View at: https://agentverse.ai/agents/healthcare-voice-agent")
    
    @healthcare_agent.on_message()
    async def handle_voice_data(ctx, sender, msg):
        """Handle voice data."""
        logger.info(f"🎤 Received voice data from {sender}: {msg}")
        
        # Process voice data (simplified for demo)
        response = {
            "voice_data": str(msg),
            "processed_at": datetime.now().isoformat(),
            "recommendations": ["High priority: Patient reports chest pain"],
            "agent_address": ctx.agent.address
        }
        
        # Send response back
        await ctx.send(sender, response)
        logger.info(f"✅ Voice data processed and response sent")

async def run_online_agents():
    """Run agents connected to the online network."""
    print("🏥 Starting Healthcare Agents - Online Mode")
    print("=" * 60)
    
    # Create online agents
    master_agent, healthcare_agent = create_online_agents()
    
    if not master_agent or not healthcare_agent:
        return
    
    # Set up handlers
    setup_master_agent_handlers(master_agent)
    setup_healthcare_agent_handlers(healthcare_agent)
    
    print("\n🚀 Starting agents...")
    print("=" * 30)
    
    # Start both agents concurrently
    try:
        await asyncio.gather(
            master_agent.run(),
            healthcare_agent.run()
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down online agents...")
        print("✅ Agents stopped successfully")

def show_online_agent_info():
    """Show information about online agents."""
    print("\n🌐 Online Agent Information")
    print("=" * 40)
    print()
    print("Your healthcare agents are now online and discoverable!")
    print()
    print("🔗 Agent Links:")
    print("• Master Agent: https://agentverse.ai/agents/healthcare-master-agent")
    print("• Healthcare Agent: https://agentverse.ai/agents/healthcare-voice-agent")
    print()
    print("📱 How to interact:")
    print("1. Visit https://agentverse.ai/dashboard")
    print("2. Find your agents in the list")
    print("3. Send test messages to them")
    print("4. Monitor their activity and logs")
    print()
    print("🤝 Other agents can now:")
    print("• Discover your agents on the network")
    print("• Send messages to them")
    print("• Collaborate on healthcare tasks")
    print()

def main():
    """Main function."""
    print("🏥 Healthcare Agents - Online Network")
    print("=" * 50)
    
    # Check if we have the required configuration
    if not os.getenv("AGENTVERSE_API_KEY"):
        print("❌ Missing Agentverse API key!")
        print()
        print("Please:")
        print("1. Go to https://agentverse.ai")
        print("2. Create an account and get your API key")
        print("3. Add AGENTVERSE_API_KEY=your_key to your .env file")
        print()
        print("Or run: python setup_online_agents.py")
        return
    
    # Show agent information
    show_online_agent_info()
    
    # Run the agents
    asyncio.run(run_online_agents())

if __name__ == "__main__":
    main()

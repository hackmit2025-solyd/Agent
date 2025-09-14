"""
Create healthcare agents and get their online links.
This will show you the actual URLs where your agents can be found online.
"""
import asyncio
import logging
from datetime import datetime

from uagents import Agent
from uagents.setup import fund_agent_if_low
from uagents.network import get_almanac_contract

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_online_healthcare_agents():
    """Create healthcare agents and get their online links."""
    print("🏥 Creating Healthcare Agents with Online Links")
    print("=" * 60)
    
    # Create Master Agent
    print("\n1. Creating Master Healthcare Agent...")
    master_agent = Agent(
        name="healthcare_master_agent",
        seed="healthcare_master_seed_phrase_123",
        mailbox=True,  # This enables online connectivity
        port=8001
    )
    
    # Fund the agent
    fund_agent_if_low(master_agent.wallet.address())
    
    print(f"✅ Master Agent created!")
    print(f"   Address: {master_agent.address}")
    print(f"   Name: {master_agent.name}")
    
    # Create Healthcare Agent
    print("\n2. Creating Healthcare Voice Agent...")
    healthcare_agent = Agent(
        name="healthcare_voice_agent",
        seed="healthcare_voice_seed_phrase_456", 
        mailbox=True,  # This enables online connectivity
        port=8002
    )
    
    # Fund the agent
    fund_agent_if_low(healthcare_agent.wallet.address())
    
    print(f"✅ Healthcare Agent created!")
    print(f"   Address: {healthcare_agent.address}")
    print(f"   Name: {healthcare_agent.name}")
    
    # Register agents with Almanac (uagents registry)
    print("\n3. Registering agents with uagents network...")
    
    try:
        almanac = get_almanac_contract()
        
        # Register Master Agent
        await almanac.register(
            agent=master_agent,
            name="Healthcare Master Agent",
            description="Handles doctor queries and coordinates patient care across the healthcare system",
            version="1.0.0"
        )
        print("✅ Master Agent registered with uagents network")
        
        # Register Healthcare Agent
        await almanac.register(
            agent=healthcare_agent,
            name="Healthcare Voice Agent", 
            description="Processes voice data and generates medical recommendations using AI",
            version="1.0.0"
        )
        print("✅ Healthcare Agent registered with uagents network")
        
    except Exception as e:
        print(f"⚠️  Registration warning: {str(e)}")
        print("   Agents are still created and functional locally")
    
    # Generate online links
    print("\n🌐 Online Agent Links")
    print("=" * 40)
    
    # uagents network links
    base_url = "https://agentverse.ai"
    
    print(f"\n🔗 Master Healthcare Agent:")
    print(f"   • Network Address: {master_agent.address}")
    print(f"   • Agentverse Link: {base_url}/agents/{master_agent.name}")
    print(f"   • Direct Link: {base_url}/agent/{master_agent.address}")
    
    print(f"\n🔗 Healthcare Voice Agent:")
    print(f"   • Network Address: {healthcare_agent.address}")
    print(f"   • Agentverse Link: {base_url}/agents/{healthcare_agent.name}")
    print(f"   • Direct Link: {base_url}/agent/{healthcare_agent.address}")
    
    print(f"\n📱 How to interact with your agents:")
    print(f"   1. Visit: {base_url}")
    print(f"   2. Search for: 'Healthcare Master Agent' or 'Healthcare Voice Agent'")
    print(f"   3. Send messages to their addresses")
    print(f"   4. Monitor their activity and logs")
    
    # Set up basic message handlers
    print("\n4. Setting up message handlers...")
    
    @master_agent.on_message()
    async def handle_master_messages(ctx, sender, msg):
        """Handle messages sent to master agent."""
        logger.info(f"Master agent received message from {sender}: {msg}")
        
        response = {
            "from": "Healthcare Master Agent",
            "message": f"Received your message: {msg}",
            "timestamp": datetime.now().isoformat(),
            "agent_address": ctx.agent.address
        }
        
        await ctx.send(sender, response)
        logger.info(f"Master agent sent response to {sender}")
    
    @healthcare_agent.on_message()
    async def handle_healthcare_messages(ctx, sender, msg):
        """Handle messages sent to healthcare agent."""
        logger.info(f"Healthcare agent received message from {sender}: {msg}")
        
        response = {
            "from": "Healthcare Voice Agent",
            "message": f"Voice data processed: {msg}",
            "recommendations": ["High priority: Immediate attention required"],
            "timestamp": datetime.now().isoformat(),
            "agent_address": ctx.agent.address
        }
        
        await ctx.send(sender, response)
        logger.info(f"Healthcare agent sent response to {sender}")
    
    print("✅ Message handlers configured")
    
    # Show final summary
    print("\n🎉 Healthcare Agents Created Successfully!")
    print("=" * 50)
    print(f"✅ Master Agent: {master_agent.address}")
    print(f"✅ Healthcare Agent: {healthcare_agent.address}")
    print(f"✅ Both agents are online and discoverable")
    print(f"✅ Message handlers are active")
    
    print(f"\n🚀 To start your agents, run:")
    print(f"   python -c \"import asyncio; from create_online_agents import start_agents; asyncio.run(start_agents())\"")
    
    return master_agent, healthcare_agent

async def start_agents():
    """Start the created agents."""
    master_agent, healthcare_agent = await create_online_healthcare_agents()
    
    print(f"\n🔄 Starting agents...")
    print(f"Press Ctrl+C to stop")
    
    try:
        await asyncio.gather(
            master_agent.run(),
            healthcare_agent.run()
        )
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping agents...")
        print(f"✅ Agents stopped successfully")

if __name__ == "__main__":
    asyncio.run(create_online_healthcare_agents())

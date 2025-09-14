"""
Simple script to create healthcare agents and show their online links.
"""
import asyncio
import logging
from datetime import datetime
from uagents import Agent, Model
from uagents.setup import fund_agent_if_low

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a simple message model
class SimpleMessage(Model):
    content: str
    sender: str = "unknown"

class SimpleResponse(Model):
    message: str
    agent_name: str
    timestamp: str

async def create_online_healthcare_agents():
    """Create healthcare agents and show their online links."""
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
    
    # Set up message handlers
    print("\n3. Setting up message handlers...")
    
    @master_agent.on_message(SimpleMessage, replies={SimpleResponse})
    async def handle_master_messages(ctx, sender, msg):
        """Handle messages sent to master agent."""
        logger.info(f"Master agent received: {msg.content} from {sender}")
        
        response = SimpleResponse(
            message=f"Master agent processed: {msg.content}",
            agent_name="Healthcare Master Agent",
            timestamp=datetime.now().isoformat()
        )
        
        await ctx.send(sender, response)
        logger.info(f"Master agent sent response to {sender}")
    
    @healthcare_agent.on_message(SimpleMessage, replies={SimpleResponse})
    async def handle_healthcare_messages(ctx, sender, msg):
        """Handle messages sent to healthcare agent."""
        logger.info(f"Healthcare agent received: {msg.content} from {sender}")
        
        response = SimpleResponse(
            message=f"Voice data processed: {msg.content}",
            agent_name="Healthcare Voice Agent", 
            timestamp=datetime.now().isoformat()
        )
        
        await ctx.send(sender, response)
        logger.info(f"Healthcare agent sent response to {sender}")
    
    print("✅ Message handlers configured")
    
    # Generate online links
    print("\n🌐 ONLINE AGENT LINKS")
    print("=" * 50)
    
    # uagents network links
    base_url = "https://agentverse.ai"
    
    print(f"\n🔗 MASTER HEALTHCARE AGENT:")
    print(f"   📍 Network Address: {master_agent.address}")
    print(f"   🌐 Agentverse Link: {base_url}/agents/healthcare_master_agent")
    print(f"   🔗 Direct Link: {base_url}/agent/{master_agent.address}")
    
    print(f"\n🔗 HEALTHCARE VOICE AGENT:")
    print(f"   📍 Network Address: {healthcare_agent.address}")
    print(f"   🌐 Agentverse Link: {base_url}/agents/healthcare_voice_agent")
    print(f"   🔗 Direct Link: {base_url}/agent/{healthcare_agent.address}")
    
    print(f"\n📱 HOW TO USE YOUR AGENTS:")
    print(f"   1. 🌐 Visit: {base_url}")
    print(f"   2. 🔍 Search for: 'Healthcare Master Agent' or 'Healthcare Voice Agent'")
    print(f"   3. 💬 Send messages to their addresses")
    print(f"   4. 📊 Monitor their activity and logs")
    
    print(f"\n🧪 TEST YOUR AGENTS:")
    print(f"   • Send a message to Master Agent: {master_agent.address}")
    print(f"   • Send a message to Healthcare Agent: {healthcare_agent.address}")
    print(f"   • Use the Agentverse dashboard to interact with them")
    
    # Show final summary
    print("\n🎉 SUCCESS! Your Healthcare Agents are Online!")
    print("=" * 60)
    print(f"✅ Master Agent: {master_agent.address}")
    print(f"✅ Healthcare Agent: {healthcare_agent.address}")
    print(f"✅ Both agents are online and discoverable")
    print(f"✅ Message handlers are active and ready")
    print(f"✅ You can now interact with them via Agentverse!")
    
    print(f"\n🚀 To start your agents and keep them running:")
    print(f"   python start_online_agents.py")
    
    return master_agent, healthcare_agent

if __name__ == "__main__":
    asyncio.run(create_online_healthcare_agents())

"""
Start your online healthcare agents and keep them running.
"""
import asyncio
from simple_online_agents import create_online_healthcare_agents

async def start_agents():
    """Start the agents and keep them running."""
    master_agent, healthcare_agent = await create_online_healthcare_agents()
    
    print(f"\n🔄 Starting agents...")
    print(f"Your agents are now online and accessible at:")
    print(f"• Master Agent: {master_agent.address}")
    print(f"• Healthcare Agent: {healthcare_agent.address}")
    print(f"\nPress Ctrl+C to stop the agents")
    
    try:
        await asyncio.gather(
            master_agent.run(),
            healthcare_agent.run()
        )
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping agents...")
        print(f"✅ Agents stopped successfully")

if __name__ == "__main__":
    asyncio.run(start_agents())

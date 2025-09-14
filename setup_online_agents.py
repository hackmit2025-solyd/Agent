"""
Simple setup script to connect healthcare agents to the online uagents network.
This will make your agents discoverable and communicable over the internet.
"""
import os
import asyncio
from uagents import Agent
from uagents.setup import fund_agent_if_low

def show_agentverse_setup_instructions():
    """Show instructions for setting up Agentverse connection."""
    print("🌐 UAgents Online Network Setup")
    print("=" * 50)
    print()
    print("To connect your healthcare agents to the online uagents network:")
    print()
    print("1. 📝 Get Agentverse API Key:")
    print("   • Go to: https://agentverse.ai")
    print("   • Create an account or sign in")
    print("   • Navigate to your dashboard")
    print("   • Copy your API key")
    print()
    print("2. 🔧 Set Environment Variables:")
    print("   • Create a .env file with:")
    print("     AGENTVERSE_API_KEY=your_api_key_here")
    print("     UAGENTS_ENDPOINT=https://agentverse.ai")
    print("     UAGENTS_MAILBOX_KEY=your_mailbox_key_here")
    print()
    print("3. 🚀 Run Online Agents:")
    print("   • python run_online_agents.py")
    print()
    print("4. 🔗 View Your Agents Online:")
    print("   • Your agents will be visible at: https://agentverse.ai/agents")
    print("   • Other agents can discover and communicate with yours")
    print()
    print("5. 📱 Test Online Communication:")
    print("   • Use the Agentverse dashboard to send test messages")
    print("   • Monitor agent activity and logs")
    print()

def create_online_agent_config():
    """Create configuration for online agents."""
    config_content = """# Online UAgents Configuration
# Copy this to your .env file and update with your actual values

# Agentverse API Configuration
AGENTVERSE_API_KEY=your_agentverse_api_key_here
AGENTVERSE_ENDPOINT=https://agentverse.ai
AGENTVERSE_MAILBOX_URL=https://agentverse.ai/mailbox

# UAgents Configuration
UAGENTS_SEED=healthcare_agents_online_seed_phrase
UAGENTS_ENDPOINT=https://agentverse.ai
UAGENTS_MAILBOX_KEY=your_mailbox_key_here

# Agent Names for Online Registration
MASTER_AGENT_NAME=Healthcare Master Agent
HEALTHCARE_AGENT_NAME=Healthcare Voice Agent

# Service URLs (keep these as local for now)
DATABASE_SERVICE_URL=http://localhost:3000/api/query
DATABASE_SERVICE_API_KEY=your-api-key-here
LIVEKIT_SERVER_URL=http://localhost:7880
WEBHOOK_PORT=8000
"""
    
    with open('.env.online', 'w') as f:
        f.write(config_content)
    
    print("✅ Online configuration template created: .env.online")
    print("📝 Copy the contents to your .env file and update with your API keys")

def show_agent_links():
    """Show how to find agent links once online."""
    print("\n🔗 Finding Your Online Agents")
    print("=" * 40)
    print()
    print("Once your agents are online, you can find them at:")
    print()
    print("1. 🌐 Agentverse Dashboard:")
    print("   • https://agentverse.ai/dashboard")
    print("   • View all your registered agents")
    print("   • Monitor agent activity and logs")
    print()
    print("2. 🔍 Agent Discovery:")
    print("   • https://agentverse.ai/agents")
    print("   • Browse all public agents")
    print("   • Search for specific agent types")
    print()
    print("3. 📡 Agent Communication:")
    print("   • Send messages between agents")
    print("   • Test agent responses")
    print("   • Monitor communication logs")
    print()
    print("4. 📊 Agent Analytics:")
    print("   • View agent performance metrics")
    print("   • Monitor message throughput")
    print("   • Track agent uptime")
    print()

def main():
    """Main setup function."""
    print("🏥 Healthcare Agents - Online Setup")
    print("=" * 50)
    print()
    
    while True:
        print("Choose an option:")
        print("1. Show setup instructions")
        print("2. Create configuration template")
        print("3. Show how to find online agents")
        print("4. Exit")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            show_agentverse_setup_instructions()
        elif choice == "2":
            create_online_agent_config()
        elif choice == "3":
            show_agent_links()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()

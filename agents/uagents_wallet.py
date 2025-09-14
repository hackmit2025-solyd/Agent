"""
Wallet management for uagents-based healthcare system.
Handles agent identity and basic operations using uagents framework.
"""
import os
from typing import Dict, Any, Optional
from uagents import Agent
from uagents.crypto import Identity
from config.agent_config import AgentConfig


class UAgentsWalletManager:
    """Manages uagents wallet operations for the healthcare system."""
    
    def __init__(self):
        self.identities = {}
        self.agents = {}
        
    def create_agent_identity(self, agent_name: str, seed: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new agent identity using uagents.
        
        Args:
            agent_name: Name of the agent
            seed: Optional seed phrase for deterministic generation
            
        Returns:
            dict: Agent information including address and identity
        """
        try:
            # Create identity
            if seed:
                identity = Identity.from_seed(seed, 0)
            else:
                identity = Identity.generate()
            
            # Create agent
            agent = Agent(
                name=agent_name,
                seed=seed,
                endpoint=AgentConfig.UAGENTS_ENDPOINT,
                mailbox=AgentConfig.UAGENTS_MAILBOX_KEY
            )
            
            agent_info = {
                "name": agent_name,
                "address": agent.address,
                "identity": identity,
                "agent": agent,
                "seed": seed
            }
            
            # Store for later use
            self.identities[agent_name] = identity
            self.agents[agent_name] = agent
            
            print(f"Created agent identity for {agent_name}:")
            print(f"Address: {agent.address}")
            if seed:
                print(f"Seed: {seed}")
            
            return agent_info
            
        except Exception as e:
            print(f"Failed to create agent identity: {str(e)}")
            raise
    
    def load_agent_identity(self, agent_name: str, seed: str) -> Dict[str, Any]:
        """
        Load an existing agent identity from seed.
        
        Args:
            agent_name: Name of the agent
            seed: Seed phrase for the identity
            
        Returns:
            dict: Agent information
        """
        try:
            # Create identity from seed
            identity = Identity.from_seed(seed, 0)
            
            # Create agent
            agent = Agent(
                name=agent_name,
                seed=seed,
                endpoint=AgentConfig.UAGENTS_ENDPOINT,
                mailbox=AgentConfig.UAGENTS_MAILBOX_KEY
            )
            
            agent_info = {
                "name": agent_name,
                "address": agent.address,
                "identity": identity,
                "agent": agent,
                "seed": seed
            }
            
            # Store for later use
            self.identities[agent_name] = identity
            self.agents[agent_name] = agent
            
            print(f"Loaded agent identity for {agent_name}:")
            print(f"Address: {agent.address}")
            
            return agent_info
            
        except Exception as e:
            print(f"Failed to load agent identity: {str(e)}")
            raise
    
    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Get an existing agent by name."""
        return self.agents.get(agent_name)
    
    def get_identity(self, agent_name: str) -> Optional[Identity]:
        """Get an existing identity by name."""
        return self.identities.get(agent_name)
    
    def list_agents(self) -> Dict[str, str]:
        """List all created agents and their addresses."""
        return {name: agent.address for name, agent in self.agents.items()}
    
    def save_agent_config(self, agent_name: str, agent_info: Dict[str, Any]):
        """Save agent configuration to environment file."""
        env_content = f"""# Generated uagents configuration
UAGENTS_SEED={agent_info.get('seed', '')}
UAGENTS_ENDPOINT={AgentConfig.UAGENTS_ENDPOINT or ''}
UAGENTS_MAILBOX_KEY={AgentConfig.UAGENTS_MAILBOX_KEY or ''}

# Agent addresses
{agent_name.upper()}_ADDRESS={agent_info['address']}

# Add other environment variables as needed
DATABASE_SERVICE_URL={AgentConfig.DATABASE_SERVICE_URL}
DATABASE_SERVICE_API_KEY={AgentConfig.DATABASE_SERVICE_API_KEY}
LIVEKIT_SERVER_URL={AgentConfig.LIVEKIT_SERVER_URL}
WEBHOOK_PORT={AgentConfig.WEBHOOK_PORT}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print(f"Agent configuration saved to .env file for {agent_name}")
    
    def create_system_agents(self) -> Dict[str, Dict[str, Any]]:
        """Create all system agents."""
        agents = {}
        
        # Create master agent
        master_seed = AgentConfig.UAGENTS_SEED or "master_agent_seed_phrase_here"
        agents["master"] = self.create_agent_identity("master_agent", master_seed)
        
        # Create healthcare agent
        healthcare_seed = AgentConfig.UAGENTS_SEED or "healthcare_agent_seed_phrase_here"
        agents["healthcare"] = self.create_agent_identity("healthcare_agent", healthcare_seed)
        
        # Save configuration
        for agent_name, agent_info in agents.items():
            self.save_agent_config(agent_name, agent_info)
        
        return agents
    
    def get_balance(self, agent_name: str) -> float:
        """
        Get the current balance of an agent's wallet.
        Note: This is a placeholder for actual balance checking.
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        print(f"Balance check for agent {agent_name}: {agent.address}")
        print("Note: Implement actual balance checking with uagents network API")
        return 0.0


def main():
    """Command-line interface for wallet management."""
    import sys
    
    wallet_manager = UAgentsWalletManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            agent_name = sys.argv[2] if len(sys.argv) > 2 else "test_agent"
            seed = sys.argv[3] if len(sys.argv) > 3 else None
            wallet_manager.create_agent_identity(agent_name, seed)
            
        elif command == "load":
            agent_name = sys.argv[2] if len(sys.argv) > 2 else "test_agent"
            seed = sys.argv[3] if len(sys.argv) > 3 else None
            if not seed:
                print("Error: Seed required for loading agent")
                return
            wallet_manager.load_agent_identity(agent_name, seed)
            
        elif command == "create_system":
            wallet_manager.create_system_agents()
            
        elif command == "list":
            agents = wallet_manager.list_agents()
            for name, address in agents.items():
                print(f"{name}: {address}")
                
        else:
            print("Unknown command")
    else:
        print("Usage:")
        print("  python uagents_wallet.py create <agent_name> [seed]  - Create a new agent")
        print("  python uagents_wallet.py load <agent_name> <seed>     - Load existing agent")
        print("  python uagents_wallet.py create_system               - Create all system agents")
        print("  python uagents_wallet.py list                        - List all agents")


if __name__ == "__main__":
    main()

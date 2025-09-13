"""
Wallet management for Fetch.ai agents.
Handles wallet creation, loading, and basic operations.
Simplified version for feasibility testing.
"""
import os
import secrets
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from config.agent_config import AgentConfig


class WalletIdentity:
    """Simple identity class for agent."""
    def __init__(self, name, address, public_key):
        self.name = name
        self.address = address
        self.public_key = public_key


class WalletManager:
    """Manages Fetch.ai wallet operations for the agent."""
    
    def __init__(self):
        self.identity = None
        self.private_key = None
        
    def create_new_wallet(self, save_to_file=True):
        """
        Create a new wallet (simplified for feasibility testing).
        
        Args:
            save_to_file (bool): Whether to save the private key to a file
            
        Returns:
            dict: Wallet information including address and private key
        """
        # Generate a new private key using cryptography
        private_key = ec.generate_private_key(ec.SECP256K1())
        
        # Get private key bytes
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Get public key
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Create a simple address (for testing - in production use proper Fetch.ai address generation)
        address_hash = hashes.Hash(hashes.SHA256())
        address_hash.update(public_key_bytes)
        address = "fetch" + address_hash.finalize().hex()[:32]
        
        # Create identity
        identity = WalletIdentity("healthcare_agent", address, public_key_bytes.decode())
        
        wallet_info = {
            "address": address,
            "private_key": private_key_bytes.decode(),
            "public_key": public_key_bytes.decode(),
            "identity": identity
        }
        
        if save_to_file:
            self._save_wallet_to_env(wallet_info)
        
        self.identity = identity
        self.private_key = private_key_bytes.decode()
        
        print(f"New wallet created:")
        print(f"Address: {wallet_info['address'][:20]}...")
        print(f"Private key saved to environment configuration")
        
        return wallet_info
    
    def load_existing_wallet(self, private_key=None):
        """
        Load an existing wallet from private key (simplified for testing).
        
        Args:
            private_key (str): The private key to load. If None, loads from environment.
            
        Returns:
            dict: Wallet information
        """
        if private_key is None:
            private_key = AgentConfig.WALLET_PRIVATE_KEY
            
        if not private_key:
            raise ValueError("No private key provided and none found in environment")
        
        # For feasibility testing, create a mock identity
        # In production, parse the actual private key
        mock_address = "fetch" + secrets.token_hex(16)
        identity = WalletIdentity("healthcare_agent", mock_address, "mock_public_key")
        
        wallet_info = {
            "address": mock_address,
            "private_key": private_key,
            "public_key": "mock_public_key",
            "identity": identity
        }
        
        self.identity = identity
        self.private_key = private_key
        
        print(f"Wallet loaded:")
        print(f"Address: {wallet_info['address'][:20]}...")
        
        return wallet_info
    
    def get_balance(self):
        """
        Get the current balance of the wallet.
        Note: This is a placeholder for actual balance checking.
        """
        if not self.identity:
            raise ValueError("No wallet loaded")
        
        # In a real implementation, you would query the Fetch.ai network
        # For now, return a placeholder
        print(f"Balance check for address: {self.identity.address}")
        print("Note: Implement actual balance checking with Fetch.ai network API")
        return 0
    
    def _save_wallet_to_env(self, wallet_info):
        """Save wallet information to environment file."""
        env_content = f"""# Generated wallet configuration
WALLET_PRIVATE_KEY={wallet_info['private_key']}
WALLET_ADDRESS={wallet_info['address']}
WALLET_PUBLIC_KEY={wallet_info['public_key']}

# Add other environment variables as needed
DATABASE_SERVICE_URL=http://localhost:3000/api/query
DATABASE_SERVICE_API_KEY=your-api-key-here
LIVEKIT_SERVER_URL=http://localhost:7880
WEBHOOK_PORT=8000
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("Wallet configuration saved to .env file")


def main():
    """Command-line interface for wallet management."""
    import sys
    
    wallet_manager = WalletManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        print("Creating new wallet...")
        wallet_manager.create_new_wallet()
    elif len(sys.argv) > 1 and sys.argv[1] == "load":
        print("Loading existing wallet...")
        try:
            wallet_manager.load_existing_wallet()
        except ValueError as e:
            print(f"Error: {e}")
            print("Use 'python wallet_manager.py create' to create a new wallet")
    else:
        print("Usage:")
        print("  python wallet_manager.py create  - Create a new wallet")
        print("  python wallet_manager.py load    - Load existing wallet from .env")


if __name__ == "__main__":
    main()

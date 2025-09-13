"""
Main runner for the HackMIT Healthcare Voice Processing Agent System.
Coordinates webhook server, agent, and provides testing interface.
"""
import asyncio
import threading
import time
import sys
import subprocess
from pathlib import Path

from agents.healthcare_agent import HealthcareAgent
from config.agent_config import AgentConfig


class AgentSystem:
    """Main system coordinator for the healthcare agent."""
    
    def __init__(self):
        self.agent = None
        self.webhook_server_process = None
        self.agent_task = None
    
    async def start_agent(self):
        """Start the healthcare agent."""
        print("🤖 Starting Healthcare Agent...")
        self.agent = HealthcareAgent()
        await self.agent.initialize()
        
        # Start agent in background task
        self.agent_task = asyncio.create_task(self.agent.start())
        print("✅ Healthcare Agent started successfully")
    
    def start_webhook_server(self):
        """Start the webhook server."""
        print("🌐 Starting Webhook Server...")
        try:
            self.webhook_server_process = subprocess.Popen([
                sys.executable, "-m", "services.webhook_receiver"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(3)  # Give server time to start
            print(f"✅ Webhook Server started on http://{AgentConfig.WEBHOOK_HOST}:{AgentConfig.WEBHOOK_PORT}")
            return True
        except Exception as e:
            print(f"❌ Failed to start webhook server: {str(e)}")
            return False
    
    async def run_feasibility_tests(self):
        """Run all feasibility tests."""
        print("\n🧪 Running Feasibility Tests")
        print("=" * 50)
        
        # Test 1: Webhook Reception
        print("\n📡 Test 1: Webhook Reception Feasibility")
        print("-" * 40)
        
        import sys
        import subprocess
        
        webhook_result = subprocess.run([
            sys.executable, "-m", "tests.test_webhook_reception"
        ], capture_output=True, text=True)
        
        if webhook_result.returncode == 0:
            print("✅ Webhook Reception Test: PASSED")
            webhook_success = True
        else:
            print("❌ Webhook Reception Test: FAILED")
            print(webhook_result.stderr)
            webhook_success = False
        
        # Test 2: Database Service Communication
        print("\n💾 Test 2: Database Service Communication")
        print("-" * 40)
        
        db_result = subprocess.run([
            sys.executable, "-m", "tests.test_database_service"
        ], capture_output=True, text=True)
        
        if db_result.returncode == 0:
            print("✅ Database Service Test: PASSED") 
            db_success = True
        else:
            print("❌ Database Service Test: FAILED")
            print(db_result.stderr)
            db_success = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 PHASE 1 FEASIBILITY SUMMARY")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 2
        
        if webhook_success:
            print("✅ Webhook Reception: FEASIBLE")
            print("   ✓ Agent can receive POST requests from external server")
            print("   ✓ Voice data processing pipeline ready")
            tests_passed += 1
        else:
            print("❌ Webhook Reception: NEEDS WORK")
            print("   ⚠ Check webhook server configuration")
        
        if db_success:
            print("✅ Database Service Communication: FEASIBLE")
            print("   ✓ Agent can send queries to database service")
            print("   ✓ JSON response processing working")
            tests_passed += 1
        else:
            print("❌ Database Service Communication: NEEDS WORK")
            print("   ⚠ Check database service availability and configuration")
        
        print(f"\n🎯 Overall Feasibility: {tests_passed}/{total_tests} core concepts verified")
        
        if tests_passed == total_tests:
            print("🎉 PHASE 1 COMPLETE: All core concepts are feasible!")
            print("\n🚀 Ready for Phase 2 Development:")
            print("   • Advanced voice processing")
            print("   • Improved patient data extraction")
            print("   • Production-ready error handling")
            print("   • Real-time agent communication")
        else:
            print("⚠️ Phase 1 needs additional work before proceeding")
        
        return tests_passed == total_tests
    
    async def demo_integration(self):
        """Run a demo showing end-to-end integration."""
        print("\n🎬 Running Integration Demo")
        print("=" * 40)
        
        if not self.agent:
            print("❌ Agent not started - cannot run demo")
            return
        
        # Simulate voice data processing
        sample_voice_data = {
            "session_id": "demo_session_001",
            "timestamp": "2024-01-15T10:30:00Z",
            "transcript": "Hello doctor, this is patient John Doe with ID PAT-12345. I'm experiencing chest pain and shortness of breath.",
            "participant_id": "patient_demo",
            "duration": 20.5,
            "metadata": {"demo": True}
        }
        
        print("📋 Sample Voice Data:")
        print(f"   Session: {sample_voice_data['session_id']}")
        print(f"   Transcript: {sample_voice_data['transcript'][:60]}...")
        
        print("\n🔄 Processing with Healthcare Agent...")
        result = await self.agent.process_voice_data(sample_voice_data)
        
        print("✅ Processing Result:")
        print(f"   Steps completed: {', '.join(result['processing_steps'])}")
        print(f"   Agent address: {result['agent_address']}")
        
        if result['recommendations']:
            print(f"   Recommendations: {len(result['recommendations'])} generated")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"     {i}. {rec['message']} (Priority: {rec['priority']})")
        
        print("🎯 Demo completed successfully!")
    
    async def start_full_system(self):
        """Start the complete system."""
        print("🚀 Starting HackMIT Healthcare Agent System")
        print("=" * 60)
        
        # Start webhook server
        if not self.start_webhook_server():
            print("❌ Failed to start webhook server")
            return False
        
        # Start agent
        await self.start_agent()
        
        print("\n✅ System fully operational!")
        print(f"   Webhook endpoint: http://{AgentConfig.WEBHOOK_HOST}:{AgentConfig.WEBHOOK_PORT}/webhook/voice-data")
        print(f"   Agent address: {self.agent.agent_identity.address}")
        
        return True
    
    async def stop_system(self):
        """Stop all system components."""
        print("\n🛑 Shutting down system...")
        
        # Stop agent
        if self.agent:
            await self.agent.stop()
            print("✅ Agent stopped")
        
        # Stop webhook server
        if self.webhook_server_process:
            self.webhook_server_process.terminate()
            try:
                self.webhook_server_process.wait(timeout=5)
                print("✅ Webhook server stopped")
            except subprocess.TimeoutExpired:
                self.webhook_server_process.kill()
                print("⚠️ Webhook server force killed")
        
        print("✅ System shutdown complete")


async def main():
    """Main application entry point."""
    print("🏥 HackMIT Healthcare Voice Processing Agent")
    print("Phase 1: Foundational Setup & Feasibility Testing")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        print("\nAvailable commands:")
        print("  python main.py test      - Run feasibility tests only")
        print("  python main.py demo      - Run integration demo")
        print("  python main.py run       - Start full system")
        print("  python main.py wallet    - Create/manage agent wallet")
        print("\nDefaulting to feasibility tests...")
        command = "test"
    
    system = AgentSystem()
    
    try:
        if command == "test":
            # Start webhook server for testing
            system.start_webhook_server()
            time.sleep(2)
            
            # Run feasibility tests
            result = await system.run_feasibility_tests()
            
            # Cleanup
            await system.stop_system()
            
            return result
        
        elif command == "demo":
            # Start full system
            await system.start_full_system()
            
            # Run demo
            await system.demo_integration()
            
            print("\nPress Ctrl+C to stop the system...")
            await asyncio.sleep(60)  # Run for 1 minute
        
        elif command == "run":
            # Start full system and keep running
            await system.start_full_system()
            
            print("\nSystem is running... Press Ctrl+C to stop")
            while True:
                await asyncio.sleep(1)
        
        elif command == "wallet":
            # Wallet management
            from agents.wallet_manager import WalletManager
            wallet_manager = WalletManager()
            wallet_manager.create_new_wallet()
        
        else:
            print(f"Unknown command: {command}")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Interrupted by user")
        await system.stop_system()
    except Exception as e:
        print(f"\n❌ System error: {str(e)}")
        await system.stop_system()
        return False
    
    return True


if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

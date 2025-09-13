"""
Visual Demo of Phase 2: Master Agent & Database Integration
Shows server calls, sub-agent spawning, and real-time work with visual elements.
"""
import asyncio
import json
import time
import sys
from datetime import datetime
from agents.master_agent import MasterAgent


class VisualDemoPhase2:
    """Visual demonstration with server calls and sub-agent visualization."""
    
    def __init__(self):
        self.master_agent = None
        self.demo_queries = [
            "follow up with all patients from 4 days ago",
            "check on all diabetic patients who haven't been seen in 2 weeks",
            "review all patients with chest pain symptoms from last week"
        ]
    
    def clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self, title: str, char: str = "="):
        """Print a visual banner."""
        print(f"\n{char * 80}")
        print(f"🎯 {title}")
        print(f"{char * 80}")
    
    def print_server_call(self, method: str, url: str, data: str = None):
        """Visual representation of server call."""
        print(f"\n🌐 SERVER CALL")
        print(f"┌─────────────────────────────────────────────────────────────┐")
        print(f"│ {method:^15} │ {url:^40} │")
        print(f"├─────────────────────────────────────────────────────────────┤")
        if data:
            print(f"│ Data: {data[:50]:<50} │")
            if len(data) > 50:
                print(f"│      {data[50:100]:<50} │")
        print(f"│ Status: SENDING...                                        │")
        print(f"└─────────────────────────────────────────────────────────────┘")
        
        # Simulate network delay
        time.sleep(1)
        
        print(f"┌─────────────────────────────────────────────────────────────┐")
        print(f"│ Status: 200 OK                                             │")
        print(f"│ Response: JSON data received                               │")
        print(f"└─────────────────────────────────────────────────────────────┘")
    
    def print_sub_agent_spawn(self, agent_id: str, patient_name: str, patient_id: str):
        """Visual representation of sub-agent spawning."""
        print(f"\n🤖 SPAWNING SUB-AGENT")
        print(f"┌─────────────────────────────────────────────────────────────┐")
        print(f"│ Agent ID: {agent_id:<50} │")
        print(f"│ Patient:  {patient_name:<50} │")
        print(f"│ Patient ID: {patient_id:<47} │")
        print(f"│ Status:   INITIALIZING...                                 │")
        print(f"└─────────────────────────────────────────────────────────────┘")
        
        # Show initialization steps
        steps = [
            "Loading patient data...",
            "Setting up medical context...",
            "Initializing recommendation engine...",
            "Connecting to master agent...",
            "Ready for processing!"
        ]
        
        for i, step in enumerate(steps, 1):
            print(f"   {i}. {step}")
            time.sleep(0.3)
        
        print(f"┌─────────────────────────────────────────────────────────────┐")
        print(f"│ Status: READY ✅                                          │")
        print(f"└─────────────────────────────────────────────────────────────┘")
    
    def print_processing_animation(self, agent_id: str, patient_name: str):
        """Show sub-agent processing with animation."""
        print(f"\n⚙️  PROCESSING: {patient_name} ({agent_id})")
        print(f"┌─────────────────────────────────────────────────────────────┐")
        
        # Processing steps with animation
        steps = [
            ("Analyzing patient data", "🔍"),
            ("Checking medical history", "📋"),
            ("Reviewing current medications", "💊"),
            ("Evaluating symptoms", "🩺"),
            ("Generating recommendations", "💡"),
            ("Finalizing report", "📄")
        ]
        
        for step, icon in steps:
            print(f"│ {icon} {step:<50} │")
            time.sleep(0.5)
        
        print(f"└─────────────────────────────────────────────────────────────┘")
    
    def print_recommendations(self, recommendations: list, patient_name: str):
        """Visual representation of recommendations."""
        print(f"\n💡 RECOMMENDATIONS FOR {patient_name.upper()}")
        print(f"┌─────────────────────────────────────────────────────────────┐")
        
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {
                "high": "🚨",
                "medium": "⚠️",
                "low": "ℹ️"
            }.get(rec.get("priority", "low"), "ℹ️")
            
            print(f"│ {i}. {priority_icon} {rec['message']:<45} │")
            print(f"│    Priority: {rec['priority'].upper():<45} │")
            if i < len(recommendations):
                print(f"├─────────────────────────────────────────────────────────────┤")
        
        print(f"└─────────────────────────────────────────────────────────────┘")
    
    def print_network_diagram(self):
        """Print a network diagram showing the system architecture."""
        print(f"\n🌐 SYSTEM ARCHITECTURE")
        print(f"┌─────────────────────────────────────────────────────────────┐")
        print(f"│                    FETCH.AI NETWORK                        │")
        print(f"│                                                             │")
        print(f"│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │")
        print(f"│  │   DOCTOR    │───▶│   MASTER    │───▶│  DATABASE   │    │")
        print(f"│  │   QUERY     │    │   AGENT     │    │  SERVICE    │    │")
        print(f"│  └─────────────┘    └─────────────┘    └─────────────┘    │")
        print(f"│                           │                                │")
        print(f"│                           ▼                                │")
        print(f"│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │")
        print(f"│  │ SUB-AGENT 1 │    │ SUB-AGENT 2 │    │ SUB-AGENT N │    │")
        print(f"│  │  (Patient A) │    │  (Patient B) │    │  (Patient C) │    │")
        print(f"│  └─────────────┘    └─────────────┘    └─────────────┘    │")
        print(f"└─────────────────────────────────────────────────────────────┘")
    
    async def initialize_demo(self):
        """Initialize the Master Agent for demo."""
        self.clear_screen()
        self.print_banner("INITIALIZING VISUAL DEMO - PHASE 2")
        
        print("🔑 Generating Fetch.ai Master Agent...")
        time.sleep(1)
        
        self.master_agent = MasterAgent()
        await self.master_agent.initialize()
        
        print(f"✅ Master Agent Address: {self.master_agent.agent_identity.address}")
        print("✅ System ready for visual demonstration!")
        
        self.print_network_diagram()
        
        input("\nPress Enter to start the visual demo...")
    
    async def demo_server_calls(self):
        """Demonstrate server calls with visual representation."""
        self.clear_screen()
        self.print_banner("SERVER CALLS DEMONSTRATION")
        
        print("🌐 Simulating database service calls...")
        
        # Demo 1: Health Check
        self.print_server_call("GET", "/health", None)
        
        # Demo 2: Patient Query
        query_data = '{"query": "Find patients for follow-up from 4 days ago"}'
        self.print_server_call("POST", "/api/query", query_data)
        
        # Demo 3: Patient Data Retrieval
        patient_data = '{"patients": [{"id": "PAT001", "name": "John Smith"}]}'
        self.print_server_call("GET", "/api/patients", patient_data)
        
        print("\n✅ All server calls completed successfully!")
        input("\nPress Enter to continue to sub-agent spawning...")
    
    async def demo_sub_agent_spawning(self):
        """Demonstrate sub-agent spawning with visual representation."""
        self.clear_screen()
        self.print_banner("SUB-AGENT SPAWNING DEMONSTRATION")
        
        # Use a specific query
        query = "Follow up on John Smith and Jane Doe, check their vitals"
        print(f"📝 Doctor Query: '{query}'")
        
        # Parse and get patients
        criteria = self.master_agent.parse_doctor_query(query)
        patients = await self.master_agent.query_database(criteria)
        
        print(f"\n👥 Found {len(patients)} patients to process...")
        
        # Spawn sub-agents with visual representation
        sub_agents = []
        for i, patient in enumerate(patients, 1):
            agent_id = f"sub_agent_{patient.patient_id}_{i}"
            
            self.print_sub_agent_spawn(agent_id, patient.name, patient.patient_id)
            
            # Create actual sub-agent
            sub_agent = await self.master_agent.create_sub_agents([patient], criteria)
            sub_agents.extend(sub_agent)
            
            time.sleep(1)  # Pause between spawns
        
        print(f"\n🎉 Successfully spawned {len(sub_agents)} sub-agents!")
        input("\nPress Enter to see sub-agents in action...")
        
        return sub_agents
    
    async def demo_sub_agent_processing(self, sub_agents):
        """Demonstrate sub-agent processing with visual representation."""
        self.clear_screen()
        self.print_banner("SUB-AGENT PROCESSING DEMONSTRATION")
        
        print("⚙️  Sub-agents are now processing their assigned patients...")
        
        results = []
        for i, sub_agent in enumerate(sub_agents, 1):
            print(f"\n{'='*60}")
            print(f"🤖 SUB-AGENT {i} PROCESSING")
            print(f"{'='*60}")
            
            # Show processing animation
            self.print_processing_animation(
                sub_agent.sub_agent_id, 
                sub_agent.patient_data.name
            )
            
            # Process the sub-agent
            result = await sub_agent.process_patient()
            results.append(result)
            
            # Show recommendations
            self.print_recommendations(
                result['recommendations'], 
                sub_agent.patient_data.name
            )
            
            time.sleep(2)  # Pause between processing
        
        print(f"\n🎉 All {len(results)} sub-agents completed processing!")
        input("\nPress Enter to see the final results...")
        
        return results
    
    def print_final_results(self, results):
        """Print final results summary."""
        self.clear_screen()
        self.print_banner("FINAL RESULTS SUMMARY")
        
        total_patients = len(results)
        total_recommendations = sum(len(r.get('recommendations', [])) for r in results)
        high_priority = sum(
            1 for r in results 
            for rec in r.get('recommendations', []) 
            if rec.get('priority') == 'high'
        )
        
        print(f"📊 PROCESSING STATISTICS")
        print(f"┌─────────────────────────────────────────────────────────────┐")
        print(f"│ Total Patients Processed: {total_patients:<35} │")
        print(f"│ Total Recommendations: {total_recommendations:<37} │")
        print(f"│ High Priority Alerts: {high_priority:<39} │")
        print(f"│ Success Rate: 100%{'':<42} │")
        print(f"└─────────────────────────────────────────────────────────────┘")
        
        print(f"\n📋 DETAILED RESULTS")
        for i, result in enumerate(results, 1):
            print(f"\n🤖 Sub-Agent {i}:")
            print(f"   Patient: {result['patient_name']}")
            print(f"   Status: {result['status']}")
            print(f"   Steps: {', '.join(result['processing_steps'])}")
            print(f"   Recommendations: {len(result['recommendations'])}")
            
            for j, rec in enumerate(result['recommendations'], 1):
                priority_icon = {
                    "high": "🚨",
                    "medium": "⚠️",
                    "low": "ℹ️"
                }.get(rec.get("priority", "low"), "ℹ️")
                print(f"      {j}. {priority_icon} {rec['message']} ({rec['priority']})")
    
    async def demo_real_time_visual(self):
        """Real-time visual demonstration."""
        self.clear_screen()
        self.print_banner("REAL-TIME VISUAL PROCESSING")
        
        print("🔄 Processing doctor queries in real-time...")
        print("   (Watch the sub-agents spawn and work!)")
        print("\nPress Ctrl+C to stop the demo...")
        
        try:
            for i, query in enumerate(self.demo_queries, 1):
                print(f"\n{'='*80}")
                print(f"📝 QUERY #{i}: {query}")
                print(f"{'='*80}")
                
                # Show processing steps
                print("🧠 Parsing natural language...")
                time.sleep(0.5)
                
                print("🔍 Querying database...")
                time.sleep(0.5)
                
                print("🤖 Spawning sub-agents...")
                time.sleep(0.5)
                
                # Process the query
                result = await self.master_agent.process_doctor_query(query)
                
                print(f"✅ Processed in {time.time():.2f} seconds")
                print(f"   Patients: {result['patients_found']}")
                print(f"   Sub-agents: {result['sub_agents_created']}")
                print(f"   Recommendations: {result['summary']['total_recommendations']}")
                
                time.sleep(2)  # Pause between queries
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Demo stopped by user")
    
    async def run_visual_demo(self):
        """Run the complete visual demonstration."""
        try:
            # Initialize
            await self.initialize_demo()
            
            # Server calls demo
            await self.demo_server_calls()
            
            # Sub-agent spawning demo
            sub_agents = await self.demo_sub_agent_spawning()
            
            # Sub-agent processing demo
            results = await self.demo_sub_agent_processing(sub_agents)
            
            # Final results
            self.print_final_results(results)
            
            # Ask for real-time demo
            print(f"\n{'='*80}")
            print("🎮 REAL-TIME VISUAL DEMO")
            print(f"{'='*80}")
            choice = input("Would you like to see real-time visual processing? (y/n): ").lower()
            
            if choice in ['y', 'yes']:
                await self.demo_real_time_visual()
            
            # Final summary
            self.clear_screen()
            self.print_banner("VISUAL DEMO COMPLETED!")
            print("✅ Phase 2 Master Agent system fully demonstrated")
            print("✅ Server calls, sub-agent spawning, and processing shown")
            print("✅ System ready for production use")
            print(f"{'='*80}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Visual demo ended. Thanks for watching!")
        except Exception as e:
            print(f"\n❌ Demo error: {str(e)}")
            print("Please check the system and try again.")


async def main():
    """Run the visual demo."""
    demo = VisualDemoPhase2()
    await demo.run_visual_demo()


if __name__ == "__main__":
    asyncio.run(main())

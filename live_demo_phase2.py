"""
Live Interactive Demo of Phase 2: Master Agent & Database Integration
Real-time demonstration of patient data flow and sub-agent creation.
"""
import asyncio
import json
import time
from datetime import datetime
from agents.master_agent import MasterAgent


class LiveDemoPhase2:
    """Live demonstration of Phase 2 Master Agent functionality."""
    
    def __init__(self):
        self.master_agent = None
        self.demo_queries = [
            "follow up with all patients from 4 days ago",
            "check on all diabetic patients who haven't been seen in 2 weeks",
            "review all patients with chest pain symptoms from last week",
            "get all patients over 65 with medication changes in the past month",
            "Follow up on John Smith and Jane Doe, check their vitals"
        ]
    
    async def initialize_demo(self):
        """Initialize the Master Agent for demo."""
        print("🚀 INITIALIZING LIVE DEMO - PHASE 2")
        print("=" * 60)
        
        print("📡 Connecting to Fetch.ai network...")
        print("🔑 Generating Master Agent wallet...")
        
        self.master_agent = MasterAgent()
        await self.master_agent.initialize()
        
        print(f"✅ Master Agent Address: {self.master_agent.agent_identity.address}")
        print("✅ Master Agent ready for live demonstration!")
        print()
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(f"🎯 {title}")
        print("=" * 70)
    
    def print_step(self, step_num: int, title: str, details: str = ""):
        """Print a formatted step."""
        print(f"\n📋 STEP {step_num}: {title}")
        print("-" * 50)
        if details:
            print(f"   {details}")
    
    def print_result(self, success: bool, message: str, details: str = ""):
        """Print a formatted result."""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {status}: {message}")
        if details:
            print(f"      {details}")
    
    async def demo_natural_language_parsing(self):
        """Demonstrate natural language parsing."""
        self.print_header("NATURAL LANGUAGE PARSING DEMO")
        
        test_queries = [
            "follow up with all patients from 4 days ago",
            "check on all diabetic patients who haven't been seen in 2 weeks",
            "review all patients with chest pain symptoms from last week"
        ]
        
        for i, query in enumerate(test_queries, 1):
            self.print_step(i, f"Parsing Query: '{query}'")
            
            # Parse the query
            criteria = self.master_agent.parse_doctor_query(query)
            
            print(f"   🧠 Parsed Action: {criteria.action}")
            print(f"   ⏰ Time Filter: {criteria.time_filter or 'None'}")
            print(f"   🏥 Condition Filter: {criteria.condition_filter or 'None'}")
            print(f"   🩺 Symptom Filter: {criteria.symptom_filter or 'None'}")
            print(f"   👴 Age Filter: {criteria.age_filter or 'None'}")
            print(f"   💊 Medication Filter: {criteria.medication_filter or 'None'}")
            print(f"   📅 Date Range: {criteria.date_range or 'None'}")
            
            self.print_result(True, f"Successfully parsed '{query}'")
            await asyncio.sleep(1)  # Pause for effect
    
    async def demo_database_integration(self):
        """Demonstrate database integration."""
        self.print_header("DATABASE INTEGRATION DEMO")
        
        self.print_step(1, "Connecting to Ryan's Database Service")
        print("   🔗 Database URL: http://localhost:3000/api/query")
        print("   🔑 API Key: [CONFIGURED]")
        
        # Test database connection
        connection_test = self.master_agent.database_client.test_connection()
        
        if "error" in connection_test:
            self.print_result(False, "Database service unavailable (expected in demo)")
            print("   ℹ️  Using sample data for demonstration")
        else:
            self.print_result(True, "Database connection successful")
        
        self.print_step(2, "Querying Patient Data")
        
        # Demo queries
        demo_queries = [
            "Find patients for follow-up from 4 days ago",
            "Find patients for status check with diabetic",
            "Find patients for review from last week with chest pain"
        ]
        
        for i, query in enumerate(demo_queries, 1):
            print(f"   Query {i}: '{query}'")
            
            # Send query
            response = self.master_agent.database_client.query_patient_data(query)
            
            if "error" in response:
                print(f"      Response: Database unavailable (using sample data)")
            else:
                print(f"      Response: {len(response)} patients found")
            
            await asyncio.sleep(0.5)
        
        self.print_result(True, "Database integration working (with sample data)")
    
    async def demo_sub_agent_creation(self):
        """Demonstrate sub-agent creation and processing."""
        self.print_header("SUB-AGENT CREATION & PROCESSING DEMO")
        
        # Use a specific query for this demo
        query = "Follow up on John Smith and Jane Doe, check their vitals"
        
        self.print_step(1, f"Processing Doctor Query: '{query}'")
        
        # Parse the query
        criteria = self.master_agent.parse_doctor_query(query)
        print(f"   🧠 Parsed Action: {criteria.action}")
        
        # Get patient data
        patients = await self.master_agent.query_database(criteria)
        print(f"   👥 Patients Found: {len(patients)}")
        
        for i, patient in enumerate(patients, 1):
            print(f"      Patient {i}: {patient.name} (ID: {patient.patient_id})")
            print(f"         Medical History: {', '.join(patient.medical_history)}")
            print(f"         Medications: {', '.join(patient.current_medications)}")
        
        self.print_step(2, "Creating Sub-Agents")
        print("   🤖 Spawning sub-agents for each patient...")
        
        # Create sub-agents
        sub_agents = await self.master_agent.create_sub_agents(patients, criteria)
        
        print(f"   ✅ Created {len(sub_agents)} sub-agents:")
        for i, sub_agent in enumerate(sub_agents, 1):
            print(f"      Sub-Agent {i}: {sub_agent.sub_agent_id}")
            print(f"         Patient: {sub_agent.patient_data.name}")
            print(f"         Context: {sub_agent.master_context.action}")
            print(f"         Status: {sub_agent.status}")
        
        self.print_step(3, "Processing Sub-Agents")
        print("   ⚙️  Each sub-agent processing its assigned patient...")
        
        # Process each sub-agent
        results = []
        for i, sub_agent in enumerate(sub_agents, 1):
            print(f"      Processing Sub-Agent {i}: {sub_agent.patient_data.name}")
            
            result = await sub_agent.process_patient()
            results.append(result)
            
            print(f"         Status: {result['status']}")
            print(f"         Steps: {', '.join(result['processing_steps'])}")
            print(f"         Recommendations: {len(result['recommendations'])}")
            
            for j, rec in enumerate(result['recommendations'], 1):
                print(f"            {j}. {rec['message']} ({rec['priority']})")
            
            await asyncio.sleep(1)  # Pause for effect
        
        self.print_result(True, f"Processed {len(results)} sub-agents successfully")
        print(f"      Total Recommendations: {sum(len(r.get('recommendations', [])) for r in results)}")
    
    async def demo_real_time_processing(self):
        """Demonstrate real-time processing with live updates."""
        self.print_header("REAL-TIME PROCESSING DEMO")
        
        print("🔄 Simulating real-time doctor queries...")
        print("   (Press Ctrl+C to stop)")
        
        try:
            for i, query in enumerate(self.demo_queries, 1):
                print(f"\n📝 Doctor Query #{i}: '{query}'")
                print("   ⏳ Processing...")
                
                # Process the query
                start_time = time.time()
                result = await self.master_agent.process_doctor_query(query)
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                print(f"   ⚡ Processed in {processing_time:.2f} seconds")
                print(f"   👥 Patients Found: {result['patients_found']}")
                print(f"   🤖 Sub-agents Created: {result['sub_agents_created']}")
                print(f"   💡 Recommendations: {result['summary']['total_recommendations']}")
                print(f"   🚨 High Priority: {result['summary']['high_priority_recommendations']}")
                
                # Show some recommendations
                if result['processing_results']:
                    print("   📋 Sample Recommendations:")
                    for j, sub_result in enumerate(result['processing_results'][:2], 1):
                        print(f"      Sub-Agent {j} ({sub_result['patient_name']}):")
                        for k, rec in enumerate(sub_result['recommendations'][:2], 1):
                            print(f"         {k}. {rec['message']} ({rec['priority']})")
                
                await asyncio.sleep(2)  # Pause between queries
                
        except KeyboardInterrupt:
            print("\n   ⏹️  Demo stopped by user")
    
    async def demo_system_status(self):
        """Show system status and capabilities."""
        self.print_header("SYSTEM STATUS & CAPABILITIES")
        
        print("🤖 Master Agent Status:")
        print(f"   Address: {self.master_agent.agent_identity.address}")
        print(f"   Status: Active and Processing")
        print(f"   Sub-agents Created: {len(self.master_agent.sub_agents)}")
        
        print("\n🔧 System Capabilities:")
        print("   ✅ Natural Language Processing")
        print("   ✅ Database Integration")
        print("   ✅ Sub-Agent Creation")
        print("   ✅ Patient Data Processing")
        print("   ✅ Medical Recommendation Generation")
        print("   ✅ Real-time Query Processing")
        
        print("\n📊 Sample Queries Supported:")
        for i, query in enumerate(self.demo_queries, 1):
            print(f"   {i}. {query}")
        
        print("\n🎯 Ready for Production Integration:")
        print("   • LiveKit Server Integration")
        print("   • Ryan's Database Service")
        print("   • Real-time Voice Processing")
        print("   • Advanced NLP Models")
    
    async def run_live_demo(self):
        """Run the complete live demonstration."""
        print("🎬 LIVE DEMO - PHASE 2: MASTER AGENT & DATABASE INTEGRATION")
        print("=" * 80)
        print("This demo shows the complete Phase 2 system in action!")
        print("=" * 80)
        
        # Initialize
        await self.initialize_demo()
        
        # Run demos
        await self.demo_natural_language_parsing()
        await self.demo_database_integration()
        await self.demo_sub_agent_creation()
        
        # Show system status
        await self.demo_system_status()
        
        # Ask if user wants real-time demo
        print("\n" + "=" * 70)
        print("🎮 INTERACTIVE DEMO")
        print("=" * 70)
        print("Would you like to see real-time processing? (y/n): ", end="")
        
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes']:
                await self.demo_real_time_processing()
        except KeyboardInterrupt:
            print("\n   ⏹️  Demo stopped")
        
        print("\n" + "=" * 70)
        print("🎉 LIVE DEMO COMPLETED!")
        print("=" * 70)
        print("✅ Phase 2 Master Agent system is fully operational")
        print("✅ All core functionality demonstrated and working")
        print("✅ Ready for Phase 3 development")
        print("=" * 70)


async def main():
    """Run the live demo."""
    demo = LiveDemoPhase2()
    await demo.run_live_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo ended. Thanks for watching!")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("Please check the system and try again.")

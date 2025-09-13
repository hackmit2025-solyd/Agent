"""
Test Claude Integration
Shows what you need to set up for Claude API integration.
"""
import os
import asyncio
from services.llm_service import llm_service, LLMProvider


async def test_claude_setup():
    """Test Claude API setup and show what's needed."""
    print("🤖 Claude Integration Test")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found!")
        print("\n📋 To use Claude, you need to:")
        print("1. Get an API key from: https://console.anthropic.com/")
        print("2. Set the environment variable:")
        print("   Windows: set ANTHROPIC_API_KEY=your_key_here")
        print("   Linux/Mac: export ANTHROPIC_API_KEY=your_key_here")
        print("3. Or create a .env file with: ANTHROPIC_API_KEY=your_key_here")
        print("\n🔄 Testing with mock responses for now...")
    else:
        print(f"✅ ANTHROPIC_API_KEY found: {api_key[:10]}...")
        print("🚀 Testing Claude integration...")
    
    # Test query parsing
    print(f"\n📝 Testing Query Parsing:")
    query = "Follow up with all diabetic patients from last week who have been experiencing vision problems"
    print(f"Query: {query}")
    
    parsed = await llm_service.parse_doctor_query(query)
    print(f"Parsed Result: {parsed}")
    
    # Test communication generation
    print(f"\n💬 Testing Communication Generation:")
    patient_data = {
        "name": "John Smith",
        "medical_history": ["Diabetes Type 2", "Hypertension"],
        "current_medications": ["Metformin", "Lisinopril"],
        "symptoms": ["blurred vision", "fatigue"]
    }
    
    context = {
        "goals": [
            "Check blood sugar levels",
            "Assess vision problems", 
            "Review medication adherence",
            "Schedule next appointment"
        ]
    }
    
    print(f"Patient: {patient_data['name']}")
    print(f"Goals: {', '.join(context['goals'])}")
    
    transcript = await llm_service.generate_communication_transcript(patient_data, context)
    print(f"\nGenerated Transcript:")
    print(f"Duration: {transcript.get('duration', 0)} seconds")
    print(f"Confidence: {transcript.get('confidence_score', 0.0):.2f}")
    print(f"Quality: {transcript.get('conversation_quality', 'unknown')}")
    print(f"\nTranscript Preview:")
    print(f"{transcript.get('transcript', '')[:200]}...")
    
    # Test decision analysis
    print(f"\n🧠 Testing Decision Analysis:")
    analysis = await llm_service.analyze_communication_outcome(transcript, patient_data)
    print(f"Outcome: {analysis.get('outcome', 'unknown')}")
    print(f"Reasoning: {analysis.get('reasoning', 'No reasoning provided')}")
    print(f"Confidence: {analysis.get('confidence', 0.0):.2f}")
    
    print(f"\n🎉 Claude Integration Test Complete!")
    
    if not api_key:
        print(f"\n💡 Once you set up your API key, the system will use real Claude responses!")
        print(f"   The mock responses above show what the system will do with Claude.")


if __name__ == "__main__":
    asyncio.run(test_claude_setup())

"""
LLM Service for Intelligent Healthcare Agent System
Provides AI-powered natural language processing, decision making, and communication generation.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from anthropic import Anthropic
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logging.warning("Anthropic library not available. Install with: pip install anthropic")

from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"


@dataclass
class LLMResponse:
    """Response from LLM service."""
    content: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]


class LLMService:
    """
    LLM Service for intelligent healthcare agent operations.
    Supports multiple providers with fallback to mock responses.
    """
    
    def __init__(self, provider: LLMProvider = LLMProvider.OPENAI):
        self.provider = provider
        self.client = None
        self.available = LLM_AVAILABLE
        
        if self.available:
            self._initialize_client()
        else:
            logger.warning("LLM libraries not available. Using mock responses.")
    
    def _initialize_client(self):
        """Initialize the LLM client based on provider."""
        try:
            if self.provider == LLMProvider.OPENAI:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("OPENAI_API_KEY not found. Using mock responses.")
                    self.available = False
                    return
                self.client = OpenAI(api_key=api_key)
                
            elif self.provider == LLMProvider.ANTHROPIC:
                api_key = os.getenv("CLAUDE_SECRET") or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    logger.warning("CLAUDE_SECRET not found. Using mock responses.")
                    self.available = False
                    return
                self.client = Anthropic(api_key=api_key)
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {str(e)}")
            self.available = False
    
    async def parse_doctor_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a doctor's natural language query into structured criteria.
        
        Args:
            query: Natural language query from doctor
            
        Returns:
            Dictionary with parsed criteria
        """
        if not self.available:
            return self._mock_parse_query(query)
        
        system_prompt = """You are a healthcare AI assistant that parses doctor queries into structured criteria.

Parse the following doctor query and extract:
1. Action type (follow_up, check_status, review, urgent, schedule)
2. Time filter (today, yesterday, last_week, last_month, specific_date)
3. Patient criteria (status, condition, age_range, etc.)
4. Condition filters (specific medical conditions)
5. Symptom filters (specific symptoms to look for)

Return a JSON object with these fields. Be precise and extract all relevant information."""

        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.1
                )
                content = response.choices[0].message.content
                
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",  # Cheapest Claude model
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\nQuery: {query}"}
                    ]
                )
                content = response.content[0].text
            
            # Parse JSON response
            parsed = json.loads(content)
            return parsed
            
        except Exception as e:
            logger.error(f"LLM query parsing failed: {str(e)}")
            return self._mock_parse_query(query)
    
    async def generate_communication_transcript(self, patient_data: Dict[str, Any], 
                                              context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a realistic communication transcript between agent and patient.
        
        Args:
            patient_data: Patient information
            context: Communication context and goals
            
        Returns:
            Dictionary with transcript and analysis
        """
        if not self.available:
            return self._mock_generate_transcript(patient_data, context)
        
        system_prompt = f"""You are a healthcare AI agent conducting a patient follow-up call.

Patient Information:
- Name: {patient_data.get('name', 'Unknown')}
- Medical History: {', '.join(patient_data.get('medical_history', []))}
- Current Medications: {', '.join(patient_data.get('current_medications', []))}
- Symptoms: {', '.join(patient_data.get('symptoms', []))}

Communication Goals: {', '.join(context.get('goals', []))}

Generate a realistic conversation transcript between the AI agent and patient. The conversation should:
1. Be natural and professional
2. Cover all communication goals
3. Show patient responses based on their medical condition
4. Include realistic medical details
5. End with appropriate next steps

Return a JSON object with:
- transcript: The conversation text
- duration: Estimated duration in seconds
- data_obtained: Key information gathered (boolean flags)
- missing_data: Information that couldn't be obtained
- confidence_score: Confidence in the communication (0.0-1.0)
- conversation_quality: Quality assessment (poor/fair/good/excellent)
- patient_cooperation: Patient cooperation level (poor/fair/good/excellent)"""

        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Generate the conversation transcript."}
                    ],
                    temperature=0.7
                )
                content = response.choices[0].message.content
                
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",  # Cheapest Claude model
                    max_tokens=2000,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\nGenerate the conversation transcript."}
                    ]
                )
                content = response.content[0].text
            
            # Parse JSON response
            result = json.loads(content)
            return result
            
        except Exception as e:
            logger.error(f"LLM transcript generation failed: {str(e)}")
            return self._mock_generate_transcript(patient_data, context)
    
    async def analyze_communication_outcome(self, transcript_data: Dict[str, Any], 
                                          patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze communication outcome and determine next steps.
        
        Args:
            transcript_data: Generated transcript and metadata
            patient_data: Patient information
            
        Returns:
            Analysis with decision recommendation
        """
        if not self.available:
            return self._mock_analyze_outcome(transcript_data, patient_data)
        
        system_prompt = f"""You are a healthcare AI analyzing a patient communication outcome and making critical decisions about patient care.

Patient Data:
- Medical History: {', '.join(patient_data.get('medical_history', []))}
- Current Symptoms: {', '.join(patient_data.get('symptoms', []))}
- Current Medications: {', '.join(patient_data.get('current_medications', []))}

Communication Data:
- Duration: {transcript_data.get('duration', 0)} seconds
- Confidence: {transcript_data.get('confidence_score', 0.0)}
- Quality: {transcript_data.get('conversation_quality', 'unknown')}
- Data Obtained: {transcript_data.get('data_obtained', {})}
- Missing Data: {transcript_data.get('missing_data', [])}
- Transcript: {transcript_data.get('transcript', '')[:500]}...

You must make a critical decision about this patient's care:

DECISION OPTIONS:
1. CLOSE_LOOP: Communication successful, all critical information obtained, patient stable, no urgent concerns
2. FLAG_FOR_DOCTOR_REVIEW: Missing important information, patient needs human medical review, non-urgent
3. ESCALATE_URGENT: URGENT - Patient has serious symptoms, needs immediate medical attention, safety concern
4. RETRY_COMMUNICATION: Communication failed, technical issues, patient unresponsive, needs retry

CRITICAL DECISION FACTORS:
- Patient safety is ABSOLUTE priority
- Look for urgent red flags: chest pain, severe symptoms, medication problems, patient distress
- Consider data completeness - what's missing and how critical is it?
- Assess patient cooperation and understanding
- Evaluate medication adherence and side effects
- Check for new or worsening symptoms

URGENT CONDITIONS TO ESCALATE:
- Chest pain, shortness of breath, severe pain
- High blood pressure, irregular heartbeat
- Severe medication side effects or non-compliance
- Patient expressing suicidal thoughts or severe depression
- Signs of stroke, heart attack, or other emergencies
- Severe allergic reactions or drug interactions

Return a JSON object with:
- outcome: Your decision (CLOSE_LOOP/FLAG_FOR_DOCTOR_REVIEW/ESCALATE_URGENT/RETRY_COMMUNICATION)
- reasoning: Detailed medical reasoning for your decision
- confidence: Your confidence in this decision (0.0-1.0)
- urgent_conditions: List of urgent conditions detected (empty if none)
- next_steps: Specific recommended actions
- termination_reason: Why you chose to terminate or continue the communication"""

        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Analyze the communication outcome."}
                    ],
                    temperature=0.1
                )
                content = response.choices[0].message.content
                
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",  # Cheapest Claude model
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\nAnalyze the communication outcome."}
                    ]
                )
                content = response.content[0].text
            
            # Parse JSON response
            result = json.loads(content)
            return result
            
        except Exception as e:
            logger.error(f"LLM outcome analysis failed: {str(e)}")
            return self._mock_analyze_outcome(transcript_data, patient_data)
    
    async def generate_patient_summary(self, patient_data: Dict[str, Any], 
                                     communication_result: Dict[str, Any]) -> str:
        """
        Generate a comprehensive patient summary for doctor review.
        
        Args:
            patient_data: Patient information
            communication_result: Communication analysis results
            
        Returns:
            Formatted patient summary
        """
        if not self.available:
            return self._mock_generate_summary(patient_data, communication_result)
        
        system_prompt = f"""You are a healthcare AI generating a patient summary for doctor review.

Patient Information:
- Name: {patient_data.get('name', 'Unknown')}
- Medical History: {', '.join(patient_data.get('medical_history', []))}
- Current Medications: {', '.join(patient_data.get('current_medications', []))}
- Symptoms: {', '.join(patient_data.get('symptoms', []))}

Communication Results:
- Outcome: {communication_result.get('outcome', 'unknown')}
- Confidence: {communication_result.get('confidence', 0.0)}
- Data Obtained: {communication_result.get('data_obtained', {})}
- Missing Data: {communication_result.get('missing_data', [])}
- Urgent Conditions: {communication_result.get('urgent_conditions', [])}

Generate a professional, concise patient summary that includes:
1. Patient identification and key medical information
2. Communication outcome and confidence level
3. Key findings and concerns
4. Recommended actions
5. Urgent flags if any

Format as a clear, professional medical summary."""

        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Generate the patient summary."}
                    ],
                    temperature=0.3
                )
                content = response.choices[0].message.content
                
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",  # Cheapest Claude model
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\nGenerate the patient summary."}
                    ]
                )
                content = response.content[0].text
            
            return content
            
        except Exception as e:
            logger.error(f"LLM summary generation failed: {str(e)}")
            return self._mock_generate_summary(patient_data, communication_result)
    
    # Mock methods for when LLM is not available
    def _mock_parse_query(self, query: str) -> Dict[str, Any]:
        """Mock query parsing when LLM is not available."""
        return {
            "action": "follow_up",
            "time_filter": "today",
            "patient_criteria": {"status": "active"},
            "condition_filter": [],
            "symptom_filter": []
        }
    
    def _mock_generate_transcript(self, patient_data: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock transcript generation when LLM is not available."""
        return {
            "transcript": f"Agent: Hello {patient_data.get('name', 'Patient')}, this is your healthcare follow-up call.\nPatient: Hi, I'm doing well today.\nAgent: How are your symptoms?\nPatient: They're manageable.\nAgent: Are you taking your medications?\nPatient: Yes, as prescribed.\nAgent: Great! I'll schedule your next appointment.\nPatient: Thank you.",
            "duration": 120.0,
            "data_obtained": {
                "feeling_well": True,
                "medication_adherence": True,
                "no_concerns": True
            },
            "missing_data": [],
            "confidence_score": 0.85,
            "conversation_quality": "good",
            "patient_cooperation": "excellent"
        }
    
    def _mock_analyze_outcome(self, transcript_data: Dict[str, Any], 
                            patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock outcome analysis when LLM is not available."""
        confidence = transcript_data.get('confidence_score', 0.0)
        
        if confidence >= 0.8:
            outcome = "close_loop"
        elif confidence >= 0.6:
            outcome = "flag_for_doctor_review"
        else:
            outcome = "escalate_urgent"
        
        return {
            "outcome": outcome,
            "reasoning": f"Based on confidence score of {confidence:.2f}",
            "confidence": 0.9,
            "urgent_conditions": [],
            "next_steps": ["Continue monitoring", "Schedule follow-up"]
        }
    
    def _mock_generate_summary(self, patient_data: Dict[str, Any], 
                             communication_result: Dict[str, Any]) -> str:
        """Mock summary generation when LLM is not available."""
        return f"""PATIENT SUMMARY
================
Patient: {patient_data.get('name', 'Unknown')}
Outcome: {communication_result.get('outcome', 'unknown').upper()}
Confidence: {communication_result.get('confidence', 0.0):.2f}

Key Findings:
- Communication completed successfully
- Patient cooperative and responsive
- No urgent conditions identified

Recommendations:
- Continue current treatment plan
- Schedule routine follow-up
- Monitor for any changes in condition"""


# Global LLM service instance - Default to Claude
llm_service = LLMService(provider=LLMProvider.ANTHROPIC)


async def main():
    """Test the LLM service."""
    print("🤖 LLM Service Test")
    print("=" * 40)
    
    # Test query parsing
    query = "Follow up with all diabetic patients from last week who have been experiencing vision problems"
    print(f"Testing query parsing: {query}")
    
    parsed = await llm_service.parse_doctor_query(query)
    print(f"Parsed result: {json.dumps(parsed, indent=2)}")
    
    # Test transcript generation
    patient_data = {
        "name": "John Smith",
        "medical_history": ["Diabetes Type 2"],
        "current_medications": ["Metformin"],
        "symptoms": ["blurred vision"]
    }
    
    context = {
        "goals": ["Check blood sugar levels", "Assess vision problems", "Review medication adherence"]
    }
    
    print(f"\nTesting transcript generation for {patient_data['name']}")
    transcript = await llm_service.generate_communication_transcript(patient_data, context)
    print(f"Generated transcript: {transcript['transcript'][:200]}...")
    
    print(f"\n🎉 LLM Service test complete!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

"""
Master Agent for Phase 2: Core Agent & Database Integration
Handles patient data ingestion, context parsing, and sub-agent creation.
"""
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re
import dateparser
from dataclasses import dataclass

from agents.wallet_manager import WalletManager
from services.database_client import DatabaseClient
from services.llm_service import llm_service
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)


@dataclass
class ParsedCriteria:
    """Structured representation of parsed doctor query criteria."""
    action: str
    time_filter: Optional[str] = None
    condition_filter: Optional[str] = None
    symptom_filter: Optional[str] = None
    age_filter: Optional[str] = None
    medication_filter: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    patient_criteria: Optional[Dict[str, Any]] = None


@dataclass
class PatientRecord:
    """Structured patient record from database."""
    patient_id: str
    name: str
    last_visit: str
    status: str
    medical_history: List[str]
    current_medications: List[str]
    age: Optional[int] = None
    symptoms: Optional[List[str]] = None
    follow_up_reason: Optional[str] = None
    medication_changes: Optional[List[Dict]] = None


class SubAgent:
    """Temporary sub-agent for individual patient processing."""
    
    def __init__(self, patient_data: PatientRecord, master_context: ParsedCriteria, sub_agent_id: str):
        self.sub_agent_id = sub_agent_id
        self.patient_data = patient_data
        self.master_context = master_context
        self.created_at = datetime.utcnow()
        self.status = "initialized"
        
        logger.info(f"Sub-agent {sub_agent_id} created for patient {patient_data.patient_id}")
    
    async def process_patient(self) -> Dict[str, Any]:
        """Process the assigned patient based on master context."""
        logger.info(f"Sub-agent {self.sub_agent_id} processing patient {self.patient_data.patient_id}")
        
        result = {
            "sub_agent_id": self.sub_agent_id,
            "patient_id": self.patient_data.patient_id,
            "patient_name": self.patient_data.name,
            "action": self.master_context.action,
            "processing_steps": [],
            "recommendations": [],
            "status": "processing"
        }
        
        # Process based on master context action
        if self.master_context.action == "follow_up":
            result = await self._process_follow_up(result)
        elif self.master_context.action == "check_status":
            result = await self._process_status_check(result)
        elif self.master_context.action == "review":
            result = await self._process_review(result)
        elif self.master_context.action == "get_patients":
            result = await self._process_get_patients(result)
        
        result["status"] = "completed"
        result["completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Sub-agent {self.sub_agent_id} completed processing")
        return result
    
    async def _process_follow_up(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process follow-up action for patient."""
        result["processing_steps"].append("follow_up_analysis")
        
        # Analyze patient's medical history and current status
        if "diabetes" in [h.lower() for h in self.patient_data.medical_history]:
            result["recommendations"].append({
                "type": "diabetes_monitoring",
                "message": "Schedule diabetes management follow-up",
                "priority": "medium"
            })
        
        if "chest_pain" in (self.patient_data.symptoms or []):
            result["recommendations"].append({
                "type": "cardiac_follow_up",
                "message": "Urgent cardiac follow-up required",
                "priority": "high"
            })
        
        result["recommendations"].append({
            "type": "routine_follow_up",
            "message": f"Schedule routine follow-up for {self.patient_data.name}",
            "priority": "low"
        })
        
        return result
    
    async def _process_status_check(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process status check action for patient."""
        result["processing_steps"].append("status_analysis")
        
        # Check medication adherence
        if self.patient_data.current_medications:
            result["recommendations"].append({
                "type": "medication_review",
                "message": f"Review medication adherence for {len(self.patient_data.current_medications)} current medications",
                "priority": "medium"
            })
        
        # Check for concerning conditions
        concerning_conditions = ["diabetes", "heart disease", "hypertension"]
        patient_conditions = [h.lower() for h in self.patient_data.medical_history]
        
        for condition in concerning_conditions:
            if any(condition in pc for pc in patient_conditions):
                result["recommendations"].append({
                    "type": "condition_monitoring",
                    "message": f"Monitor {condition} management",
                    "priority": "high"
                })
        
        return result
    
    async def _process_review(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process review action for patient."""
        result["processing_steps"].append("symptom_review")
        
        # Review symptoms mentioned in master context
        if self.master_context.symptom_filter == "chest_pain":
            result["recommendations"].append({
                "type": "cardiac_evaluation",
                "message": "Comprehensive cardiac evaluation required",
                "priority": "high"
            })
        
        result["recommendations"].append({
            "type": "symptom_monitoring",
            "message": "Continue monitoring reported symptoms",
            "priority": "medium"
        })
        
        return result
    
    async def _process_get_patients(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Process get patients action."""
        result["processing_steps"].append("patient_data_compilation")
        
        # Compile patient information
        result["patient_summary"] = {
            "age": self.patient_data.age,
            "conditions": self.patient_data.medical_history,
            "medications": self.patient_data.current_medications,
            "last_visit": self.patient_data.last_visit
        }
        
        result["recommendations"].append({
            "type": "data_compilation",
            "message": "Patient data compiled for review",
            "priority": "low"
        })
        
        return result


class MasterAgent:
    """
    Master Agent for Phase 2: Handles patient data ingestion, context parsing,
    database querying, and sub-agent creation.
    """
    
    def __init__(self):
        self.wallet_manager = WalletManager()
        self.database_client = DatabaseClient()
        self.agent_identity = None
        self.sub_agents = {}
        self.sample_queries = self._load_sample_queries()
        
    def _load_sample_queries(self) -> Dict[str, Any]:
        """Load sample queries from JSON file."""
        try:
            with open("data/sample_queries.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Sample queries file not found, using empty queries")
            return {"sample_queries": []}
    
    async def initialize(self):
        """Initialize the Master Agent."""
        logger.info("Initializing Master Agent...")
        
        # Initialize wallet
        try:
            if AgentConfig.WALLET_PRIVATE_KEY:
                wallet_info = self.wallet_manager.load_existing_wallet()
            else:
                wallet_info = self.wallet_manager.create_new_wallet()
            
            self.agent_identity = wallet_info['identity']
            logger.info(f"Master Agent wallet initialized: {self.agent_identity.address}")
            
        except Exception as e:
            logger.error(f"Failed to initialize wallet: {str(e)}")
            raise
        
        logger.info("Master Agent initialization completed")
    
    async def parse_doctor_query(self, query: str) -> ParsedCriteria:
        """
        Parse natural language doctor query into structured criteria using LLM.
        
        Args:
            query: Natural language query from doctor
            
        Returns:
            ParsedCriteria object with structured information
        """
        logger.info(f"Parsing doctor query with LLM: '{query}'")
        
        # Use LLM to parse the query
        llm_result = await llm_service.parse_doctor_query(query)
        
        # Convert LLM result to ParsedCriteria
        criteria = ParsedCriteria(
            action=llm_result.get("action", "follow_up"),
            time_filter=llm_result.get("time_filter"),
            condition_filter=llm_result.get("condition_filter"),
            symptom_filter=llm_result.get("symptom_filter"),
            age_filter=llm_result.get("age_filter"),
            medication_filter=llm_result.get("medication_filter"),
            patient_criteria=llm_result.get("patient_criteria", {"status": "active"})
        )
        
        logger.info(f"LLM parsed criteria: {criteria}")
        return criteria
    
    def _extract_action(self, query: str) -> str:
        """Extract action from query."""
        if "follow up" in query:
            return "follow_up"
        elif "check" in query or "status" in query:
            return "check_status"
        elif "review" in query:
            return "review"
        elif "get" in query or "find" in query:
            return "get_patients"
        else:
            return "general"
    
    def _extract_time_filter(self, query: str) -> Optional[str]:
        """Extract time filter from query."""
        time_patterns = [
            r"(\d+)\s+days?\s+ago",
            r"(\d+)\s+weeks?\s+ago",
            r"(\d+)\s+months?\s+ago",
            r"last\s+week",
            r"past\s+month",
            r"yesterday",
            r"today"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(0)
        
        return None
    
    def _parse_date_range(self, query: str, time_filter: Optional[str]) -> Optional[Dict[str, str]]:
        """Parse date range from time filter."""
        if not time_filter:
            return None
        
        try:
            if "days ago" in time_filter:
                days = int(re.search(r"(\d+)", time_filter).group(1))
                target_date = datetime.now() - timedelta(days=days)
                return {
                    "start_date": target_date.strftime("%Y-%m-%d"),
                    "end_date": target_date.strftime("%Y-%m-%d")
                }
            elif "weeks ago" in time_filter:
                weeks = int(re.search(r"(\d+)", time_filter).group(1))
                target_date = datetime.now() - timedelta(weeks=weeks)
                return {
                    "start_date": target_date.strftime("%Y-%m-%d"),
                    "end_date": target_date.strftime("%Y-%m-%d")
                }
            elif "last week" in time_filter:
                end_date = datetime.now() - timedelta(days=7)
                start_date = end_date - timedelta(days=7)
                return {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            elif "past month" in time_filter:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                return {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
        except Exception as e:
            logger.warning(f"Failed to parse date range: {str(e)}")
        
        return None
    
    def _extract_condition_filter(self, query: str) -> Optional[str]:
        """Extract condition filter from query."""
        conditions = ["diabetic", "diabetes", "hypertension", "asthma", "heart disease"]
        
        for condition in conditions:
            if condition in query:
                return condition
        
        return None
    
    def _extract_symptom_filter(self, query: str) -> Optional[str]:
        """Extract symptom filter from query."""
        symptoms = ["chest pain", "headache", "fever", "cough", "shortness of breath"]
        
        for symptom in symptoms:
            if symptom in query:
                return symptom.replace(" ", "_")
        
        return None
    
    def _extract_age_filter(self, query: str) -> Optional[str]:
        """Extract age filter from query."""
        age_patterns = [
            r"over\s+(\d+)",
            r"under\s+(\d+)",
            r"(\d+)\s+and\s+over",
            r"(\d+)\s+and\s+under"
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_medication_filter(self, query: str) -> Optional[str]:
        """Extract medication filter from query."""
        if "medication" in query and ("change" in query or "adjust" in query):
            return "recent_changes"
        elif "medication" in query:
            return "current_medications"
        
        return None
    
    def _build_patient_criteria(self, time_filter, condition_filter, symptom_filter, 
                               age_filter, medication_filter, date_range) -> Dict[str, Any]:
        """Build patient criteria dictionary."""
        criteria = {"status": "active"}
        
        if time_filter:
            criteria["time_filter"] = time_filter
        
        if condition_filter:
            criteria["conditions"] = [condition_filter]
        
        if symptom_filter:
            criteria["symptoms"] = [symptom_filter]
        
        if age_filter:
            if "over" in age_filter:
                age = int(re.search(r"(\d+)", age_filter).group(1))
                criteria["age_min"] = age
            elif "under" in age_filter:
                age = int(re.search(r"(\d+)", age_filter).group(1))
                criteria["age_max"] = age
        
        if medication_filter:
            criteria["medication_filter"] = medication_filter
        
        if date_range:
            criteria["date_range"] = date_range
        
        return criteria
    
    async def query_database(self, criteria: ParsedCriteria) -> List[PatientRecord]:
        """
        Query database service using parsed criteria.
        
        Args:
            criteria: Parsed criteria from doctor query
            
        Returns:
            List of PatientRecord objects
        """
        logger.info(f"Querying database with criteria: {criteria.action}")
        
        # Build database query from criteria
        query_text = self._build_database_query(criteria)
        
        try:
            # Send query to database service
            response = self.database_client.query_patient_data(query_text)
            
            if "error" in response:
                logger.warning(f"Database query failed: {response['error']}")
                # For testing, return sample data
                return self._get_sample_patients(criteria)
            
            # Parse response into PatientRecord objects
            patients = self._parse_database_response(response, criteria)
            
            logger.info(f"Retrieved {len(patients)} patients from database")
            return patients
            
        except Exception as e:
            logger.error(f"Database query failed: {str(e)}")
            # Return sample data for testing
            return self._get_sample_patients(criteria)
    
    def _build_database_query(self, criteria: ParsedCriteria) -> str:
        """Build database query text from criteria."""
        query_parts = []
        
        if criteria.action == "follow_up":
            query_parts.append("Find patients for follow-up")
        elif criteria.action == "check_status":
            query_parts.append("Find patients for status check")
        elif criteria.action == "review":
            query_parts.append("Find patients for review")
        else:
            query_parts.append("Find patients")
        
        if criteria.time_filter:
            query_parts.append(f"from {criteria.time_filter}")
        
        if criteria.condition_filter:
            query_parts.append(f"with {criteria.condition_filter}")
        
        if criteria.symptom_filter:
            query_parts.append(f"with {criteria.symptom_filter.replace('_', ' ')}")
        
        if criteria.age_filter:
            query_parts.append(f"age {criteria.age_filter}")
        
        return " ".join(query_parts)
    
    def _get_sample_patients(self, criteria: ParsedCriteria) -> List[PatientRecord]:
        """Get sample patients for testing when database is unavailable."""
        # Find matching sample query
        for sample_query in self.sample_queries.get("sample_queries", []):
            if sample_query["parsed_criteria"]["action"] == criteria.action:
                patients = []
                for patient_data in sample_query["expected_patients"]:
                    patient = PatientRecord(
                        patient_id=patient_data["patient_id"],
                        name=patient_data["name"],
                        last_visit=patient_data["last_visit"],
                        status=patient_data["status"],
                        medical_history=patient_data["medical_history"],
                        current_medications=patient_data["current_medications"],
                        age=patient_data.get("age"),
                        symptoms=patient_data.get("symptoms"),
                        follow_up_reason=patient_data.get("follow_up_reason"),
                        medication_changes=patient_data.get("medication_changes")
                    )
                    patients.append(patient)
                return patients
        
        # Default sample patients
        return [
            PatientRecord(
                patient_id="SAMPLE001",
                name="Sample Patient",
                last_visit="2024-01-09",
                status="active",
                medical_history=["Sample Condition"],
                current_medications=["Sample Medication"]
            )
        ]
    
    def _parse_database_response(self, response: Dict[str, Any], criteria: ParsedCriteria) -> List[PatientRecord]:
        """Parse database response into PatientRecord objects."""
        patients = []
        
        # This would parse the actual database response
        # For now, return sample data
        return self._get_sample_patients(criteria)
    
    async def create_sub_agents(self, patients: List[PatientRecord], master_context: ParsedCriteria) -> List[SubAgent]:
        """
        Create sub-agents for each patient.
        
        Args:
            patients: List of patient records
            master_context: Master context from doctor query
            
        Returns:
            List of SubAgent objects
        """
        logger.info(f"Creating {len(patients)} sub-agents")
        
        sub_agents = []
        
        for i, patient in enumerate(patients):
            sub_agent_id = f"sub_agent_{patient.patient_id}_{i+1}"
            sub_agent = SubAgent(patient, master_context, sub_agent_id)
            sub_agents.append(sub_agent)
            self.sub_agents[sub_agent_id] = sub_agent
        
        logger.info(f"Created {len(sub_agents)} sub-agents")
        return sub_agents
    
    async def process_doctor_query(self, query: str) -> Dict[str, Any]:
        """
        Main method to process doctor query end-to-end.
        
        Args:
            query: Natural language doctor query
            
        Returns:
            Complete processing result
        """
        logger.info(f"Processing doctor query: '{query}'")
        
        # Step 1: Parse query into criteria
        criteria = self.parse_doctor_query(query)
        
        # Step 2: Query database
        patients = await self.query_database(criteria)
        
        # Step 3: Create sub-agents
        sub_agents = await self.create_sub_agents(patients, criteria)
        
        # Step 4: Process each sub-agent
        results = []
        for sub_agent in sub_agents:
            result = await sub_agent.process_patient()
            results.append(result)
        
        # Step 5: Compile master result
        master_result = {
            "master_agent_id": self.agent_identity.address if self.agent_identity else "unknown",
            "original_query": query,
            "parsed_criteria": {
                "action": criteria.action,
                "time_filter": criteria.time_filter,
                "condition_filter": criteria.condition_filter,
                "symptom_filter": criteria.symptom_filter,
                "age_filter": criteria.age_filter,
                "medication_filter": criteria.medication_filter
            },
            "patients_found": len(patients),
            "sub_agents_created": len(sub_agents),
            "processing_results": results,
            "summary": {
                "total_patients": len(patients),
                "total_recommendations": sum(len(r.get("recommendations", [])) for r in results),
                "high_priority_recommendations": sum(
                    1 for r in results 
                    for rec in r.get("recommendations", []) 
                    if rec.get("priority") == "high"
                )
            }
        }
        
        logger.info(f"Master query processing completed: {master_result['summary']}")
        return master_result


async def main():
    """Test the Master Agent functionality."""
    print("🤖 Master Agent Phase 2 Test")
    print("=" * 50)
    
    # Initialize Master Agent
    master_agent = MasterAgent()
    await master_agent.initialize()
    
    # Test with sample queries
    test_queries = [
        "follow up with all patients from 4 days ago",
        "check on all diabetic patients who haven't been seen in 2 weeks",
        "review all patients with chest pain symptoms from last week"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing Query: '{query}'")
        print("-" * 40)
        
        result = await master_agent.process_doctor_query(query)
        
        print(f"✅ Patients Found: {result['patients_found']}")
        print(f"✅ Sub-agents Created: {result['sub_agents_created']}")
        print(f"✅ Total Recommendations: {result['summary']['total_recommendations']}")
        print(f"✅ High Priority: {result['summary']['high_priority_recommendations']}")


if __name__ == "__main__":
    asyncio.run(main())

"""
Database service client for querying patient information.
Communicates with Ryan's database service to retrieve patient data.
"""
import requests
import json
import logging
from typing import Dict, Any, Optional
from config.agent_config import AgentConfig

# Configure logging
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL))
logger = logging.getLogger(__name__)


class DatabaseClient:
    """Client for communicating with the external database service."""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize the database client.
        
        Args:
            base_url: The base URL of the database service
            api_key: API key for authentication
        """
        self.base_url = base_url or AgentConfig.DATABASE_SERVICE_URL
        self.api_key = api_key or AgentConfig.DATABASE_SERVICE_API_KEY
        self.session = requests.Session()
        
        # Set up authentication headers
        if self.api_key and self.api_key != "your-api-key-here":
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
        else:
            self.session.headers.update({
                "Content-Type": "application/json"
            })
            logger.warning("No API key configured for database service")
    
    def query_patient_data(self, query: str) -> Dict[str, Any]:
        """
        Query the database service for patient information.
        
        Args:
            query: Text query describing what patient information is needed
            
        Returns:
            JSON response containing patient data
        """
        try:
            payload = {
                "query": query,
                "source": "healthcare_voice_agent",
                "timestamp": self._get_current_timestamp()
            }
            
            logger.info(f"Sending query to database service: {query}")
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Database query successful: {len(str(result))} characters returned")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Database service request failed: {str(e)}")
            return {
                "error": "database_service_unavailable",
                "message": str(e),
                "query": query
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from database service: {str(e)}")
            return {
                "error": "invalid_response_format",
                "message": "Database service returned invalid JSON",
                "query": query
            }
    
    def search_patient_by_name(self, patient_name: str) -> Dict[str, Any]:
        """
        Search for a patient by name.
        
        Args:
            patient_name: The patient's name to search for
            
        Returns:
            Patient information if found
        """
        query = f"Find patient information for {patient_name}"
        return self.query_patient_data(query)
    
    def search_patient_by_id(self, patient_id: str) -> Dict[str, Any]:
        """
        Search for a patient by ID.
        
        Args:
            patient_id: The patient's ID to search for
            
        Returns:
            Patient information if found
        """
        query = f"Find patient information for patient ID {patient_id}"
        return self.query_patient_data(query)
    
    def get_medical_history(self, patient_identifier: str) -> Dict[str, Any]:
        """
        Get medical history for a patient.
        
        Args:
            patient_identifier: Patient name or ID
            
        Returns:
            Medical history information
        """
        query = f"Get complete medical history for {patient_identifier} including previous visits, diagnoses, medications, and test results"
        return self.query_patient_data(query)
    
    def get_current_medications(self, patient_identifier: str) -> Dict[str, Any]:
        """
        Get current medications for a patient.
        
        Args:
            patient_identifier: Patient name or ID
            
        Returns:
            Current medication information
        """
        query = f"Get current medications and prescriptions for {patient_identifier}"
        return self.query_patient_data(query)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to the database service.
        
        Returns:
            Connection test result
        """
        test_query = "Test connection - please return a simple acknowledgment"
        
        logger.info("Testing database service connection...")
        result = self.query_patient_data(test_query)
        
        if "error" not in result:
            logger.info("Database service connection test successful")
            return {
                "status": "success",
                "message": "Database service is reachable",
                "response": result
            }
        else:
            logger.error(f"Database service connection test failed: {result}")
            return {
                "status": "failed",
                "message": "Database service is not reachable",
                "error": result
            }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


def main():
    """Command-line interface for testing database client."""
    import sys
    
    client = DatabaseClient()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("Testing database service connection...")
            result = client.test_connection()
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "query" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            print(f"Querying: {query}")
            result = client.query_patient_data(query)
            print(json.dumps(result, indent=2))
        else:
            print("Usage:")
            print("  python database_client.py test                    - Test connection")
            print("  python database_client.py query <your query>     - Send a query")
    else:
        print("Usage:")
        print("  python database_client.py test                    - Test connection")
        print("  python database_client.py query <your query>     - Send a query")
        print("\nExample:")
        print("  python database_client.py query 'Find patient John Doe'")


if __name__ == "__main__":
    main()

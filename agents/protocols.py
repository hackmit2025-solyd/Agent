"""
Message protocols for uagents-based healthcare system.
Defines the communication patterns between different agents.
"""
from uagents import Model
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class FollowUpStatus(str, Enum):
    """Status of follow-up communication."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    FLAGGED_FOR_REVIEW = "flagged_for_review"


class DecisionOutcome(str, Enum):
    """Decision outcomes for follow-up completion."""
    CLOSE_LOOP = "close_loop"
    FLAG_FOR_DOCTOR_REVIEW = "flag_for_doctor_review"
    RETRY_COMMUNICATION = "retry_communication"
    ESCALATE_URGENT = "escalate_urgent"


class PatientRecord(Model):
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
    medication_changes: Optional[List[Dict[str, Any]]] = None


class ParsedCriteria(Model):
    """Structured representation of parsed doctor query criteria."""
    action: str
    time_filter: Optional[str] = None
    condition_filter: Optional[str] = None
    symptom_filter: Optional[str] = None
    age_filter: Optional[str] = None
    medication_filter: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    patient_criteria: Optional[Dict[str, Any]] = None


class DoctorQuery(Model):
    """Doctor query message."""
    query: str
    timestamp: datetime
    doctor_id: Optional[str] = None


class QueryParsed(Model):
    """Response after parsing doctor query."""
    criteria: ParsedCriteria
    original_query: str
    timestamp: datetime


class DatabaseQuery(Model):
    """Database query message."""
    criteria: ParsedCriteria
    original_query: str
    timestamp: datetime


class DatabaseResponse(Model):
    """Database response message."""
    patients: List[PatientRecord]
    query_criteria: ParsedCriteria
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class CreateSubAgent(Model):
    """Message to create a sub-agent for a patient."""
    patient: PatientRecord
    master_context: ParsedCriteria
    sub_agent_id: str
    timestamp: datetime


class SubAgentCreated(Model):
    """Response when sub-agent is created."""
    sub_agent_id: str
    patient_id: str
    status: str
    timestamp: datetime


class ProcessPatient(Model):
    """Message to process a patient."""
    patient: PatientRecord
    master_context: ParsedCriteria
    sub_agent_id: str
    timestamp: datetime


class PatientProcessed(Model):
    """Response when patient processing is complete."""
    sub_agent_id: str
    patient_id: str
    processing_steps: List[str]
    recommendations: List[Dict[str, Any]]
    status: str
    timestamp: datetime


class CommunicationResult(Model):
    """Result of a communication session."""
    session_id: str
    patient_id: str
    status: FollowUpStatus
    outcome: DecisionOutcome
    data_obtained: Dict[str, Any]
    missing_data: List[str]
    confidence_score: float
    timestamp: datetime
    notes: str


class InitiateCommunication(Model):
    """Message to initiate communication with a patient."""
    patient: PatientRecord
    master_context: ParsedCriteria
    sub_agent_id: str
    communication_goals: List[str]
    timestamp: datetime


class CommunicationCompleted(Model):
    """Response when communication is completed."""
    result: CommunicationResult
    sub_agent_id: str
    timestamp: datetime


class VoiceData(Model):
    """Voice data from webhook."""
    session_id: str
    transcript: str
    audio_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime


class VoiceProcessed(Model):
    """Response after processing voice data."""
    session_id: str
    patient_data: Optional[PatientRecord] = None
    recommendations: List[Dict[str, Any]]
    processing_steps: List[str]
    timestamp: datetime


class MasterQueryResult(Model):
    """Complete result from master agent processing."""
    master_agent_id: str
    original_query: str
    parsed_criteria: Dict[str, Any]
    patients_found: int
    sub_agents_created: int
    processing_results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    timestamp: datetime


class AgentStatus(Model):
    """Agent status message."""
    agent_id: str
    agent_type: str
    status: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class SystemStatus(Model):
    """Overall system status."""
    total_sub_agents: int
    completed: int
    flagged_for_review: int
    failed: int
    success_rate: float
    timestamp: datetime
